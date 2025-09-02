import json
import os
import warnings
from datetime import datetime
from pathlib import Path as path

import torch
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field, field_validator
from transformers import AutoTokenizer, pipeline

from extract_model_response import (
    MODEL_NAME,
    correct_arabic_text,
)
from logger import get_logger

load_dotenv()
# Configure PyTorch to avoid warnings and optimize for RTX 2060
os.environ["TORCH_NCCL_BLOCKING_WAIT"] = "1"
os.environ["TORCH_CUDNN_V8_API_ENABLED"] = "1"
# Disable inductor optimizations that cause warnings on RTX 2060
os.environ["TORCH_COMPILE_DEBUG"] = "0"
os.environ["TORCHINDUCTOR_DISABLE_COMPRESSION"] = "1"
# Additional settings to suppress specific warnings
os.environ["TORCH_LOGS"] = "+dynamo"
os.environ["TORCHINDUCTOR_MAX_AUTOTUNE"] = "0"

# Suppress specific PyTorch warnings

warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*does not support bfloat16.*")
warnings.filterwarnings("ignore", message=".*Not enough SMs to use max_autotune_gemm.*")

# Set CUDA memory management for better stability
if torch.cuda.is_available():
    torch.backends.cuda.enable_flash_sdp(False)  # Disable for RTX 2060 compatibility
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    # Avoid bfloat16 compilation warnings
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True


logger = get_logger(__name__)

app = FastAPI(
    title="Arabic Text Correction API",
    description="API for correcting Arabic text using AI model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


tokenizer = None
pipe = None


class TextCorrectionRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Arabic text to be corrected",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class TextCorrectionResponse(BaseModel):
    original_text: str
    corrected_text: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    model_loaded: bool


class ErrorResponse(BaseModel):
    error: str
    message: str


with path.open("outputs.json", "r") as f:
    loaded_data = json.load(f)

    OUTPUTS = loaded_data if isinstance(loaded_data, list) else []


def update_json_file() -> None:
    with path.open("outputs.json", "w", encoding="utf-8") as f:
        json.dump(OUTPUTS, f, ensure_ascii=False, indent=2)


def initialize_model() -> None:
    global pipe, tokenizer

    try:
        logger.info(f"Loading model {MODEL_NAME}..")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        tokenizer.chat_template = """{% for message in messages %}{{'<start_of_turn>' + message['role'] + '\n' + message['content'] + '<end_of_turn>\n'}}{% endfor %}{% if add_generation_prompt %}{{'<start_of_turn>model\n'}}{% endif %}"""

        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

        logger.info(f"Using device: {device}")

        # Initialize CUDA context properly if using GPU
        if device == "cuda":
            torch.cuda.init()
            # Create a small tensor to ensure CUDA context is fully initialized
            _ = torch.zeros(1, device=device)
            torch.cuda.empty_cache()

        # Configure pipeline with proper settings for numerical stability
        pipeline_kwargs = {
            "task": "text-generation",
            "model": MODEL_NAME,
            "tokenizer": tokenizer,
        }

        # Add GPU-specific optimizations with stable settings
        if device == "cuda":
            pipeline_kwargs.update(
                {
                    "torch_dtype": torch.float16,  # Use float16 for stability on RTX 2060
                    "device_map": "auto",
                    "trust_remote_code": True,
                    "model_kwargs": {
                        "attn_implementation": "eager",  # Use eager attention to avoid flash attention issues
                    },
                },
            )
        else:
            pipeline_kwargs["device"] = device

        # Ensure proper tokenizer configuration
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        pipe = pipeline(**pipeline_kwargs)

        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e!s}")
        raise e


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and model is loaded",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=pipe is not None,
    )


@app.get("/gec/all")
async def get_all_text() -> list[dict]:
    return OUTPUTS


@app.post(
    "/gec/correct",
    response_model=TextCorrectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Correct Arabic Text",
    description="Correct an Arabic Text using AI",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid input"},
        503: {
            "model": ErrorResponse,
            "description": "Server Unavailable - Model not loaded",
        },
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def correct_text(request: TextCorrectionRequest) -> TextCorrectionResponse:
    try:
        if not pipe or not tokenizer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Model not loaded",
                    "message": "Server is still initializing",
                },
            )

        input_text = request.text
        logger.info(f"Received request for text: {input_text[:50]}...")

        corrected_text = correct_arabic_text(input_text)

        response = TextCorrectionResponse(
            original_text=input_text,
            corrected_text=corrected_text,
            timestamp=datetime.now().isoformat(),
        )
        logger.info(
            f"Correction completed successfully: '{input_text}' → '{corrected_text}'",
        )

        output = {
            "id": OUTPUTS[-1]["id"] + 1,
            "input text": input_text,
            "corrected text": corrected_text,
        }
        OUTPUTS.append(output)
        update_json_file()

        return response

    except Exception as e:
        logger.error(f"Error in /correct endpoint: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        )


@app.delete(
    "/gec/delete/{text_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete text",
    description="Delete text by id number",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid ID number"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def delete_book(text_id: int = Path(gt=0)) -> None:
    if text_id <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid ID number",
                "message": "ID must be greater than 0",
            },
        )

    for output in OUTPUTS:
        if output["id"] == text_id:
            OUTPUTS.remove(output)

            update_json_file()


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("FastAPI server starting up...")
    try:
        initialize_model()
        logger.info("Model initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("FastAPI sever shutting down...")

    global pipe, tokenizer
    pipe = None
    tokenizer = None
