# Module Spec: Aura GUI Dashboard

## Responsibility
Providing a user interface to configure triggers, monitor system health, and toggle engines.

## Interface
- **Role**: Process controller (Starts/Stops sub-engines).
- **Visualization**: Real-time display of recognized words and gesture confidence.

## Key Components
- **Dashboard**: Toggle switches for Voice and Gesture engines.
- **Mapping Editor**: UI to assign AHK scripts to specific gestures/commands.
- **Log Viewer**: Console output for debugging triggers.

## Technology
- `CustomTkinter`: Modern, dark-themed UI components.

## Performance Constraints
- GUI must remain responsive even if engines are under heavy load.
- Should minimize to system tray to stay out of the way during gaming.
