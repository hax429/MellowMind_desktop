#!/usr/bin/env python3
"""
Test script for Moly crash recovery system.
Creates incomplete sessions and tests recovery functionality.
"""

import os
import json
import shutil
from datetime import datetime, timezone
import time

def create_incomplete_session(participant_id, last_screen="descriptive_task", num_responses=1):
    """Create an incomplete session for testing recovery."""
    
    # Create logs directory if it doesn't exist
    logs_dir = f"logs/{participant_id}"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create session info (without end time - this makes it "incomplete")
    session_info = {
        "participant_id": participant_id,
        "session_start_time": {
            "local": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix_timestamp": time.time() - 300  # 5 minutes ago
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
    
    # Create some sample actions
    actions = []
    base_time = time.time() - 300  # 5 minutes ago
    
    # Add various actions to simulate a session
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
    
    if last_screen in ["descriptive_task", "stroop", "math_task", "post_study_rest"]:
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
    
    if last_screen in ["stroop", "math_task", "post_study_rest"]:
        actions.append({
            "timestamp": {
                "local": datetime.fromtimestamp(base_time + 120).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "utc": datetime.fromtimestamp(base_time + 120, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "unix": base_time + 120
            },
            "participant_id": participant_id,
            "action_type": "SCREEN_DISPLAYED",
            "details": "Stroop screen displayed and ready",
            "screen": "stroop",
            "session_duration_seconds": 121.0
        })
    
    # Add final screen action
    final_time = base_time + 200
    actions.append({
        "timestamp": {
            "local": datetime.fromtimestamp(final_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "utc": datetime.fromtimestamp(final_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "unix": final_time
        },
        "participant_id": participant_id,
        "action_type": "SCREEN_DISPLAYED",
        "details": f"{last_screen} screen displayed and ready",
        "screen": last_screen,
        "session_duration_seconds": 201.0
    })
    
    # Write actions
    actions_path = os.path.join(logs_dir, f"actions_{timestamp}.jsonl")
    with open(actions_path, 'w') as f:
        for action in actions:
            f.write(json.dumps(action) + '\n')
    
    # Create sample responses for descriptive task
    responses = []
    if num_responses > 0 and last_screen in ["descriptive_task", "stroop", "math_task", "post_study_rest"]:
        for i in range(num_responses):
            response_time = base_time + 60 + (i * 30)
            responses.append({
                "timestamp": {
                    "local": datetime.fromtimestamp(response_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": datetime.fromtimestamp(response_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix": response_time
                },
                "participant_id": participant_id,
                "prompt_index": i + 1,
                "prompt_text": f"Sample prompt {i + 1}",
                "response_text": f"Sample response {i + 1} with some test content.",
                "word_count": 8,
                "character_count": 45,
                "session_duration_seconds": response_time - base_time
            })
    
    # Write responses
    responses_path = os.path.join(logs_dir, f"descriptive_responses_{timestamp}.jsonl")
    with open(responses_path, 'w') as f:
        for response in responses:
            f.write(json.dumps(response) + '\n')
    
    print(f"✅ Created incomplete session for {participant_id}")
    print(f"   Last screen: {last_screen}")
    print(f"   Completed responses: {len(responses)}")
    print(f"   Session files: {logs_dir}/")
    
    return {
        'participant_id': participant_id,
        'timestamp': timestamp,
        'logs_dir': logs_dir,
        'last_screen': last_screen,
        'num_responses': len(responses)
    }

def list_incomplete_sessions():
    """List all incomplete sessions."""
    if not os.path.exists("logs"):
        print("No logs directory found.")
        return []
    
    incomplete_sessions = []
    for participant_dir in os.listdir("logs"):
        participant_path = os.path.join("logs", participant_dir)
        if not os.path.isdir(participant_path):
            continue
        
        # Check each session for this participant
        import glob
        session_files = glob.glob(os.path.join(participant_path, "session_info_*.json"))
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_info = json.load(f)
                
                # If session doesn't have an end time, it's incomplete
                if 'session_end_time' not in session_info:
                    incomplete_sessions.append({
                        'participant_id': session_info['participant_id'],
                        'session_file': session_file,
                        'start_time': session_info['session_start_time']['local']
                    })
            except Exception as e:
                print(f"Error reading {session_file}: {e}")
    
    return incomplete_sessions

def cleanup_test_sessions():
    """Remove all test sessions."""
    test_participants = ['TEST001', 'TEST002', 'TEST003', 'CRASH001', 'CRASH002']
    
    for participant in test_participants:
        participant_dir = f"logs/{participant}"
        if os.path.exists(participant_dir):
            shutil.rmtree(participant_dir)
            print(f"🗑️ Removed test session: {participant}")

def main():
    """Main test function."""
    print("🧪 Moly Crash Recovery Test Script")
    print("=" * 50)
    
    # Show current incomplete sessions
    print("\n📋 Current incomplete sessions:")
    incomplete = list_incomplete_sessions()
    if incomplete:
        for session in incomplete:
            print(f"   {session['participant_id']} - {session['start_time']}")
    else:
        print("   None found")
    
    print("\n🔧 Test Options:")
    print("1. Create incomplete session in descriptive task (2 responses completed)")
    print("2. Create incomplete session in relaxation screen")
    print("3. Create incomplete session in stroop screen")
    print("4. Create incomplete session in math task")
    print("5. Clean up test sessions")
    print("6. List all incomplete sessions")
    print("7. Run Moly app to test recovery")
    
    choice = input("\nEnter choice (1-7): ").strip()
    
    if choice == '1':
        create_incomplete_session("TEST001", "descriptive_task", 2)
        print("\n💡 Now run 'python moly_app.py' to test recovery!")
        
    elif choice == '2':
        create_incomplete_session("TEST002", "relaxation", 0)
        print("\n💡 Now run 'python moly_app.py' to test recovery!")
        
    elif choice == '3':
        create_incomplete_session("TEST003", "stroop", 3)
        print("\n💡 Now run 'python moly_app.py' to test recovery!")
        
    elif choice == '4':
        create_incomplete_session("CRASH001", "math_task", 5)
        print("\n💡 Now run 'python moly_app.py' to test recovery!")
        
    elif choice == '5':
        cleanup_test_sessions()
        print("\n✅ Test sessions cleaned up!")
        
    elif choice == '6':
        print("\n📋 All incomplete sessions:")
        incomplete = list_incomplete_sessions()
        if incomplete:
            for session in incomplete:
                print(f"   📁 {session['participant_id']}")
                print(f"      Started: {session['start_time']}")
                print(f"      File: {session['session_file']}")
                print()
        else:
            print("   None found")
            
    elif choice == '7':
        print("\n🚀 Starting Moly app...")
        os.system("python moly_app.py")
        
    else:
        print("❌ Invalid choice")

if __name__ == '__main__':
    main()
