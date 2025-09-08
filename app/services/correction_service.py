import os
from typing import Optional

import torch
from transformers import AutoTokenizer, pipeline

from app.config import get_settings
from app.models.schema import CorrectionCreate
from logger import get_logger

settings = get_settings()

logger = get_logger(__name__)

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
import warnings

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


class CorrectionService:
    def __init__(self) -> None:
        self.tokenizer: Optional[AutoTokenizer] = None
        self.pipe = None
        self.model_loaded = False

    def extract_model_response(self, generated_text: str) -> str:
        """Extract just the model's response from the full generated text."""
        # Find the position after "model" marker
        model_marker = "\nmodel\n"
        if model_marker in generated_text:
            response_start = generated_text.find(model_marker) + len(model_marker)
            response = generated_text[response_start:].strip()
            # Remove any end-of-turn markers from the response
            response = response.replace("<end_of_turn>", "").strip()
            return response

        # Alternative format (in case formatting changes)
        alt_marker = "model\n"
        if alt_marker in generated_text:
            response_start = generated_text.find(alt_marker) + len(alt_marker)
            response = generated_text[response_start:].strip()
            response = response.replace("<end_of_turn>", "").strip()
            return response

        # If no markers found, try to extract after the input text
        # This is a fallback in case the model generates differently than expected
        return generated_text.strip()

    def initialize_model(self) -> None:
        try:
            logger.info(f"Loading model {settings.model_name}..")

            self.tokenizer = AutoTokenizer.from_pretrained(settings.model_name)

            self.tokenizer.chat_template = """{% for message in messages %}{{'<start_of_turn>' + message['role'] + '\n' + message['content'] + '<end_of_turn>\n'}}{% endfor %}{% if add_generation_prompt %}{{'<start_of_turn>model\n'}}{% endif %}"""

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
                "model": settings.model_name,
                "tokenizer": self.tokenizer,
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
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.pipe = pipeline(**pipeline_kwargs)
            self.model_loaded = True
            logger.info("Model loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading model: {e!s}")
            raise e

    def correct_arabic_text(self, text: str) -> str:
        """Correct Arabic text using the fine-tuned model with CPU fallback for stability."""
        if not self.model_loaded or not self.pipe or not self.tokenizer:
            raise ValueError("Model not loaded")
        try:
            messages = [{"role": "user", "content": text}]
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            # Try GPU first (for speed), but with very conservative settings
            try:
                outputs = self.pipe(
                    prompt,
                    max_new_tokens=64,  # Conservative limit
                    do_sample=False,  # Only greedy decoding
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    return_full_text=True,
                )
                full_text = outputs[0]["generated_text"]
                result = self.extract_model_response(full_text)

                # If GPU generated a result and it's different from input, use it
                if result.strip() and result.strip() != text.strip():
                    return result.strip()

            except RuntimeError as gpu_error:
                logger.error(f"GPU generation failed: {gpu_error}")

            # Fallback to CPU (more reliable)
            logger.info("Using CPU fallback for text correction...")
            cpu_pipe = pipeline(
                "text-generation",
                model=settings.model_name,
                tokenizer=self.tokenizer,
                device="cpu",
                torch_dtype=torch.float32,
                trust_remote_code=True,
            )

            outputs = cpu_pipe(
                prompt,
                max_new_tokens=100,
                do_sample=False,
                return_full_text=True,
            )

            full_text = outputs[0]["generated_text"]
            result = self.extract_model_response(full_text)

            # Return the corrected text or original if no correction made
            return result.strip() if result.strip() else text

        except RuntimeError as e:
            # Final fallback: return input text if all methods fail
            logger.error(f"Text correction completely failed: {e}")
            return text


correction_service = CorrectionService()
