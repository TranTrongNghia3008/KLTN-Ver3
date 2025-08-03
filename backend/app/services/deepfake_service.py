from app.config import *
from app.models.deepfake import *
from app.services.cheapfake_service import *
from app.services.genconvit_service import predict_single_video

def cut_video_into_clips(final_statements_json, video_path: str):
    """
    Cuts the video into clips based on the provided statements.
    Ensures clip end time does not exceed video duration.
    """
    clip_dir = os.path.join("statement_clips", os.path.splitext(os.path.basename(video_path))[0])
    
    # Tạo thư mục hoặc dọn sạch nếu đã tồn tại
    os.makedirs(clip_dir, exist_ok=True)
    for f in os.listdir(clip_dir):
        file_path = os.path.join(clip_dir, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Load video để lấy thời lượng thực tế
    full_video = VideoFileClip(video_path)
    video_duration = full_video.duration
    
    # Kiểm tra nếu final_statements_json chỉ có một phần tử thì lấy toàn bộ video lưu vào clip_dir
    if len(final_statements_json) == 1:
        clip_path = os.path.join(clip_dir, "clip_1.mp4")
        print(f"✂️ Cutting full video to {clip_path}")
        full_video.write_videofile(clip_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        full_video.close()
        return clip_dir

    for i, s in enumerate(final_statements_json):
        start, end = float(s['start']), float(s['end'])

        # Bỏ qua nếu start vượt quá thời lượng video
        if start >= video_duration:
            print(f"⚠️ Skip clip_{i+1}: start time {start:.2f}s >= video duration {video_duration:.2f}s")
            continue

        # Giới hạn end không vượt quá video
        end = min(end, video_duration)

        clip_path = os.path.join(clip_dir, f"clip_{i+1}.mp4")
        print(f"✂️ Cutting {clip_path} from {start:.2f}s to {end:.2f}s")

        clip = full_video.subclip(start, end)
        clip.write_videofile(clip_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

    full_video.close()
    print(f"✅ Finished cutting video into clips. Saved to {clip_dir}")
    return clip_dir

# def call_api_detect_deepfake(clip_dir: str):
#     """
#     Detects deepfake in the video clips.
#     """
#     # Tạo danh sách file để gửi
#     video_files = []
#     for filename in os.listdir(clip_dir):
#         if filename.endswith(".mp4"):
#             file_path = os.path.join(clip_dir, filename)
#             video_files.append(("videos", (filename, open(file_path, "rb"), "video/mp4")))
    
#     # Gửi yêu cầu POST
#     print("📤 Sending batch videos to deepfake API...")
#     response = requests.post(API_URL, files=video_files)

#     # Kết quả
#     if response.status_code == 200:
#         result = response.json()
#         print("✅ Detection results:")
#         for fname, r in result.items():
#             print(f"{fname}: {r}")
#         return result
#     else:
#         print(f"❌ Error {response.status_code}: {response.text}")
        
#     return None

def call_internal_detect_deepfake(clip_dir: str):
    """
    Detects deepfake in the video clips by calling predict_single_video directly.
    """
    results = {}

    for filename in os.listdir(clip_dir):
        if filename.endswith(".mp4"):
            file_path = os.path.join(clip_dir, filename)

            # Đọc file vào memory buffer (giống UploadFile)
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                file_stream = BytesIO(file_bytes)
                upload_file = UploadFile(filename=filename, file=file_stream)

                try:
                    result = predict_single_video(upload_file)
                    results[filename] = result
                except Exception as e:
                    results[filename] = {"error": str(e)}
    
    # In kết quả
    print("✅ Detection results:")
    for fname, r in results.items():
        print(f"{fname}: {r}")
    
    return results

def detect_deepfake(final_statements_json, video_path: str):
    """
    Main function to detect deepfake in the video.
    """
    print("🎥 Cutting video into clips...")
    
    clip_dir = cut_video_into_clips(final_statements_json, video_path)

    print("🔍 Detecting deepfake in clips...")
    results = call_internal_detect_deepfake(clip_dir)

    for idx, statement in enumerate(final_statements_json):
        clip_name = f"clip_{idx+1}.mp4"
        result = results.get(clip_name, {})
        
        # Lấy nhãn deepfake nếu có
        label = result["pred_label"][0]
        pred_score = result["pred"][0]
        
        # Gắn vào statement
        statement["deepfake_label"] = label
        statement["deepfake_score"] = pred_score
    
    print("✅ Finished detecting deepfake.")
    return final_statements_json

def process_single_statement(statement):
    try:
        query = statement["text"].strip('"')
        crawl_json = []

        # Crawl theo statement
        crawl_articles(query, crawl_json=crawl_json)

        # Crawl thêm theo context
        context = statement["context"]
        crawl_articles(query=context, crawl_json=crawl_json)

        # Loại bỏ các kết quả None
        crawl_json = [item for item in crawl_json if item is not None]

        # Nối lại toàn bộ nội dung: thêm title và content mỗi bài
        article_texts = "\n\n".join(
            f"### {item.get('title', 'No Title')}\n{item.get('contents', '').strip()}"
            for item in crawl_json
            if item.get("contents")
        )

        # Trả lại enriched statement
        enriched_statement = statement.copy()
        enriched_statement["article_texts"] = article_texts.strip()

        return enriched_statement
    except Exception as e:
        print(f"❌ Error processing statement {statement['text']}: {e}")
        enriched_statement = statement.copy()
        enriched_statement["article_texts"] = ""
        return enriched_statement


def enrich_statements_with_articles(final_statements_json):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(process_single_statement, final_statements_json))

def fact_check(statement):
    prompt = f"""
You are a professional fact-checking assistant. Your task is to determine whether a specific statement made by a public figure is **factually accurate and verifiably attributed to them**, using only the provided reference documents.

### Instructions:

Follow this strict two-step verification process:

1. **Check if the speaker truly made the statement**:
   - Search the reference documents to confirm whether the speaker is explicitly or clearly quoted as saying this or something semantically equivalent.
   - If you find strong evidence that the speaker made the statement, continue to step 2.
   - If **no such quote or attribution** exists in the documents, set:
     - **label = false**
     - and stop. Do not proceed to step 2.

2. **Evaluate the factual accuracy** of the statement using only the reference materials:
   - If it is directly supported by the documents, set `label = true`.
   - If it is **partially true, misleading, or contradicted**, or if the documents **do not support** it clearly, set `label = false`.

**Important Guidelines:**
- Use only the reference documents. Do not assume or infer information.
- If unsure, default to `label = false`.
- Be skeptical: only statements that are clearly made and clearly true should be labeled `true`.

### Context:
{statement['context']}

### Speaker:
{statement['speaker']}

### Statement:
"{statement['text']}"

### Documents:
{statement['article_texts']}

### Output format:
label: true or false
"""
    try:
        response = client.responses.parse(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "You are a medical fact-checking expert."},
                {"role": "user", "content": prompt},
            ],
            text_format=FactCheck
        )
        result = response.output_parsed

    except Exception as e:
        print(f"Problem with API: {e}")
        result = "Unverified"

    return result

def fact_check_single_statement(statement):
    print(statement)
    text = statement["text"]

    print(f"🧐 Fact-checking: {text[:80]}...")

    result = fact_check(statement)

    if result == "Unverified":
        statement["label"] = None
        print("❌ Unable to verify statement.")
    else:
        statement["label"] = result.label

    return statement


def run_fact_checks_parallel(enriched_statements, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(fact_check_single_statement, enriched_statements))
    return results
