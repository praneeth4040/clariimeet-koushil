import whisper
import os
import sys
import json
from datetime import datetime

def transcribe_audio(file_path: str, model_size: str = "base") -> dict:
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        model = whisper.load_model(model_size)
        print(f"Model '{model_size}' loaded. Transcribing...")
        result = model.transcribe(file_path)
        return {"text": result["text"]}
    except Exception as e:
        return {"error": str(e)}

def save_transcript(file_path: str, transcript_text: str):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_dir = os.path.join("transcripts")
    os.makedirs(output_dir, exist_ok=True)

    txt_path = os.path.join(output_dir, f"{base_name}_{timestamp}.txt")
    json_path = os.path.join(output_dir, f"{base_name}_{timestamp}.json")

    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(transcript_text)
    
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump({"text": transcript_text}, json_file, ensure_ascii=False, indent=2)

    print(f"Saved TXT: {txt_path}")
    print(f"Saved JSON: {json_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python transcribe.py <audio_file_path>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    result = transcribe_audio(file_path, model_size)
    
    if "text" in result:
        save_transcript(file_path, result["text"])
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result))
