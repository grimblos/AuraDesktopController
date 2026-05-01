"""
Aura Voice Engine
Handles offline speech recognition and wake-word detection using Vosk.
"""

from multiprocessing import Queue

class VoiceEngine:
    def __init__(self, model_path: str, wake_word: str):
        """
        Initialize the voice engine with a specific STT model and wake word.
        """
        self.model_path = model_path
        self.wake_word = wake_word
        pass

    def run(self, event_queue: Queue):
        """
        Main loop for audio capture and recognition.
        Pushes recognized triggers to the event_queue.
        """
        pass

    def stop(self):
        """
        Gracefully shut down the microphone stream and engine.
        """
        pass
