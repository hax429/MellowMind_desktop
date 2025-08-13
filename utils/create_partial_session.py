#!/usr/bin/env python3
"""
Create a test session with partial text and countdown state for recovery testing.
"""

import os
import json
import time
from datetime import datetime, timezone

def create_session_with_partial_text():
    """Create a session with partial text and countdown state."""
    
    participant_id = "RECOVERY_TEST"
    logs_dir = f"logs/{participant_id}"
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_time = time.time() - 120  # 2 minutes ago
    
    # Create session info (incomplete)
    session_info = {
        "participant_id": participant_id,
        "session_start_time": {
            "local": datetime.fromtimestamp(base_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.fromtimestamp(base_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix_timestamp": base_time
        },
        "application_version": "1.0",
        "configuration": {
            "developer_mode": False,
            "focus_mode": True,
            "descriptive_line_logging": True,
            "countdown_enabled": True,
            "descriptive_countdown_minutes": 5,
            "stroop_countdown_minutes": 3,
            "math_countdown_minutes": 2
        },
        "file_structure": {
            "actions_log": f"actions_{timestamp}.jsonl",
            "descriptive_responses": f"descriptive_responses_{timestamp}.jsonl",
            "session_info": f"session_info_{timestamp}.json"
        }
    }
    
    # Write session info
    session_info_path = os.path.join(logs_dir, f"session_info_{timestamp}.json")
    with open(session_info_path, 'w') as f:
        json.dump(session_info, f, indent=2)
    
    # Create actions with partial text updates
    actions = []
    
    # Initial actions
    actions.append({
        "timestamp": {
            "local": datetime.fromtimestamp(base_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.fromtimestamp(base_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix": base_time
        },
        "participant_id": participant_id,
        "action_type": "PARTICIPANT_ID_SUBMITTED",
        "details": f"Participant ID: {participant_id}",
        "screen": "participant_id",
        "session_duration_seconds": 1.0
    })
    
    # Relaxation screen
    actions.append({
        "timestamp": {
            "local": datetime.fromtimestamp(base_time + 10).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.fromtimestamp(base_time + 10, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix": base_time + 10
        },
        "participant_id": participant_id,
        "action_type": "SCREEN_DISPLAYED",
        "details": "Relaxation screen displayed and ready",
        "screen": "relaxation",
        "session_duration_seconds": 11.0
    })
    
    # Descriptive task start
    actions.append({
        "timestamp": {
            "local": datetime.fromtimestamp(base_time + 30).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.fromtimestamp(base_time + 30, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix": base_time + 30
        },
        "participant_id": participant_id,
        "action_type": "SCREEN_DISPLAYED",
        "details": "Descriptive task screen displayed and ready",
        "screen": "descriptive_task",
        "session_duration_seconds": 31.0
    })
    
    # Countdown state (3 minutes remaining)
    actions.append({
        "timestamp": {
            "local": datetime.fromtimestamp(base_time + 35).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.fromtimestamp(base_time + 35, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix": base_time + 35
        },
        "participant_id": participant_id,
        "action_type": "COUNTDOWN_STATE",
        "details": json.dumps({
            "remaining_seconds": 180,
            "total_seconds": 300,
            "percentage_complete": 40.0
        }),
        "screen": "descriptive_task",
        "session_duration_seconds": 36.0
    })
    
    # Partial text updates (simulating user typing)
    partial_texts = [
        "The image shows",
        "The image shows a beautiful",
        "The image shows a beautiful landscape with mountains",
        "The image shows a beautiful landscape with mountains and a lake. The colors are",
        "The image shows a beautiful landscape with mountains and a lake. The colors are vibrant and the scene appears peaceful"
    ]
    
    for i, text in enumerate(partial_texts):
        text_time = base_time + 40 + (i * 15)  # Every 15 seconds
        countdown_remaining = 180 - (i * 15)  # Countdown decreases
        
        actions.append({
            "timestamp": {
                "local": datetime.fromtimestamp(text_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "utc": datetime.fromtimestamp(text_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "unix": text_time
            },
            "participant_id": participant_id,
            "action_type": "PARTIAL_TEXT_UPDATE",
            "details": {
                "text_content": text,
                "text_length": len(text),
                "word_count": len(text.split()),
                "current_prompt_index": 0,
                "countdown_remaining": countdown_remaining
            },
            "screen": "descriptive_task",
            "session_duration_seconds": text_time - base_time
        })
    
    # Write actions
    actions_path = os.path.join(logs_dir, f"actions_{timestamp}.jsonl")
    with open(actions_path, 'w') as f:
        for action in actions:
            f.write(json.dumps(action) + '\n')
    
    # Create empty responses file (no completed responses yet)
    responses_path = os.path.join(logs_dir, f"descriptive_responses_{timestamp}.jsonl")
    with open(responses_path, 'w') as f:
        pass  # Empty file
    
    print(f"✅ Created recovery test session: {participant_id}")
    print(f"   📝 Partial text: '{partial_texts[-1][:50]}...'")
    print(f"   ⏱️ Countdown remaining: {countdown_remaining} seconds")
    print(f"   📁 Files in: {logs_dir}/")
    
    return {
        'participant_id': participant_id,
        'partial_text': partial_texts[-1],
        'countdown_remaining': countdown_remaining,
        'logs_dir': logs_dir
    }

if __name__ == '__main__':
    result = create_session_with_partial_text()
    print(f"\n💡 Now run 'python moly_app.py' to test text and countdown recovery!")
    print(f"   Expected: Text should restore to: '{result['partial_text']}'")
    print(f"   Expected: Countdown should show: {result['countdown_remaining']} seconds remaining")
