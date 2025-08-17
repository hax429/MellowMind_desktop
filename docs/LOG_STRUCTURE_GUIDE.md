# Moly Optimized Log Structure Guide

## Overview
The Moly application now uses an optimized, searchable log structure with organized folders and JSON/JSONL formats for easy querying and analysis.

## Directory Structure
```
logs/
└── {participant_id}/
    ├── session_info_{timestamp}.json      # Session metadata and configuration
    ├── actions_{timestamp}.jsonl          # All user actions and system events
    └── descriptive_responses_{timestamp}.jsonl  # User responses to descriptive prompts
```

## File Formats

### 1. Session Info File (`session_info_{timestamp}.json`)
**Format**: Single JSON object with complete session metadata
**Purpose**: Quick session overview and configuration reference

```json
{
  "participant_id": "MA001",
  "session_start_time": {
    "local": "2025-08-13 15:07:08.253",
    "utc": "2025-08-13 19:07:08.253",
    "unix_timestamp": 1755112028.253912
  },
  "session_end_time": {
    "local": "2025-08-13 15:07:52.227",
    "utc": "2025-08-13 19:07:52.227",
    "unix_timestamp": 1755112072.2274282
  },
  "session_duration_seconds": 48.656395,
  "session_duration_minutes": 0.8109399166666668,
  "application_version": "1.0",
  "configuration": {
    "developer_mode": false,
    "focus_mode": true,
    "descriptive_line_logging": true,
    "countdown_enabled": true,
    "descriptive_countdown_minutes": 5,
    "stroop_countdown_minutes": 3,
    "math_countdown_minutes": 2
  },
  "file_structure": {
    "actions_log": "actions_20250813_150708.jsonl",
    "descriptive_responses": "descriptive_responses_20250813_150708.jsonl",
    "session_info": "session_info_20250813_150708.json"
  }
}
```

### 2. Actions Log File (`actions_{timestamp}.jsonl`)
**Format**: JSON Lines (one JSON object per line)
**Purpose**: All user interactions and system events with precise timing

```json
{
  "timestamp": {
    "local": "2025-08-13 15:07:08.254",
    "utc": "2025-08-13 19:07:08.254",
    "unix": 1755112028.254893
  },
  "participant_id": "MA001",
  "action_type": "PARTICIPANT_ID_SUBMITTED",
  "details": "Participant ID: MA001",
  "screen": "participant_id",
  "session_duration_seconds": 4.683836
}
```

**Action Types Include**:
- `PARTICIPANT_ID_SUBMITTED`
- `SCREEN_TRANSITION`
- `SCREEN_DISPLAYED`
- `TRANSITION_SCREEN_DISPLAYED`
- `TRANSITION_CONFIRMED`
- `KEY_PRESS`
- `BUTTON_PRESS`
- `FONT_CHANGE`
- `SENTENCE_COMPLETED`
- `APPLICATION_EXIT`

### 3. Descriptive Responses File (`descriptive_responses_{timestamp}.jsonl`)
**Format**: JSON Lines (one JSON object per line)
**Purpose**: User responses to descriptive task prompts with analytics

```json
{
  "timestamp": {
    "local": "2025-08-13 15:07:40.791",
    "utc": "2025-08-13 19:07:40.791",
    "unix": 1755112060.791285
  },
  "participant_id": "MA001",
  "prompt_index": 1,
  "prompt_text": "Describe the colors you see around you in detail",
  "response_text": "You can put your text here. It will log sentences as well.",
  "word_count": 19,
  "character_count": 95,
  "session_duration_seconds": 37.220233
}
```

## Querying and Analysis

### Using Command Line Tools

**1. Find all button presses:**
```bash
grep '"action_type": "BUTTON_PRESS"' logs/MA001/actions_*.jsonl
```

**2. Extract all screen transitions:**
```bash
grep '"action_type": "SCREEN_TRANSITION"' logs/MA001/actions_*.jsonl | jq '.details'
```

**3. Calculate time spent on each screen:**
```bash
grep '"action_type": "SCREEN_DISPLAYED"' logs/MA001/actions_*.jsonl | jq '{screen: .screen, time: .timestamp.local}'
```

**4. Get all sentence completions:**
```bash
grep '"action_type": "SENTENCE_COMPLETED"' logs/MA001/actions_*.jsonl | jq -r '.details | fromjson | .sentence'
```

**5. Analyze response word counts:**
```bash
jq '.word_count' logs/MA001/descriptive_responses_*.jsonl
```

### Using Python for Analysis

```python
import json
import glob
from datetime import datetime

def load_actions(participant_id):
    """Load all actions for a participant."""
    actions = []
    for file_path in glob.glob(f'logs/{participant_id}/actions_*.jsonl'):
        with open(file_path, 'r') as f:
            for line in f:
                actions.append(json.loads(line))
    return actions

def load_responses(participant_id):
    """Load all descriptive responses for a participant."""
    responses = []
    for file_path in glob.glob(f'logs/{participant_id}/descriptive_responses_*.jsonl'):
        with open(file_path, 'r') as f:
            for line in f:
                responses.append(json.loads(line))
    return responses

def load_session_info(participant_id):
    """Load session info for a participant."""
    for file_path in glob.glob(f'logs/{participant_id}/session_info_*.json'):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

# Example usage
actions = load_actions('MA001')
screen_transitions = [a for a in actions if a['action_type'] == 'SCREEN_TRANSITION']
button_presses = [a for a in actions if a['action_type'] == 'BUTTON_PRESS']

responses = load_responses('MA001')
total_words = sum(r['word_count'] for r in responses)
```

## Benefits of New Structure

### 1. **Organized Storage**
- Each participant has their own folder
- Clear file naming convention
- Easy to archive and backup

### 2. **Easy Querying**
- JSON/JSONL format works with standard tools (jq, Python, etc.)
- Each log entry is self-contained
- Consistent field names across all entries

### 3. **Rich Metadata**
- Multiple timestamp formats (local, UTC, Unix)
- Session duration tracking
- Configuration snapshot
- Automatic word/character counts

### 4. **Scalable Analysis**
- Stream processing friendly (JSONL)
- Database import ready
- Works with big data tools

### 5. **Research Friendly**
- Precise millisecond timing
- Complete session context
- Easy statistical analysis
- Export to CSV/Excel possible

## Migration from Old Format

The old text-based log files have been replaced with:
- ❌ `{participant}_{timestamp}.log` (empty legacy file)
- ❌ `{participant}_{timestamp}_actions.log` (text format)
- ❌ `{participant}_{timestamp}_descriptive_responses.txt` (text format)

**New structure:**
- ✅ `logs/{participant}/session_info_{timestamp}.json`
- ✅ `logs/{participant}/actions_{timestamp}.jsonl`
- ✅ `logs/{participant}/descriptive_responses_{timestamp}.jsonl`

## Example Queries

### Time Analysis
```bash
# Average session duration
jq -r '.session_duration_minutes' logs/*/session_info_*.json | awk '{sum+=$1; count++} END {print "Average:", sum/count, "minutes"}'

# Time between screen transitions
grep '"action_type": "SCREEN_TRANSITION"' logs/MA001/actions_*.jsonl | jq '.timestamp.unix' | awk 'NR>1{print $1-prev} {prev=$1}'
```

### User Behavior
```bash
# Most common actions
grep '"action_type"' logs/MA001/actions_*.jsonl | jq -r '.action_type' | sort | uniq -c | sort -nr

# Sentence completion frequency
grep '"action_type": "SENTENCE_COMPLETED"' logs/MA001/actions_*.jsonl | wc -l
```

### Response Analysis
```bash
# Average response length
jq -r '.word_count' logs/MA001/descriptive_responses_*.jsonl | awk '{sum+=$1; count++} END {print "Average words:", sum/count}'

# Response time analysis
jq -r '"\(.prompt_index) \(.word_count)"' logs/MA001/descriptive_responses_*.jsonl
```

This optimized structure makes the Moly logs much more powerful for research analysis while maintaining all the detailed timing information needed for behavioral studies.
