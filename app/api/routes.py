from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.models.schema import (
    TextCorrectionRequest,
    TextCorrectionResponse,
    HealthResponse,
    ErrorResponse,
    CorrectionCreate,
    CorrectionInDB,
)
from app.services.correction_service import correction_service
from app.services.database_service import database_service

from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/gec")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and model is loaded",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=correction_service.model_loaded is not None,
    )


@router.get(
    "/all",
    response_model=list[CorrectionInDB],
    summary="Get all corrections",
    description="Get all corrections from the database",
)
async def get_all_text() -> list[CorrectionInDB]:
    return database_service.get_all_corrections()


@router.post(
    "/correct",
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
        if not correction_service.pipe or not correction_service.tokenizer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Model not loaded",
                    "message": "Server is still initializing",
                },
            )

        input_text = request.text
        logger.info(f"Received request for text: {input_text[:50]}...")

        corrected_text = correction_service.correct_arabic_text(input_text)

        correction_create = CorrectionCreate(
            original_text=input_text, corrected_text=corrected_text
        )

        correction_in_db = database_service.create_correction(correction_create)

        response = TextCorrectionResponse(
            id=correction_in_db.id,
            original_text=input_text,
            corrected_text=corrected_text,
            timestamp=correction_in_db.created_at.isoformat(),
        )
        logger.info(
            f"Correction completed successfully: '{input_text}' → '{corrected_text}'",
        )

        return response

    except Exception as e:
        logger.error(f"Error in /correct endpoint: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        )


@router.delete(
    "/delete/{text_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete correction",
    description="Delete correction by id number",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid ID number"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def delete_correction(text_id: int = Path(gt=0)) -> None:
    try:
        success = database_service.delete_correction(id=text_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Correction not found",
                    "message": f"Correction with id {text_id} not found",
                },
            )
    except Exception as e:
        logger.error(f"Error in deleting correction: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        )
