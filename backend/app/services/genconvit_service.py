# app/services/genconvit_service.py

import os
import uuid
import shutil
from app.genconvit.model.pred_func import is_video, df_face, pred_vid, set_result, store_result, real_or_fake
from app.services.genconvit_loader import model  # ✅ dùng model đã load

TEMP_DIR = "temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)

def predict_single_video(video_file, num_frames: int = 15, net: str = "genconvit", fp16: bool = False):
    unique_filename = f"{uuid.uuid4().hex}_{video_file.filename}"
    video_path = os.path.join(TEMP_DIR, unique_filename)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)

    result = set_result()

    if not is_video(video_path):
        os.remove(video_path)
        raise ValueError("Invalid video format")

    df = df_face(video_path, num_frames, net)
    if fp16:
        df.half()

    y, y_val = (
        pred_vid(df, model)
        if len(df) >= 1
        else (0, 0.5)
    )

    result = store_result(
        result, os.path.basename(video_path), y, y_val, "uncategorized", "unknown", None
    )
    os.remove(video_path)
    return result["video"]
