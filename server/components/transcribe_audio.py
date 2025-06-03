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
    # Try to find a device with 'loopback' in the name
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if dev['hostapi'] == wasapi_index and dev['max_input_channels'] > 0 and 'loopback' in dev['name'].lower():
            return idx
    # Try to find a device with 'stereo mix' in the name
    for idx, dev in enumerate(devices):
        if dev['hostapi'] == wasapi_index and dev['max_input_channels'] > 0 and 'stereo mix' in dev['name'].lower():
            return idx
    # Fallback: prompt user to select from available input devices
    print("\n[ERROR] No loopback or Stereo Mix device found. Please select an input device manually:")
    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{idx}: {dev['name']} (hostapi: {dev['hostapi']})")
    try:
        user_idx = int(input("Enter the device index to use for speaker/loopback: "))
        return user_idx
    except Exception:
        raise RuntimeError('No valid device selected for loopback/speaker capture.')

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
        # Debug: print max amplitude to check if audio is being captured
        print(f"[DEBUG] Mixed audio max amplitude: {np.max(np.abs(mixed)):.4f}")
        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 1.0:
            mixed = mixed / max_val
        await queue.put(mixed)
        mic_buffer = None
        speaker_buffer = None

async def send_audio(ws, sample_rate):
    print("Streaming mic+speaker audio to Deepgram...")
    list_audio_devices()  # Print devices for user reference
    mic_device = sd.default.device[0]  # Default input device index
    try:
        speaker_device = get_loopback_device()  # Dynamically get loopback device
    except Exception as e:
        print(f"[ERROR] Could not find loopback device: {e}")
        return
    print(f"Using mic device index: {mic_device}")
    print(f"Using speaker device index: {speaker_device}")
    print(f"Using sample rate: {sample_rate}")
    with sd.InputStream(callback=mic_callback, channels=CHANNELS, samplerate=sample_rate, dtype='float32', device=mic_device, blocksize=2048) as mic_stream, \
         sd.InputStream(callback=speaker_callback, channels=CHANNELS, samplerate=sample_rate, dtype='float32', device=speaker_device, blocksize=2048) as speaker_stream:
        mixer_task = asyncio.create_task(audio_mixer())
        while True:
            data = await queue.get()
            audio_data = (data * 32767).astype(np.int16).tobytes()
            await ws.send(audio_data)

def find_common_samplerate(mic_device, speaker_device, rates=(16000, 44100, 48000)):
    mic_supported = set()
    speaker_supported = set()
    for rate in rates:
        try:
            sd.check_input_settings(device=mic_device, samplerate=rate)
            mic_supported.add(rate)
        except Exception:
            pass
        try:
            sd.check_input_settings(device=speaker_device, samplerate=rate)
            speaker_supported.add(rate)
        except Exception:
            pass
    common = mic_supported & speaker_supported
    if not common:
        raise RuntimeError(f"No common supported sample rate for mic device {mic_device} and speaker device {speaker_device}. Tried: {rates}")
    # Prefer higher rates
    return max(common)

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
    mic_device = sd.default.device[0]
    try:
        speaker_device = get_loopback_device()
    except Exception as e:
        print(f"[ERROR] Could not find loopback device: {e}")
        return
    try:
        sample_rate = find_common_samplerate(mic_device, speaker_device)
    except Exception as e:
        print(f"[ERROR] Could not find a common supported sample rate: {e}")
        return
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{DEEPGRAM_URL}?encoding=linear16&sample_rate={sample_rate}&channels={CHANNELS}&punctuate=true&interim_results=true"
    async with websockets.connect(url, extra_headers=headers) as ws:
        send_task = asyncio.create_task(send_audio(ws, sample_rate))
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
