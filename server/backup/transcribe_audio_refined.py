import os
import asyncio
import json
import websockets
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_URL = "wss://api.deepgram.com/v1/listen"

SAMPLE_RATE = 16000
CHANNELS = 1

queue = asyncio.Queue(maxsize=10)  # Limit queue size for efficiency
main_loop = None  # Will be set in __main__

def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio stream status: {status}")
    # Put raw float32 data into the queue (processing in async loop)
    try:
        asyncio.run_coroutine_threadsafe(queue.put(indata.copy()), main_loop)
    except Exception as e:
        print(f"Callback queue error: {e}")

async def send_audio(ws):
    print("🎙️ Streaming mic audio to Deepgram...")
    with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='float32'):
        while True:
            data = await queue.get()
            # Convert to int16 PCM bytes here (outside callback)
            audio_data = (data * 32767).astype(np.int16).tobytes()
            await ws.send(audio_data)

async def receive_transcripts(ws):
    async for message in ws:
        msg_json = json.loads(message)
        transcript = msg_json.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
        if transcript:
            print(f"📝 {transcript}")

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
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)
    main_loop.run_until_complete(main())
