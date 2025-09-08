from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.models.schema import CorrectionCreate
from app.services.correction_service import correction_service
from app.services.database_service import database_service

from logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Arabic Text Correction"}
    )


@router.post("/correct", response_class=HTMLResponse)
async def correct_text_web(request: Request, text: str = Form(...)) -> HTMLResponse:
    try:
        if not correction_service.model_loaded:
            return templates.TemplateResponse(
                "index.html", {"request": request, "error": "Model not loaded"}
            )

        corrected_text = correction_service.correct_arabic_text(text)

        correction_create = CorrectionCreate(
            original_text=text, corrected_text=corrected_text
        )

        correction_in_db = database_service.create_correction(correction_create)

        return templates.TemplateResponse(
            "correction.html",
            {
                "request": request,
                "original_text": text,
                "corrected_text": corrected_text,
                "correction_id": correction_in_db.id,
                "title": "Correction Result",
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"An error occurred while correcting text: {e!s}",
            },
        )


@router.get("/history", response_class=HTMLResponse)
async def correction_history(request: Request):
    corrections = database_service.get_all_corrections()
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "corrections": corrections, "title": "Correction History"},
    )


@router.post("/delete/{correction_id}")
async def delete_correction_web(correction_id: int):

    try:
        success = database_service.delete_correction(correction_id)
        if not success:
            # Handle error case if needed
            pass
    except Exception as e:
        # Handle error case if needed
        pass

    return RedirectResponse(url="/history", status_code=303)
