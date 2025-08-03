from app.config import *
from app.models.deepfake import *

# --- STEP 1: Extract audio from video ---
def extract_audio(video_path: str, audio_dir: str = "audios") -> str:
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    video = VideoFileClip(video_path)
    audio_path = os.path.basename(video_path).replace('.mp4', '.wav')
    audio_path = os.path.join(audio_dir, audio_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

# --- STEP 2: Diarize audio (identify speakers) ---
def diarize_audio(audio_path: str) -> List[Dict]:
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HUGGINGFACE_TOKEN)
    diarization = pipeline(audio_path)
    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return speakers

# --- STEP 3: Transcribe audio ---
def transcribe_audio(audio_path: str) -> List[Dict]:
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["segments"]

# --- STEP 4: Assign speakers to transcript segments ---
def assign_speakers(segments: List[Dict], speakers: List[Dict]) -> List[Dict]:
    output = []
    for seg in segments:
        speaker_label = "unknown"
        for sp in speakers:
            if sp["start"] <= seg["start"] <= sp["end"]:
                speaker_label = sp["speaker"]
                break
        output.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": speaker_label,
            "text": seg["text"].strip()
        })
    return output

# --- STEP 5: Identify speaker names via text cues (OpenAI) ---
def identify_speaker_names_via_text(transcript: List[Dict]) -> Dict:
    transcript_text = "\n".join(
        [f"{seg['speaker']}: {seg['text']}" for seg in transcript]
    )
    prompt = f"""
    Below is the full transcript of a video, each line contains the speaker (SPEAKER_XX) and the dialogue.

    Analyze to determine if there is any part where the speaker introduces himself or is introduced by someone else.

    Returns a JSON result with the following structure:
    {{
      {{
        id: "SPEAKER_00",
        name: "Name if available",
      }},
      ...
    }}

    If not identified, returns the name field as "Unnamed".

    Transcript:
    {transcript_text}
    """

    response = client.responses.parse(
        model="gpt-4.1-nano",
        input=[
            {"role": "system", "content": "Extract the event information."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
        text_format=ListSpeakers,
    )

    return response.output_parsed

def extract_frames_for_unknown_speakers(
    video_path: str,
    speaker_segments: List[Dict],
    speaker_name_map,  # kiểu: ListSpeakers (đã chứa list[Speaker(id, name)])
    output_dir: str = "frames",
    max_frames_per_speaker: int = 5
):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Tạo dict lookup tên từ speaker_name_map
    speaker_id_to_name = {s.id: s.name for s in speaker_name_map.listSpeakers}
    speaker_frames = {}

    for seg in speaker_segments:
        spk = seg['speaker']
        name = speaker_id_to_name.get(spk, "")
        if name.startswith("Unnamed"):
            # Nếu đã đủ 5 frame thì bỏ qua
            if spk in speaker_frames and len(speaker_frames[spk]) >= max_frames_per_speaker:
                continue

            mid_time = (seg['start'] + seg['end']) / 2
            frame_num = int(mid_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if ret:
                frame_path = os.path.join(output_dir, f"{spk}_{int(seg['start'])}.jpg")
                cv2.imwrite(frame_path, frame)
                if spk not in speaker_frames:
                    speaker_frames[spk] = []
                speaker_frames[spk].append({
                    "time": mid_time,
                    "frame_path": frame_path,
                    "text": seg["text"]
                })

    cap.release()
    return speaker_frames

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def identify_unknown_speakers_with_gpt(speaker_frames: dict) -> dict:
    """
    speaker_frames: {
        "SPEAKER_01": [
            {"time": ..., "frame_path": ..., "text": ...},
            ...
        ],
        ...
    }
    """
    speaker_id_to_name = {}

    for speaker_id, frames in speaker_frames.items():
        print(f"\n🧠 Đang xử lý {speaker_id}...")

        # Chuẩn bị prompt chính
        texts = [f'“{f["text"]}”' for f in frames if f.get("text")]
        combined_text = "\n".join(texts)  # Dùng tối đa 3 đoạn transcript

        prompt = f"""
            This is a collection of frames extracted from a video showing one speaker. Based on their appearance and the following quotes, can you identify who they are or make an educated guess?

            Quotes:
            {combined_text}

            Returns only the speaker's name (no further explanation needed).

            If you can't tell, reply with "Unnamed".
        """

        # Chuẩn bị ảnh
        content_items = [{"type": "input_text", "text": prompt}]
        for f in frames:
            image_path = f["frame_path"]  # đảm bảo đúng path
            try:
                base64_image = encode_image(image_path)
                content_items.append({
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                })
            except Exception as e:
                print(f"❌ Không thể đọc ảnh {image_path}: {e}")

        # Gửi yêu cầu lên GPT
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": content_items
                    }
                ]
            )
            name = response.output_text
            speaker_id_to_name[speaker_id] = name
            print(f"✅ {speaker_id} → {name}")
        except Exception as e:
            print(f"❌ Error for {speaker_id}: {e}")
            speaker_id_to_name[speaker_id] = "Unnamed"

    return speaker_id_to_name

def generate_named_transcript(transcript, speaker_name_map, new_names):
    # Bước 1: Gộp tên từ speaker_name_map và new_names
    speaker_lookup = {}
    for speaker in speaker_name_map.listSpeakers:
        speaker_id = speaker.id
        name = new_names.get(speaker_id, speaker.name)
        speaker_lookup[speaker_id] = name

    # Bước 2: Gán tên rõ ràng vào transcript
    named_transcript = []
    for seg in transcript:
        spk = seg['speaker']
        if spk == "unknown":
            display_name = "Unknown"
        else:
            name = speaker_lookup.get(spk, spk)
            display_name = name if name != "Unnamed" else spk

        named_transcript.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": display_name,
            "text": seg["text"]
        })

    # Bước 3: Gộp các đoạn liên tiếp cùng speaker
    if not named_transcript:
        return []

    merged_transcript = []
    current = named_transcript[0]

    for seg in named_transcript[1:]:
        if seg["speaker"] == current["speaker"]:
            # Gộp đoạn
            current["end"] = seg["end"]
            current["text"] += " " + seg["text"]
        else:
            merged_transcript.append(current)
            current = seg

    merged_transcript.append(current)  # Thêm đoạn cuối cùng
    return merged_transcript

def split_transcript(transcript, chunk_size=100):
    """Chia transcript thành các đoạn nhỏ để tránh quá dài"""
    return [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]


def find_checkworthy_statements(final_transcript, model="gpt-4.1-mini"):
    parts = split_transcript(final_transcript, chunk_size=300)
    all_statements = []

    for idx, part in enumerate(parts):
        print(f"🔍 Đang xử lý phần {idx+1}/{len(parts)}...")

        # Tạo văn bản nhập
        lines = [f"[{r['start']:.2f}-{r['end']:.2f}] {r['speaker']}: {r['text']}" for r in part]
        input_text = "\n".join(lines)
        print(input_text)

        prompt = """You are a professional fact-checking assistant.
            Your job is to extract **checkworthy statements** from transcripts of political events, such as debates, interviews, speeches, or hearings.
            Return at **least 2** verifiable statements from 2 different speakers, including unknown speaker (unless there is only 1 speaker, then return 1 statement). If the video is short or has only 1 speaker, extract the entire video.
            
            A **checkworthy statement** typically:
            - Contains a factual claim or statistic.
            - Refers to historical events, wars, or political actions.
            - Makes a cause-effect claim (e.g., "if I were president, this would never happen").
            - Assigns blame or credit for an outcome (e.g., war, economy, healthcare).
            - Makes bold or controversial public assertions.

            Very Important:
            - Only extract **entire continuous speaking segments** from a speaker. That is, if a speaker talks for several sentences in one turn (not interrupted by others), you **must return the full segment verbatim**, not just a partial sentence or fragment.
            - If a speaker talks multiple times (non-consecutively), treat each turn independently — only extract when that turn is checkworthy.

            ### Output Format:
            Return a list of structured statements in this format:
            - `start`: float → start time of the speaker’s turn (in seconds)
            - `end`: float → end time of the speaker’s turn (in seconds)
            - `speaker`: str → name of the speaker
            - `text`: str → full verbatim text spoken by the speaker in that turn
            - `reason`: str → short explanation why this is worth fact-checking
            - `context`: str → provide context including:
                + Where the quote was made (e.g., presidential debate, interview, rally) — infer if not explicit
                + When it happened (date or rough period, e.g., “during the 2024 campaign” or “in June 2025”)
                + The topic under discussion (e.g., foreign policy, war in Ukraine, tax policy)
                + Whether the speaker was replying to someone, and what was asked (if known)
            
            Cannot return null or empty list.
          """

        try:
            response = client.responses.parse(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": input_text,
                    },
                ],
                text_format=ListStatement,
            )
            statements = response.output_parsed.listStatment
            all_statements.extend(statements)

        except Exception as e:
            print(f"❌ Lỗi ở phần {idx+1}: {e}")

    return all_statements

def extract_frame_for_statement(video_path: str, statement, output_dir="statement_frames"):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    mid_time = (statement.start + statement.end) / 2
    frame_num = int(mid_time * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()

    if ret:
        filename = f"{statement.speaker}_{int(statement.start*100):06d}.jpg"
        frame_path = os.path.join(output_dir, filename)
        cv2.imwrite(frame_path, frame)
        return frame_path
    else:
        return None
    
def extract_statements_from_video(video_path: str):
    """
    Extracts the transcript from a video file.
    """
    print("🎬 Extracting audio...")
    audio_path = extract_audio(video_path)
    
    print("🔊 Diarizing speakers...")
    speakers = diarize_audio(audio_path)
    
    print("📝 Transcribing...")
    segments = transcribe_audio(audio_path)
    
    print("👥 Assigning speakers...")
    transcript = assign_speakers(segments, speakers)

    print("🧠 Inferring speaker names from transcript...")
    speaker_name_map = identify_speaker_names_via_text(transcript)
    
    print("🖼️ Extracting frames for unknown speakers...")
    speaker_frames = extract_frames_for_unknown_speakers(video_path, transcript, speaker_name_map)
    
    print("🤖 Identifying unknown speakers with GPT...")
    new_names = identify_unknown_speakers_with_gpt(speaker_frames)

    print("📜 Generating final transcript...")
    final = generate_named_transcript(transcript, speaker_name_map, new_names)
    
    print("🔍 Finding checkworthy statements...")
    final_statements = find_checkworthy_statements(final)
    
    if not final_statements:
        print("❌ No checkworthy statements found.")
        final_statements = find_checkworthy_statements(final)
    
    print(f"✅ Found {len(final_statements)} checkworthy statements.")
    
    final_statements_json = []

    for s in final_statements:
        frame_path = extract_frame_for_statement(video_path, s)

        statement_dict = s.dict()
        statement_dict["frame_path"] = frame_path or "N/A"

        final_statements_json.append(statement_dict)
    
    return final_statements_json
