import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import time

OUTPUT_FILE_NAME = "out.wav"    # file name.
SAMPLE_RATE = 48000              # [Hz]. sampling rate.

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.mic_data = []
        self.speaker_data = []
        self.mic_thread = None
        self.speaker_thread = None
        
    def record_microphone(self):
        """Continuously record from microphone until stopped"""
        try:
            with sc.get_microphone(id=str(sc.default_microphone().name)).recorder(samplerate=SAMPLE_RATE) as mic:
                print(f"Recording from microphone: {sc.default_microphone().name}")
                while self.is_recording:
                    # Record in small chunks (0.1 seconds)
                    chunk = mic.record(numframes=int(SAMPLE_RATE * 0.1))
                    if len(chunk.shape) > 1:
                        self.mic_data.extend(chunk[:, 0])  # Take first channel
                    else:
                        self.mic_data.extend(chunk)
        except Exception as e:
            print(f"Microphone recording error: {e}")
    
    def record_speaker(self):
        """Continuously record from speaker until stopped"""
        try:
            with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as speaker:
                print(f"Recording from speaker: {sc.default_speaker().name}")
                while self.is_recording:
                    # Record in small chunks (0.1 seconds)
                    chunk = speaker.record(numframes=int(SAMPLE_RATE * 0.1))
                    if len(chunk.shape) > 1:
                        self.speaker_data.extend(chunk[:, 0])  # Take first channel
                    else:
                        self.speaker_data.extend(chunk)
        except Exception as e:
            print(f"Speaker recording error: {e}")
    
    def start_recording(self):
        """Start recording from both microphone and speaker"""
        if self.is_recording:
            print("Recording is already in progress!")
            return
        
        print("Starting recording...")
        print("Press Enter to stop recording at any time.")
        
        # Reset data
        self.mic_data = []
        self.speaker_data = []
        self.is_recording = True
        
        # Start recording threads
        self.mic_thread = threading.Thread(target=self.record_microphone)
        self.speaker_thread = threading.Thread(target=self.record_speaker)
        
        self.mic_thread.start()
        self.speaker_thread.start()
        
        print("🔴 Recording started! Press Enter to stop...")
    
    def stop_recording(self):
        """Stop recording and save files"""
        if not self.is_recording:
            print("No recording in progress!")
            return
        
        print("⏹️  Stopping recording...")
        self.is_recording = False
        
        # Wait for threads to finish
        if self.mic_thread:
            self.mic_thread.join()
        if self.speaker_thread:
            self.speaker_thread.join()
        
        # Convert to numpy arrays
        mic_audio = np.array(self.mic_data, dtype=np.float32)
        speaker_audio = np.array(self.speaker_data, dtype=np.float32)
        
        # Make sure both arrays have the same length
        min_length = min(len(mic_audio), len(speaker_audio))
        if min_length > 0:
            mic_audio = mic_audio[:min_length]
            speaker_audio = speaker_audio[:min_length]
            
            # Mix both audio sources
            mixed_audio = mic_audio + speaker_audio
            # Normalize to prevent clipping
            if np.max(np.abs(mixed_audio)) > 0:
                mixed_audio = mixed_audio / np.max(np.abs(mixed_audio)) * 0.8
            
            # Save the three output files in the audio directory
            audio_dir = '../audio/'
            sf.write(audio_dir + OUTPUT_FILE_NAME, mixed_audio, SAMPLE_RATE)
            sf.write(audio_dir + "microphone_only.wav", mic_audio, SAMPLE_RATE)
            sf.write(audio_dir + "speaker_only.wav", speaker_audio, SAMPLE_RATE)
            
            duration = len(mixed_audio) / SAMPLE_RATE
            print(f"\n✅ Recording completed! Duration: {duration:.2f} seconds")
            print(f"Audio saved to:")
            print(f"- {audio_dir + OUTPUT_FILE_NAME} (mixed)")
            print(f"- {audio_dir}microphone_only.wav (mic only)")
            print(f"- {audio_dir}speaker_only.wav (speaker only)")
        else:
            print("❌ No audio data recorded!")

def main():
    recorder = AudioRecorder()
    
    print("=== Dynamic Audio Recorder ===")
    print("Commands:")
    print("  'start' or 's' - Start recording")
    print("  'stop' or Enter - Stop recording")
    print("  'quit' or 'q' - Exit program")
    print()
    
    while True:
        if recorder.is_recording:
            # If recording, wait for Enter to stop
            input()
            recorder.stop_recording()
        else:
            # If not recording, show menu
            command = input("Enter command (start/stop/quit): ").strip().lower()
            
            if command in ['start', 's']:
                recorder.start_recording()
            elif command in ['stop', '']:
                recorder.stop_recording()
            elif command in ['quit', 'q', 'exit']:
                if recorder.is_recording:
                    recorder.stop_recording()
                print("Goodbye!")
                break
            else:
                print("Invalid command. Use 'start', 'stop', or 'quit'")

if __name__ == "__main__":
    main()