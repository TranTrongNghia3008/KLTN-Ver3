from app.config import *
from app.models.deepfake import *
from app.services.extract_statements import *
from app.services.deepfake_service import *

router = APIRouter()

@router.post("/deepfake/")
async def detect_deepfake_api(video: UploadFile = File(...)):
    """
    API để kiểm tra deepfake từ video.
    Phân tích lời thoại, phát hiện deepfake, enrich bài báo và fact-check.
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        shutil.copyfileobj(video.file, temp_video)
        video_path = temp_video.name

    try:
        print("🎥 Extracting statements from video...")
        final_statements_json = extract_statements_from_video(video_path)
        print(final_statements_json)

        print("🔍 Detecting deepfake...")
        final_statements_json = detect_deepfake(final_statements_json, video_path)

        print("✅ Finished detecting deepfake.")
        print(final_statements_json)

        for statement in final_statements_json:
            if statement["deepfake_label"] == "FAKE":
                print(f"⚠️ Statement '{statement['text']}' is marked as deepfake. Skipping fact-check.")
                return {
                    "deepfake_label": "FAKE",
                    "label": False,
                    "statements": final_statements_json
                }

        print("📰 Enriching statements with articles...")
        enriched_statements = enrich_statements_with_articles(final_statements_json)
        print("✅ Finished enriching statements with articles.")

        print("🧪 Running fact-checks on statements...")
        fact_checked_results = run_fact_checks_parallel(enriched_statements)

        for result in fact_checked_results:
            if result["label"] == "False":
                print(f"❌ Statement '{result['text']}' is refuted: {result['explanation']}")
                return {
                    "deepfake_label": "REAL",
                    "label": False,
                    "statements": fact_checked_results
                }

        print("✅ All statements are supported or unverified.")
        return {
            "deepfake_label": "REAL",
            "label": True,
            "statements": fact_checked_results
        }

    finally:
        temp_video.close()