# Module Spec: Aura Voice Engine

## Responsibility
Continuous offline monitoring of microphone input for a user-defined wake word and subsequent command recognition.

## Interface
- **Input**: Configuration object (Wake Word, Model Path).
- **Output**: `Queue` events containing recognized commands.

## Key Functions
- `initialize_model(model_path: str)`: Loads the Vosk model into memory.
- `monitor_stream(wake_word: str, event_queue: Queue)`: The main loop that processes audio chunks.
- `set_wake_word(new_word: str)`: Dynamically updates the word being monitored.

## Dependencies
- `vosk`: Speech-to-text engine.
- `pyaudio`: Cross-platform audio I/O.

## Performance Constraints
- Must use < 5% CPU on a modern mid-range processor while idling (waiting for wake word).
- Must handle audio buffer overflows gracefully during high system load (gaming).
