#!/usr/bin/env python3
"""
Debug script to test the recovery system detection logic.
"""

import os
import json
import glob
from datetime import datetime, timezone

def debug_recovery_detection():
    """Debug the recovery detection logic."""
    print("🔍 Debug: Recovery Detection")
    print("=" * 40)
    
    if not os.path.exists("logs"):
        print("❌ No logs directory found")
        return
    
    incomplete_sessions = []
    
    for participant_dir in os.listdir("logs"):
        participant_path = os.path.join("logs", participant_dir)
        if not os.path.isdir(participant_path):
            continue
        
        print(f"\n📁 Checking participant: {participant_dir}")
        
        # Check each session for this participant
        session_files = glob.glob(os.path.join(participant_path, "session_info_*.json"))
        print(f"   Found {len(session_files)} session files")
        
        for session_file in session_files:
            print(f"   📄 Checking: {os.path.basename(session_file)}")
            try:
                with open(session_file, 'r') as f:
                    session_info = json.load(f)
                
                # Check if session has end time
                has_end_time = 'session_end_time' in session_info
                print(f"      Has end time: {has_end_time}")
                
                if not has_end_time:
                    print(f"      ✅ INCOMPLETE SESSION DETECTED")
                    
                    # Try to analyze it like the app does
                    recovery_data = analyze_incomplete_session(session_file)
                    if recovery_data:
                        incomplete_sessions.append(recovery_data)
                        print(f"      📊 Recovery data created successfully")
                        print(f"      📍 Last screen: {recovery_data['last_screen']}")
                    else:
                        print(f"      ❌ Failed to create recovery data")
                else:
                    print(f"      ✅ Complete session")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Total incomplete sessions found: {len(incomplete_sessions)}")
    
    if incomplete_sessions:
        # Get most recent
        most_recent = max(incomplete_sessions, key=lambda x: x['session_start_unix'])
        print(f"   Most recent incomplete session:")
        print(f"   📋 Participant: {most_recent['participant_id']}")
        print(f"   📅 Started: {datetime.fromtimestamp(most_recent['session_start_unix']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📍 Last screen: {most_recent['last_screen']}")
    
    return incomplete_sessions

def analyze_incomplete_session(session_info_path):
    """Analyze an incomplete session (simplified version of app logic)."""
    try:
        with open(session_info_path, 'r') as f:
            session_info = json.load(f)
        
        participant_id = session_info['participant_id']
        session_dir = os.path.dirname(session_info_path)
        
        # Load actions to determine last state
        actions_pattern = os.path.join(session_dir, "actions_*.jsonl")
        actions_files = glob.glob(actions_pattern)
        if not actions_files:
            print(f"      ❌ No actions file found")
            return None
        
        actions = []
        with open(actions_files[0], 'r') as f:
            for line in f:
                if line.strip():
                    actions.append(json.loads(line))
        
        if not actions:
            print(f"      ❌ No actions found")
            return None
        
        # Sort actions by timestamp
        actions.sort(key=lambda x: x['timestamp']['unix'])
        last_action = actions[-1]
        last_screen = last_action['screen']
        
        print(f"      📊 Found {len(actions)} actions")
        print(f"      📍 Last action: {last_action['action_type']}")
        print(f"      📍 Last screen: {last_screen}")
        
        return {
            'participant_id': participant_id,
            'session_start_unix': session_info['session_start_time']['unix_timestamp'],
            'session_info_path': session_info_path,
            'session_dir': session_dir,
            'last_screen': last_screen,
            'last_action': last_action,
            'actions': actions,
            'session_info': session_info
        }
        
    except Exception as e:
        print(f"      ❌ Error analyzing session: {e}")
        return None

if __name__ == '__main__':
    debug_recovery_detection()
