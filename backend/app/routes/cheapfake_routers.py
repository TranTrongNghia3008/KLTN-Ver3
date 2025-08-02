from fastapi import APIRouter, UploadFile, File, Form
from app.services.cheapfake_service import cheapfake_label_service

router = APIRouter()

@router.post("/cheapfake/")
async def detect_cheapfake(
    caption: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Detect cheapfake based on image and caption.
    The system will crawl related articles from the web,
    convert them to PDF, and analyze the content using Gemini.
    """
    result = await cheapfake_label_service(image_file=image, caption=caption)
    return result  # {"label": ..., "url_articles": [...]}
