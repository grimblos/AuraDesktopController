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

    def run(self, event_queue: Queue, audio_source=None):
        """
        Main loop for audio capture and processing.
        Pushes detected command labels to the event_queue.
        """
        # If audio_source is None, we'd use PyAudio locally.
        # If it's a queue, we're in Remote Mode.
        # TODO: Implement local PyAudio capture for standalone mode.
        
        while True:
            if audio_source:
                data = audio_source.get() # Get audio chunk from networking module
                text = self.process_audio(data)
                
                if text:
                    print(f"Recognized: {text}")
                    # Simple Wake-Word Check
                    if self.wake_word in text:
                        # Extract the command after the wake word
                        command = text.split(self.wake_word)[-1].strip().upper().replace(" ", "_")
                        if command:
                            event_queue.put({"engine": "voice", "label": command})
            
            # TODO: Advanced models can implement fuzzy string matching or 
            # Intent Classification (e.g., mapping 'Shut down the camera' to 'APP_STOP_GESTURE').

    def stop(self):
        """
        Gracefully shut down the microphone stream and engine.
        """
        pass
