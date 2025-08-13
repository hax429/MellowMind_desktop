# Moly Logging System Guide

## Overview
The Moly application now includes a comprehensive logging system with millisecond precision timestamps (both local and UTC) and reusable helper methods for easy integration of new windows.

## Log Files Created
For each session, three log files are automatically created:
- `{participant_id}_{timestamp}_actions.log` - All user actions and system events
- `{participant_id}_{timestamp}_descriptive_responses.txt` - User responses to descriptive prompts
- `{participant_id}_{timestamp}.log` - Legacy log file

## Reusable Logging Helper Methods

### 1. `log_screen_transition(screen_name, details="")`
Use when transitioning between screens.
```python
self.log_screen_transition("new_screen", "Additional context")
# Logs: SCREEN_TRANSITION - Transitioning to new_screen - Additional context
```

### 2. `log_screen_displayed(screen_name, details="")`
Use when a screen is fully loaded and ready for user interaction.
```python
self.log_screen_displayed("new_screen", "Screen ready with all components")
# Logs: SCREEN_DISPLAYED - new_screen screen displayed and ready - Screen ready with all components
```

### 3. `log_user_input(input_type, details="")`
Use for logging user interactions.
```python
self.log_user_input("KEY_PRESS", "Space key pressed")
self.log_user_input("BUTTON_CLICK", "Submit button clicked")
self.log_user_input("MOUSE_CLICK", "Clicked on element X")
```

### 4. `log_window_event(event_type, window_name, details="")`
Use for window-specific events.
```python
self.log_window_event("WINDOW_RESIZED", "main_window", "Resized to 800x600")
self.log_window_event("VIDEO_STARTED", "stroop_screen", "Video playback initiated")
```

## Adding a New Window with Logging

### Step 1: Add Transition Message
```python
TRANSITION_MESSAGES = {
    'existing_screens': "...",
    'your_new_screen': "Message shown on transition screen for your new screen"
}
```

### Step 2: Create Screen Methods
```python
def switch_to_your_new_screen(self):
    """Switch to your new screen with transition."""
    self.show_transition_screen(
        TRANSITION_MESSAGES['your_new_screen'],
        self._setup_your_new_screen
    )

def _setup_your_new_screen(self):
    """Actually setup your new screen after confirmation."""
    print("Setting up Your New Screen")
    self.log_screen_transition("your_new_screen")
    self.clear_screen()
    self.current_screen = "your_new_screen"
    
    # ... UI setup code ...
    
    # Log when screen is ready
    self.log_screen_displayed("your_new_screen")
```

### Step 3: Add User Interaction Logging
```python
def on_your_button_click(self):
    """Handle button click in your screen."""
    self.log_user_input("BUTTON_PRESS", "Your button clicked")
    # ... handle the action ...

def on_your_key_press(self, event):
    """Handle key press in your screen."""
    self.log_user_input("KEY_PRESS", f"{event.keysym} key pressed in your_new_screen")
    # ... handle the key press ...
```

## Current Transition Flow with Logging

1. **Relaxation → Descriptive Task**
   - Transition screen displayed and logged
   - User confirmation logged
   - Screen transition and display logged

2. **Descriptive Task → Stroop**
   - Transition screen displayed and logged
   - User confirmation logged
   - Screen transition and display logged

3. **Stroop → Math Task**
   - Transition screen displayed and logged
   - User confirmation logged
   - Screen transition and display logged

4. **Math Task → Post-Study Rest**
   - Transition screen displayed and logged
   - User confirmation logged
   - Screen transition and display logged

## Special Logging Features

### Sentence Completion Logging
When `DESCRIPTIVE_LINE_LOGGING = True`, the system automatically logs sentences when users type periods:
```
[2025-08-13 15:03:03.529 Local | 2025-08-13 19:03:03.529 UTC] SENTENCE_COMPLETED - "This is a complete sentence." (Screen: descriptive_task)
```

### Descriptive Response Logging
User responses are automatically saved to a separate file when moving between prompts or leaving the descriptive task screen.

### Millisecond Precision
All timestamps include milliseconds for precise timing analysis:
```
[2025-08-13 15:03:03.529 Local | 2025-08-13 19:03:03.529 UTC] ACTION_TYPE - Details
```

## Best Practices

1. **Always log screen transitions** using `log_screen_transition()`
2. **Always log when screens are ready** using `log_screen_displayed()`
3. **Log all user interactions** using `log_user_input()`
4. **Use consistent naming** for screen names and event types
5. **Include meaningful details** in the details parameter
6. **Test logging** by checking the generated log files

## Error Handling
All logging operations are wrapped in try-catch blocks to prevent crashes. If logging fails, a warning is printed but the application continues normally.
