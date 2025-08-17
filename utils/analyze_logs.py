#!/usr/bin/env python3
"""
Moly Log Analysis Tool
Provides easy analysis of Moly session logs in the new JSON format.
"""

import json
import glob
import os
from datetime import datetime
from collections import Counter
import argparse

def load_session_info(participant_id):
    """Load session info for a participant."""
    pattern = f'logs/{participant_id}/session_info_*.json'
    files = glob.glob(pattern)
    if not files:
        return None
    
    with open(files[0], 'r') as f:
        return json.load(f)

def load_actions(participant_id):
    """Load all actions for a participant."""
    actions = []
    pattern = f'logs/{participant_id}/actions_*.jsonl'
    for file_path in glob.glob(pattern):
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    actions.append(json.loads(line))
    return sorted(actions, key=lambda x: x['timestamp']['unix'])

def load_responses(participant_id):
    """Load all descriptive responses for a participant."""
    responses = []
    pattern = f'logs/{participant_id}/descriptive_responses_*.jsonl'
    for file_path in glob.glob(pattern):
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    responses.append(json.loads(line))
    return sorted(responses, key=lambda x: x['timestamp']['unix'])

def load_tech_logs(participant_id):
    """Load all tech log entries for a participant."""
    tech_logs = []
    pattern = f'logs/{participant_id}/tech_log_*.jsonl'
    for file_path in glob.glob(pattern):
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    tech_logs.append(json.loads(line))
    return sorted(tech_logs, key=lambda x: x['timestamp']['unix'])

def analyze_session_overview(participant_id):
    """Provide session overview."""
    session_info = load_session_info(participant_id)
    if not session_info:
        print(f"No session info found for participant {participant_id}")
        return
    
    print(f"\n=== SESSION OVERVIEW: {participant_id} ===")
    print(f"Session Duration: {session_info['session_duration_minutes']:.2f} minutes")
    print(f"Start Time: {session_info['session_start_time']['local']}")
    print(f"End Time: {session_info['session_end_time']['local']}")
    
    config = session_info['configuration']
    print(f"\nConfiguration:")
    print(f"  Developer Mode: {config['developer_mode']}")
    print(f"  Countdown Enabled: {config['countdown_enabled']}")
    print(f"  Line Logging: {config['descriptive_line_logging']}")
    print(f"  Task Selection Mode: {config.get('task_selection_mode', 'not specified')}")
    
    # Task Selection Information
    if 'task_selection' in session_info:
        task_sel = session_info['task_selection']
        print(f"\nTask Selection:")
        print(f"  Selected Task: {task_sel['selected_task']} ({task_sel['task_description']})")
        print(f"  Selection Mode: {task_sel['selection_mode']}")
        print(f"  Selection Time: {task_sel['selection_timestamp']['local']}")
        
        # Distribution stats
        dist = task_sel['task_distribution_at_selection']
        print(f"  Distribution at Selection:")
        print(f"    Total Participants: {dist['total_assignments']}")
        print(f"    Mandala: {dist['mandala_count']} ({dist['mandala_percent']}%)")
        print(f"    Diary: {dist['diary_count']} ({dist['diary_percent']}%)")
        print(f"    Mindfulness: {dist['mindfulness_count']} ({dist['mindfulness_percent']}%)")
    else:
        print(f"\nTask Selection: Not available (older session or task not selected yet)")

def analyze_actions(participant_id):
    """Analyze user actions."""
    actions = load_actions(participant_id)
    if not actions:
        print(f"No actions found for participant {participant_id}")
        return
    
    print(f"\n=== ACTION ANALYSIS: {participant_id} ===")
    print(f"Total Actions: {len(actions)}")
    
    # Action type frequency
    action_types = Counter(action['action_type'] for action in actions)
    print(f"\nAction Type Frequency:")
    for action_type, count in action_types.most_common():
        print(f"  {action_type}: {count}")
    
    # Screen transitions
    screen_transitions = [a for a in actions if a['action_type'] == 'SCREEN_TRANSITION']
    print(f"\nScreen Transitions ({len(screen_transitions)}):")
    for transition in screen_transitions:
        print(f"  {transition['timestamp']['local']}: {transition['details']}")
    
    # Sentence completions
    sentences = [a for a in actions if a['action_type'] == 'SENTENCE_COMPLETED']
    if sentences:
        print(f"\nSentence Completions ({len(sentences)}):")
        for sentence in sentences:
            details = json.loads(sentence['details'])
            print(f"  {sentence['timestamp']['local']}: \"{details['sentence']}\"")

def analyze_responses(participant_id):
    """Analyze descriptive responses."""
    responses = load_responses(participant_id)
    if not responses:
        print(f"No responses found for participant {participant_id}")
        return
    
    print(f"\n=== RESPONSE ANALYSIS: {participant_id} ===")
    print(f"Total Responses: {len(responses)}")
    
    total_words = sum(r['word_count'] for r in responses)
    total_chars = sum(r['character_count'] for r in responses)
    avg_words = total_words / len(responses) if responses else 0
    avg_chars = total_chars / len(responses) if responses else 0
    
    print(f"Total Words: {total_words}")
    print(f"Average Words per Response: {avg_words:.1f}")
    print(f"Average Characters per Response: {avg_chars:.1f}")
    
    print(f"\nDetailed Responses:")
    for response in responses:
        print(f"  Prompt {response['prompt_index']}: {response['word_count']} words")
        print(f"    \"{response['response_text'][:100]}...\"")
        print(f"    Time: {response['timestamp']['local']}")

def analyze_timing(participant_id):
    """Analyze timing between events."""
    actions = load_actions(participant_id)
    if len(actions) < 2:
        print(f"Not enough actions for timing analysis")
        return
    
    print(f"\n=== TIMING ANALYSIS: {participant_id} ===")
    
    # Time between screen transitions
    screen_displays = [a for a in actions if a['action_type'] == 'SCREEN_DISPLAYED']
    if len(screen_displays) > 1:
        print(f"Time spent on each screen:")
        for i in range(len(screen_displays) - 1):
            current = screen_displays[i]
            next_screen = screen_displays[i + 1]
            time_diff = next_screen['timestamp']['unix'] - current['timestamp']['unix']
            print(f"  {current['screen']}: {time_diff:.1f} seconds")

def analyze_tech_logs(participant_id):
    """Analyze technical logs and system messages."""
    tech_logs = load_tech_logs(participant_id)
    if not tech_logs:
        print(f"No tech logs found for participant {participant_id}")
        return
    
    print(f"\n=== TECHNICAL LOGS: {participant_id} ===")
    print(f"Total Tech Log Entries: {len(tech_logs)}")
    
    # Count by log level
    levels = Counter(log['level'] for log in tech_logs)
    print(f"\nLog Level Distribution:")
    for level, count in levels.most_common():
        print(f"  {level}: {count}")
    
    # Count by screen
    screens = Counter(log['screen'] for log in tech_logs)
    print(f"\nTech Messages by Screen:")
    for screen, count in screens.most_common():
        print(f"  {screen}: {count}")
    
    # Show recent tech messages
    print(f"\nRecent Technical Messages:")
    recent_logs = tech_logs[-10:]  # Last 10 entries
    for log in recent_logs:
        time_str = log['timestamp']['local']
        level = log['level']
        screen = log['screen']
        message = log['message']
        print(f"  {time_str} [{level}] ({screen}): {message}")
    
    # Show errors and warnings if any
    errors_warnings = [log for log in tech_logs if log['level'] in ['ERROR', 'WARN', 'WARNING']]
    if errors_warnings:
        print(f"\nErrors and Warnings ({len(errors_warnings)}):")
        for log in errors_warnings:
            time_str = log['timestamp']['local']
            level = log['level']
            message = log['message']
            print(f"  {time_str} [{level}]: {message}")

def analyze_task_selection(participant_id):
    """Analyze task selection data across all participants."""
    print(f"\n=== TASK SELECTION ANALYSIS: {participant_id} ===")
    
    # Individual participant task selection
    session_info = load_session_info(participant_id)
    if not session_info:
        print(f"No session info found for participant {participant_id}")
        return
    
    if 'task_selection' not in session_info:
        print(f"No task selection data found for participant {participant_id}")
        return
    
    task_sel = session_info['task_selection']
    print(f"This Participant:")
    print(f"  Task: {task_sel['selected_task']} ({task_sel['task_description']})")
    print(f"  Mode: {task_sel['selection_mode']}")
    print(f"  Selected at: {task_sel['selection_timestamp']['local']}")
    
    # Overall distribution at time of selection
    dist = task_sel['task_distribution_at_selection']
    print(f"\nOverall Distribution at Time of Selection:")
    print(f"  Total Participants: {dist['total_assignments']}")
    print(f"  Mandala: {dist['mandala_count']} participants ({dist['mandala_percent']}%)")
    print(f"  Diary: {dist['diary_count']} participants ({dist['diary_percent']}%)")
    print(f"  Mindfulness: {dist['mindfulness_count']} participants ({dist['mindfulness_percent']}%)")
    
    # Load current overall distribution
    try:
        import json
        with open('/Users/hax429/Developer/Internship/moly/task_assignments.json', 'r') as f:
            data = json.load(f)
        
        assignments = data.get("assignments", {})
        total_current = len(assignments)
        
        if total_current > 0:
            task_counts = {"mandala": 0, "diary": 0, "mindfulness": 0}
            for task in assignments.values():
                if task in task_counts:
                    task_counts[task] += 1
            
            print(f"\nCurrent Overall Distribution:")
            print(f"  Total Participants: {total_current}")
            for task, count in task_counts.items():
                percent = round((count / total_current) * 100, 1) if total_current > 0 else 0
                print(f"  {task.capitalize()}: {count} participants ({percent}%)")
        
    except Exception as e:
        print(f"\nCould not load current distribution: {e}")
    
    # Show task selection related actions
    actions = load_actions(participant_id)
    task_actions = [a for a in actions if 'TASK' in a['action_type']]
    
    if task_actions:
        print(f"\nTask Selection Actions:")
        for action in task_actions:
            print(f"  {action['timestamp']['local']}: {action['action_type']} - {action['details']}")

def list_participants():
    """List all available participants."""
    if not os.path.exists('logs'):
        print("No logs directory found")
        return []
    
    participants = [d for d in os.listdir('logs') if os.path.isdir(os.path.join('logs', d))]
    return participants

def main():
    parser = argparse.ArgumentParser(description='Analyze Moly session logs')
    parser.add_argument('participant_id', nargs='?', help='Participant ID to analyze')
    parser.add_argument('--list', action='store_true', help='List available participants')
    parser.add_argument('--overview', action='store_true', help='Show session overview only')
    parser.add_argument('--actions', action='store_true', help='Show actions analysis only')
    parser.add_argument('--responses', action='store_true', help='Show responses analysis only')
    parser.add_argument('--timing', action='store_true', help='Show timing analysis only')
    parser.add_argument('--tasks', action='store_true', help='Show task selection analysis only')
    parser.add_argument('--tech', action='store_true', help='Show technical logs analysis only')
    
    args = parser.parse_args()
    
    if args.list:
        participants = list_participants()
        if participants:
            print("Available participants:")
            for p in participants:
                print(f"  {p}")
        else:
            print("No participants found in logs directory")
        return
    
    if not args.participant_id:
        participants = list_participants()
        if participants:
            print("Available participants:")
            for p in participants:
                print(f"  {p}")
            print("\nUsage: python analyze_logs.py <participant_id>")
            print("Options: --overview, --actions, --responses, --timing, --tasks, --tech")
        else:
            print("No participants found. Run the Moly app to generate logs.")
        return
    
    # Run specific analyses or all if none specified
    if not any([args.overview, args.actions, args.responses, args.timing, args.tasks, args.tech]):
        # Run all analyses
        analyze_session_overview(args.participant_id)
        analyze_task_selection(args.participant_id)
        analyze_tech_logs(args.participant_id)
        analyze_actions(args.participant_id)
        analyze_responses(args.participant_id)
        analyze_timing(args.participant_id)
    else:
        if args.overview:
            analyze_session_overview(args.participant_id)
        if args.tasks:
            analyze_task_selection(args.participant_id)
        if args.tech:
            analyze_tech_logs(args.participant_id)
        if args.actions:
            analyze_actions(args.participant_id)
        if args.responses:
            analyze_responses(args.participant_id)
        if args.timing:
            analyze_timing(args.participant_id)

if __name__ == '__main__':
    main()
