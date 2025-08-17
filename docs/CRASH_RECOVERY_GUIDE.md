# Moly Crash Recovery System Guide

## Overview
The Moly application includes a robust crash recovery system that automatically detects incomplete sessions and offers users the option to resume where they left off or start fresh.

## How It Works

### 1. **Crash Detection**
The system detects crashes by checking for incomplete sessions on startup:
- **Complete sessions**: Have `session_end_time` in their `session_info.json` file
- **Incomplete sessions**: Missing `session_end_time` (indicating unexpected termination)

### 2. **Recovery Process**
When an incomplete session is detected:
1. **Analysis**: The system analyzes the log files to determine the last state
2. **Recovery Dialog**: User is presented with options to resume or start new
3. **State Restoration**: If resuming, the app restores the exact state where it left off

### 3. **State Recovery**
The system can recover to any of these states:
- **Participant ID Screen**: If crash happened during initial setup
- **Relaxation Screen**: If crash happened during relaxation phase
- **Descriptive Task**: Restores current prompt index and completed responses
- **Stroop Screen**: If crash happened during video task
- **Math Task**: If crash happened during math evaluation
- **Post-Study Rest**: If crash happened during final rest phase

## Recovery Dialog

When a crash is detected, users see:

```
🔄 Session Recovery

An incomplete session was detected for participant MA001.

Session started: 2025-08-13 15:07:08
Last screen: descriptive_task

Would you like to resume where you left off, or start a new session?

[RESUME SESSION]  [START NEW SESSION]
```

## Recovery Features

### **Descriptive Task Recovery**
- **Prompt Position**: Restores exact prompt index where user left off
- **Completed Responses**: All previously completed responses are preserved
- **Partial Text Restoration**: Restores any text the user was typing when the crash occurred
- **Countdown Timer Recovery**: Restores the countdown timer to the exact remaining time
- **Progress Indicator**: Shows notification of restored words and remaining time

### **Log Continuity**
- **Same Log Files**: Recovery continues writing to the original log files
- **Recovery Marker**: `SESSION_RESUMED` action is logged with details
- **Time Continuity**: Session duration calculations continue from original start time

### **Data Integrity**
- **No Data Loss**: All completed responses and actions are preserved
- **Consistent State**: Application state matches exactly where user left off
- **Audit Trail**: Complete log of crash and recovery events

## Technical Implementation

### **Crash Detection Logic**
```python
def check_for_incomplete_sessions(self):
    # Scan all participant directories
    # Check session_info files for missing session_end_time
    # Return most recent incomplete session
```

### **State Analysis**
```python
def determine_recovery_state(self, actions, responses, last_screen):
    # Analyze actions to determine exact state
    # Count completed responses for descriptive task
    # Return recovery state object with all necessary data
```

### **Recovery Execution**
```python
def resume_session(self, recovery_data):
    # Set up participant data and log file paths
    # Restore session start time for duration continuity
    # Jump to appropriate screen based on recovery state
```

## Log Entries

### **Recovery Detection**
When a crash is detected, you'll see console output:
```
🔄 Found incomplete session for MA001
🔄 Crash Recovery - Incomplete session detected
```

### **Recovery Logging**
When session is resumed, multiple log entries are created:

**Application Reopened:**
```json
{
  "timestamp": {...},
  "participant_id": "MA001",
  "action_type": "APPLICATION_REOPENED",
  "details": "Application reopened after crash, resuming from descriptive_task screen",
  "screen": "recovery",
  "session_duration_seconds": 129.2
}
```

**Session Resumed:**
```json
{
  "timestamp": {...},
  "participant_id": "MA001",
  "action_type": "SESSION_RESUMED",
  "details": "Resumed session from descriptive_task screen",
  "screen": "recovery",
  "session_duration_seconds": 129.2
}
```

**Partial Text Updates (during typing):**
```json
{
  "timestamp": {...},
  "participant_id": "MA001",
  "action_type": "PARTIAL_TEXT_UPDATE",
  "details": {
    "text_content": "The image shows a beautiful landscape...",
    "text_length": 118,
    "word_count": 20,
    "current_prompt_index": 0,
    "countdown_remaining": 120
  },
  "screen": "descriptive_task",
  "session_duration_seconds": 100.0
}
```

**Countdown State Updates:**
```json
{
  "timestamp": {...},
  "participant_id": "MA001",
  "action_type": "COUNTDOWN_STATE",
  "details": "{\"remaining_seconds\": 120, \"total_seconds\": 300, \"percentage_complete\": 60.0}",
  "screen": "descriptive_task",
  "session_duration_seconds": 100.0
}
```

## Testing Recovery System

### **Simulate a Crash**
1. Start the application normally
2. Progress to any screen (e.g., descriptive task)
3. Force-quit the application (Ctrl+C or kill process)
4. Restart the application
5. Recovery dialog should appear

### **Manual Testing**
You can manually create an incomplete session for testing:
1. Copy an existing session directory
2. Edit the `session_info.json` file to remove `session_end_time` and related fields
3. Restart the application

## Recovery States

### **Participant ID Screen**
- **When**: Crash during initial setup
- **Recovery**: Shows participant ID entry screen
- **Data**: No data to restore

### **Relaxation Screen**
- **When**: Crash during relaxation phase
- **Recovery**: Returns to relaxation video
- **Data**: Preserves session timing

### **Descriptive Task**
- **When**: Crash during descriptive task
- **Recovery**: Restores exact prompt index and completed responses
- **Data**: All previous responses preserved, continues from current prompt

### **Stroop Screen**
- **When**: Crash during stroop video task
- **Recovery**: Returns to stroop screen
- **Data**: Preserves session context

### **Math Task**
- **When**: Crash during math evaluation
- **Recovery**: Returns to math task screen
- **Data**: Preserves session timing

### **Post-Study Rest**
- **When**: Crash during final rest
- **Recovery**: Returns to post-study rest screen
- **Data**: Complete session context preserved

## Benefits

### **User Experience**
- **No Lost Work**: Users don't lose progress from crashes
- **Seamless Recovery**: One-click resume functionality
- **Choice**: Users can choose to start fresh if preferred

### **Research Integrity**
- **Complete Data**: No data loss from technical issues
- **Audit Trail**: Full record of crashes and recoveries
- **Time Accuracy**: Proper session duration tracking across crashes

### **System Robustness**
- **Fault Tolerance**: Application handles unexpected shutdowns gracefully
- **Automatic Detection**: No manual intervention needed
- **Safe Fallback**: If recovery fails, defaults to normal startup

## Error Handling

The recovery system includes comprehensive error handling:
- **File Access Errors**: Gracefully handles corrupted or inaccessible log files
- **Data Format Errors**: Handles malformed JSON or missing data
- **Recovery Failures**: Falls back to normal startup if recovery fails
- **User Choice**: Always provides option to start fresh

## Configuration

The recovery system works automatically with no configuration needed. However, you can customize:
- **Recovery Dialog Text**: Modify messages in the `show_recovery_dialog()` method
- **Recovery States**: Add new recovery states by extending `determine_recovery_state()`
- **Recovery Logic**: Customize state analysis in `analyze_incomplete_session()`

## Maintenance

### **Log File Management**
- Incomplete sessions remain in logs until completed or manually cleaned
- Recovery system automatically handles multiple incomplete sessions
- Most recent incomplete session takes priority

### **Cleanup**
- Completed sessions are finalized with `session_end_time`
- Incomplete sessions can be manually completed by adding end time to session_info.json
- Old incomplete sessions can be archived or deleted as needed

The crash recovery system ensures that technical issues don't disrupt research sessions and provides a professional, robust user experience.
