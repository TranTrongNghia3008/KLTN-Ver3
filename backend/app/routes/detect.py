from fastapi import APIRouter, UploadFile, File
from typing import List
from app.services.genconvit_service import predict_single_video

router = APIRouter()

@router.post("/detect/")
async def detect_deepfake(videos: List[UploadFile] = File(...)):
    results = {}
    for video in videos:
        try:
            result = predict_single_video(video)
            results[video.filename] = result
        except Exception as e:
            results[video.filename] = {"error": str(e)}
    return results
