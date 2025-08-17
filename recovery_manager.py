#!/usr/bin/env python3

import os
import json
import glob
from datetime import datetime


class RecoveryManager:
    """Manages crash recovery functionality for the Moly app."""
    
    def __init__(self, logging_manager):
        self.logging_manager = logging_manager
        self.recovery_data = None
        self.is_recovering = False
    
    def check_for_incomplete_sessions(self):
        """Check for incomplete sessions that can be recovered."""
        if not os.path.exists("logs"):
            return None

        incomplete_sessions = []
        for participant_dir in os.listdir("logs"):
            participant_path = os.path.join("logs", participant_dir)
            if not os.path.isdir(participant_path):
                continue

            # Check each session for this participant
            session_files = glob.glob(os.path.join(participant_path, "session_info_*.json"))
            for session_file in session_files:
                try:
                    with open(session_file, 'r') as f:
                        session_info = json.load(f)

                    # If session doesn't have an end time, it's incomplete
                    if 'session_end_time' not in session_info:
                        recovery_data = self.analyze_incomplete_session(session_file)
                        if recovery_data:
                            incomplete_sessions.append(recovery_data)
                except Exception as e:
                    print(f"Error checking session {session_file}: {e}")

        # Return the most recent incomplete session
        if incomplete_sessions:
            return max(incomplete_sessions, key=lambda x: x['session_start_unix'])
        return None

    def analyze_incomplete_session(self, session_info_path):
        """Analyze an incomplete session to determine recovery state."""
        try:
            with open(session_info_path, 'r') as f:
                session_info = json.load(f)

            participant_id = session_info['participant_id']
            session_dir = os.path.dirname(session_info_path)

            # Load actions to determine last state
            actions_pattern = os.path.join(session_dir, "actions_*.jsonl")
            actions_files = glob.glob(actions_pattern)
            if not actions_files:
                return None

            actions = []
            with open(actions_files[0], 'r') as f:
                for line in f:
                    if line.strip():
                        actions.append(json.loads(line))

            # Sort actions by timestamp
            actions.sort(key=lambda x: x['timestamp']['unix'])

            if not actions:
                return None

            last_action = actions[-1]
            last_screen = last_action['screen']

            # Load descriptive responses if any
            responses_pattern = os.path.join(session_dir, "descriptive_responses_*.jsonl")
            responses_files = glob.glob(responses_pattern)
            responses = []
            if responses_files:
                with open(responses_files[0], 'r') as f:
                    for line in f:
                        if line.strip():
                            responses.append(json.loads(line))

            # Determine recovery state
            recovery_state = self.determine_recovery_state(actions, responses, last_screen)

            return {
                'participant_id': participant_id,
                'session_start_unix': session_info['session_start_time']['unix_timestamp'],
                'session_info_path': session_info_path,
                'session_dir': session_dir,
                'last_screen': last_screen,
                'last_action': last_action,
                'recovery_state': recovery_state,
                'actions': actions,
                'responses': responses,
                'session_info': session_info
            }

        except Exception as e:
            print(f"Error analyzing incomplete session: {e}")
            return None

    def determine_recovery_state(self, actions, responses, last_screen):
        """Determine what state to recover to based on actions."""
        # Check if user was in descriptive task
        if last_screen == "descriptive_task":
            # Find current prompt index
            screen_displayed_actions = [a for a in actions if a['action_type'] == 'SCREEN_DISPLAYED' and a['screen'] == 'descriptive_task']
            if screen_displayed_actions:
                # Count how many prompts were completed
                current_prompt_index = len(responses)
                return {
                    'screen': 'descriptive_task',
                    'current_prompt_index': current_prompt_index,
                    'completed_responses': responses
                }

        # Check other screens
        elif last_screen == "relaxation":
            return {'screen': 'relaxation'}
        elif last_screen == "stroop":
            return {'screen': 'stroop'}
        elif last_screen == "math_task":
            return {'screen': 'math_task'}
        elif last_screen == "post_study_rest":
            return {'screen': 'post_study_rest'}
        elif last_screen == "participant_id":
            return {'screen': 'participant_id'}

        # Default to beginning if unsure
        return {'screen': 'participant_id'}

    def setup_recovery_session(self, recovery_data, session_start_time_callback):
        """Set up session data from recovery."""
        # Set up participant data
        participant_id = recovery_data['participant_id']
        self.logging_manager.participant_id = participant_id
        self.logging_manager.log_dir = recovery_data['session_dir']
        self.logging_manager.session_info_file_path = recovery_data['session_info_path']

        # Set up log file paths (reuse existing files)
        timestamp = os.path.basename(recovery_data['session_info_path']).replace('session_info_', '').replace('.json', '')
        self.logging_manager.action_log_file_path = os.path.join(self.logging_manager.log_dir, f"actions_{timestamp}.jsonl")
        self.logging_manager.descriptive_response_file_path = os.path.join(self.logging_manager.log_dir, f"descriptive_responses_{timestamp}.jsonl")

        # Set session start time to original session start time for proper duration calculation
        original_start = recovery_data['session_info']['session_start_time']['unix_timestamp']
        original_session_start = datetime.fromtimestamp(original_start)
        session_start_time_callback(original_session_start)

        # Set recovery flag
        self.is_recovering = True
        self.recovery_data = recovery_data

        # Log app reopening and recovery
        self.logging_manager.log_action("APPLICATION_REOPENED", f"Application reopened after crash, resuming from {recovery_data['last_screen']} screen")
        self.logging_manager.log_action("SESSION_RESUMED", f"Resumed session from {recovery_data['last_screen']} screen")

    def restore_text_and_countdown(self, response_text_widget, update_word_count_callback, 
                                 countdown_manager, countdown_enabled):
        """Restore text for current prompt if available from previous session."""
        if not self.recovery_data or not response_text_widget:
            return

        # Look for the most recent partial text update for current prompt
        actions = self.recovery_data.get('actions', [])
        partial_text = ""
        countdown_remaining = None

        # Find the most recent partial text update for the current prompt
        current_prompt = 0  # This should be passed as parameter if needed

        for action in reversed(actions):  # Start from most recent
            if action.get('action_type') == 'PARTIAL_TEXT_UPDATE':
                details = action.get('details', {})
                if isinstance(details, dict):
                    action_prompt = details.get('current_prompt_index', 0)
                    if action_prompt == current_prompt:
                        partial_text = details.get('text_content', '')
                        countdown_remaining = details.get('countdown_remaining')
                        break
            elif action.get('action_type') == 'COUNTDOWN_STATE':
                try:
                    countdown_data = json.loads(action.get('details', '{}'))
                    if countdown_remaining is None:  # Only use if we haven't found one yet
                        countdown_remaining = countdown_data.get('remaining_seconds')
                except:
                    pass

        # Restore the text if found
        if partial_text:
            import tkinter as tk
            response_text_widget.delete('1.0', tk.END)
            response_text_widget.insert('1.0', partial_text)
            update_word_count_callback()
            print(f"🔄 Restored {len(partial_text)} characters of partial text")

            # Position cursor at end
            response_text_widget.mark_set(tk.INSERT, tk.END)
            response_text_widget.focus_set()

        # Restore countdown timer if found and countdown is enabled
        if countdown_remaining and countdown_enabled:
            try:
                if countdown_remaining > 0:
                    countdown_manager.restore_countdown_from_seconds(countdown_remaining)
                    print(f"🔄 Restored countdown: {countdown_remaining} seconds remaining")
            except Exception as e:
                print(f"⚠️ Could not restore countdown: {e}")

        return partial_text, countdown_remaining

    def reset_recovery_state(self):
        """Clear recovery state."""
        self.is_recovering = False
        self.recovery_data = None