import asyncio
import websockets
import json
import subprocess
import threading
import os
import sys

connected_clients = set()
transcription_process = None
transcription_lock = threading.Lock()
main_event_loop = None
latest_summary = ""  # Global variable to store the latest summary

def start_transcription():
    global transcription_process
    with transcription_lock:
        if transcription_process is None or transcription_process.poll() is not None:
            print("[SERVER] Starting transcription subprocess...")
            transcription_process = subprocess.Popen(
                [sys.executable, '-u', 'components/transcribe_audio.py', '--ws-mode'],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            threading.Thread(target=print_subprocess_output, args=(transcription_process,), daemon=True).start()
        else:
            print("[SERVER] Transcription already running.")

def print_subprocess_output(proc):
    import re
    summary_mode = False
    summary_lines = []
    for line in proc.stdout:
        print(f"[TRANSCRIBE] {line}", end="")
        # Transcript broadcast
        match = re.match(r"Transcript: (.*)", line)
        if match:
            transcript = match.group(1)
            if main_event_loop:
                asyncio.run_coroutine_threadsafe(
                    broadcast_transcript(transcript), main_event_loop
                )
        # Summary broadcast
        if "=== SUMMARY ===" in line:
            summary_mode = True
            summary_lines = []
            continue
        if summary_mode:
            if "===============" in line:
                summary_mode = False
                summary = "\n".join(summary_lines).strip()
                if summary and main_event_loop:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_summary(summary), main_event_loop
                    )
            else:
                summary_lines.append(line.rstrip())

def stop_transcription():
    global transcription_process
    with transcription_lock:
        if transcription_process and transcription_process.poll() is None:
            print("[SERVER] Stopping transcription subprocess...")
            transcription_process.terminate()
            try:
                transcription_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                transcription_process.kill()
            print("[SERVER] Transcription stopped.")
        else:
            print("[SERVER] No transcription process running.")

async def transcript_ws_server(websocket, path):
    print("[SERVER] Client connected")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "command":
                    cmd = data.get("command")
                    if cmd == "start":
                        start_transcription()
                    elif cmd == "stop":
                        stop_transcription()
                elif data.get("type") == "chatbot_question":
                    # Handle chatbot question: answer using summary
                    from components.transcript_ai import TranscriptAI
                    ai = TranscriptAI()
                    # Use the latest summary (store it globally)
                    global latest_summary
                    question = data.get("question", "")
                    summary = latest_summary if 'latest_summary' in globals() else ""
                    if summary:
                        # Use Cohere to answer based on summary
                        import cohere, os
                        co = cohere.Client(os.getenv("COHERE_API_KEY"))
                        prompt = f"Summary: {summary}\n\nQuestion: {question}\nAnswer:"
                        response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=100, temperature=0.3)
                        answer = response.generations[0].text.strip()
                    else:
                        answer = "No summary available yet. Please wait for a summary to be generated."
                    await websocket.send(json.dumps({"type": "chatbot_response", "answer": answer}))
            except Exception as e:
                print(f"Error handling message: {e}")
    finally:
        connected_clients.remove(websocket)
        print("[SERVER] Client disconnected")

async def broadcast_transcript(transcript):
    if connected_clients:
        data = json.dumps({"type": "transcript", "text": transcript})
        print(f"[BACKEND] Broadcasting to {len(connected_clients)} clients: {data}")
        await asyncio.gather(*(client.send(data) for client in connected_clients))

async def broadcast_summary(summary):
    global latest_summary
    latest_summary = summary
    if connected_clients:
        data = json.dumps({"type": "summary", "text": summary})
        print(f"[BACKEND] Broadcasting summary to {len(connected_clients)} clients: {data}")
        await asyncio.gather(*(client.send(data) for client in connected_clients))

# To run the websocket server
async def run_ws_server():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    server = await websockets.serve(transcript_ws_server, "0.0.0.0", 8765)
    print("WebSocket server started on ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_ws_server())