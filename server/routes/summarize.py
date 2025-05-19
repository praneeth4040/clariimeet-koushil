import sys
import os
import json
from transformers import pipeline

# Load the summarizer model (only once)
print("Loading summarizer model...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
print("Model loaded.")

def summarize_file(filepath):
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read().strip()

    if len(text) == 0:
        return {"error": "Transcript file is empty."}

    # Break the text into manageable chunks (~1024 tokens max)
    max_chunk_tokens = 1024
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_tokens):
        chunk = " ".join(words[i:i + max_chunk_tokens])
        chunks.append(chunk)

    summaries = []
    for chunk in chunks:
        word_count = len(chunk.split())
        max_len = min(150, int(word_count * 0.7)) if word_count > 50 else 30
        min_len = 10 if word_count < 50 else 25

        print(f"Summarizing chunk of {word_count} words (max_length={max_len}, min_length={min_len})...")
        summary = summarizer(
            chunk,
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )[0]["summary_text"]

        summaries.append(summary)

    final_summary = "\n".join(summaries)

    return {"summary": final_summary}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python summarize.py <transcript_file.txt>"}))
        sys.exit(1)

    input_file = sys.argv[1]
    result = summarize_file(input_file)

    if "summary" in result:
        # Save to .summary.txt
        output_file = input_file.replace(".txt", ".summary.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["summary"])
        print(f"Summary saved to {output_file}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
