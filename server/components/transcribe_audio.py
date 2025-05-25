import os
import asyncio
import json
import websockets
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
import cohere  # pip install cohere
from transcript_ai import TranscriptAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import broadcast_transcript, broadcast_summary

print(f"[TRANSCRIBE_AUDIO] Script started with args: {sys.argv}")

# Load environment variables from .env file
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_URL = "wss://api.deepgram.com/v1/listen"

SAMPLE_RATE = 16000
CHANNELS = 1

queue = asyncio.Queue(maxsize=10)
main_loop = None  # Will be set in __main__
main_server_loop = None

# Shared buffers for mic and speaker
mic_buffer = None
speaker_buffer = None

# Callback for microphone
def mic_callback(indata, frames, time, status):
    global mic_buffer
    if status:
        print(f"⚠️ Mic stream status: {status}")
    mic_buffer = indata.copy()

# Callback for speaker (loopback)
def speaker_callback(indata, frames, time, status):
    global speaker_buffer
    if status:
        print(f"⚠️ Speaker stream status: {status}")
    speaker_buffer = indata.copy()

def get_loopback_device():
    # Find the hostapi index for Windows WASAPI
    hostapis = sd.query_hostapis()
    wasapi_index = None
    for idx, api in enumerate(hostapis):
        if api['name'].lower() == 'windows wasapi':
            wasapi_index = idx
            break
    if wasapi_index is None:
        raise RuntimeError('Windows WASAPI hostapi not found.')
    # Find the first WASAPI loopback device (for speakers)
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if dev['hostapi'] == wasapi_index and dev['max_input_channels'] > 0 and 'loopback' in dev['name'].lower():
            return idx
    # Fallback: find any device with 'loopback' in the name
    for idx, dev in enumerate(devices):
        if 'loopback' in dev['name'].lower():
            return idx
    raise RuntimeError('No loopback device found. Please check your audio devices.')

def list_audio_devices():
    print("\nAvailable audio devices:")
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        print(f"{idx}: {dev['name']} (hostapi: {dev['hostapi']}, max_input_channels: {dev['max_input_channels']})")
    print()

async def audio_mixer():
    global mic_buffer, speaker_buffer
    while True:
        # Wait until both buffers have data
        while mic_buffer is None or speaker_buffer is None:
            await asyncio.sleep(0.005)
        # Mix both sources (simple sum, then normalize)
        mixed = mic_buffer + speaker_buffer
        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 1.0:
            mixed = mixed / max_val
        await queue.put(mixed)
        mic_buffer = None
        speaker_buffer = None

async def send_audio(ws):
    print("Streaming mic+speaker audio to Deepgram...")
    list_audio_devices()  # Print devices for user reference
    mic_device = 11  # Microphone Array (Intel® Smart ...) or your preferred mic
    speaker_device = 1  # Stereo Mix (Realtek(R) Audio)
    print(f"Using mic device index: {mic_device}")
    print(f"Using speaker device index: {speaker_device}")
    # Increase blocksize to reduce overflow risk
    with sd.InputStream(callback=mic_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='float32', device=mic_device, blocksize=2048) as mic_stream, \
         sd.InputStream(callback=speaker_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='float32', device=speaker_device, blocksize=2048) as speaker_stream:
        # Start the audio mixer task
        mixer_task = asyncio.create_task(audio_mixer())
        while True:
            data = await queue.get()
            audio_data = (data * 32767).astype(np.int16).tobytes()
            await ws.send(audio_data)

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ai = TranscriptAI()

async def receive_transcripts(ws):
    last_transcript = ""
    async for message in ws:
        msg_json = json.loads(message)
        transcript = msg_json.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
        if transcript and transcript != last_transcript:
            print(f"Transcript: {transcript}")
            ai.add_transcript(transcript)
            last_transcript = transcript
            # Optionally, auto-summarize every time transcript grows by 500 chars
            if len(ai.full_transcript) % 500 < len(transcript):
                summary = await ai.summarize()
                if summary and main_server_loop:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_summary(summary),
                        main_server_loop
                    )
            # Broadcast to frontend
            if main_server_loop:
                asyncio.run_coroutine_threadsafe(
                    broadcast_transcript(transcript),
                    main_server_loop
                )
            else:
                await broadcast_transcript(transcript)

async def main():
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{DEEPGRAM_URL}?encoding=linear16&sample_rate={SAMPLE_RATE}&channels={CHANNELS}&punctuate=true&interim_results=true"

    async with websockets.connect(url, extra_headers=headers) as ws:
        send_task = asyncio.create_task(send_audio(ws))
        receive_task = asyncio.create_task(receive_transcripts(ws))
        await asyncio.gather(send_task, receive_task)

if __name__ == "__main__":
    import threading
    from main import run_ws_server
    if '--ws-mode' in sys.argv:
        # If started in ws-mode, only run the transcription logic (no server)
        import asyncio
        # Instead of getting the event loop here, get it from the parent process if possible
        # For now, fallback to the current event loop
        main_server_loop = None  # Do not set to get_event_loop here!
        main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_loop)
        main_loop.run_until_complete(main())
        asyncio.run(ai.summarize())
        sys.exit(0)
    # Start websocket server in a background thread
    ws_thread = threading.Thread(target=lambda: asyncio.run(run_ws_server()), daemon=True)
    ws_thread.start()
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)
    main_loop.run_until_complete(main())
    # Optionally, print final summary at the end
    asyncio.run(ai.summarize())
