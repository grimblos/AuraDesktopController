"""
Aura Voice Engine
Monitors audio stream for the Wake Word and recognizes commands using Vosk.
"""

import os
import json
import queue
import sys
from vosk import Model, KaldiRecognizer
from multiprocessing import Queue

class VoiceEngine:
    def __init__(self, model_path: str, wake_word: str = "aura"):
        """
        Initialize the voice engine with Vosk model and wake word.
        """
        if not os.path.exists(model_path):
            print(f"Please download a model from https://alphacephei.com/vosk/models and unpack as {model_path}")
            # TODO: Advanced model can implement an auto-downloader for the Vosk model.
            return

        self.model = Model(model_path)
        self.wake_word = wake_word.lower()
        self.rec = KaldiRecognizer(self.model, 16000)

    def process_audio(self, data):
        """
        Run Vosk inference on a chunk of audio data.
        """
        if self.rec.AcceptWaveform(data):
            result = json.loads(self.rec.Result())
            return result.get("text", "")
        else:
            # Partial results could be used for lower latency wake-word detection
            # partial = json.loads(self.rec.PartialResult())
            return None

    def run(self, event_queue: Queue, control_queue: Queue = None, audio_source=None):
        """
        Main loop for audio capture and processing.
        Pushes detected command labels to the event_queue.
        """
        import pyaudio
        
        self.is_active = True
        pa = None
        stream = None
        
        # Initialize local PyAudio stream if no network source is provided
        if audio_source is None:
            try:
                pa = pyaudio.PyAudio()
                stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
                stream.start_stream()
                print("Microphone successfully initialized.")
            except Exception as e:
                print(f"Failed to initialize microphone: {e}")
                return
        
        try:
            while True:
                # 1. Process Control Messages
                if control_queue and not control_queue.empty():
                    msg = control_queue.get()
                    if msg.get("target") == "voice":
                        if msg.get("action") == "stop":
                            self.is_active = False
                            print("Voice Engine Paused.")
                        elif msg.get("action") == "start":
                            self.is_active = True
                            print("Voice Engine Resumed.")
                        elif msg.get("action") == "set_wake_word":
                            self.wake_word = msg.get("value", self.wake_word).lower()
                            print(f"Wake word changed to: {self.wake_word}")

                if not self.is_active:
                    import time
                    time.sleep(0.1)
                    continue

                # 2. Capture Audio Chunk
                if audio_source:
                    data = audio_source.get() 
                else:
                    data = stream.read(4000, exception_on_overflow=False)
                
                if not data: continue

                text = self.process_audio(data)
                
                if text:
                    print(f"[Aura Ears] Heard: '{text}'")
                    # Wake-Word logic
                    if self.wake_word in text:
                        command_text = text.split(self.wake_word)[-1].strip()
                        if command_text:
                            # Standardize command (e.g. "volume up" -> "VOLUME_UP")
                            command_label = command_text.upper().replace(" ", "_")
                            print(f"[Aura Core] Voice Trigger Issued: {command_label}")
                            event_queue.put({"engine": "voice", "label": command_label})
        except KeyboardInterrupt:
            pass
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            if pa:
                pa.terminate()

    def stop(self):
        """
        Gracefully shut down the microphone stream and engine.
        """
        pass
