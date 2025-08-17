#!/usr/bin/env python3

import os
import json
import time
from datetime import datetime, timezone


class LoggingManager:
    """Manages all logging functionality for the Moly app."""
    
    def __init__(self):
        self.participant_id = None
        self.log_dir = None
        self.session_start_time = datetime.now()
        
        # Log file paths
        self.session_info_file_path = None
        self.action_log_file_path = None
        self.descriptive_response_file_path = None
        self.tech_log_file_path = None
    
    def setup_logging_for_participant(self, participant_id):
        """Set up logging files for a participant."""
        self.participant_id = participant_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create log directory structure: ./logs/{participant_id}/
        self.log_dir = os.path.join("logs", participant_id)
        os.makedirs(self.log_dir, exist_ok=True)

        # Set up file paths in the organized structure
        self.session_info_file_path = os.path.join(self.log_dir, f"session_info_{timestamp}.json")
        self.action_log_file_path = os.path.join(self.log_dir, f"actions_{timestamp}.jsonl")
        self.descriptive_response_file_path = os.path.join(self.log_dir, f"descriptive_responses_{timestamp}.jsonl")
        self.tech_log_file_path = os.path.join(self.log_dir, f"tech_log_{timestamp}.jsonl")

        # Create the log files
        self.create_session_info_file()
        self.setup_action_logging()
        self.setup_descriptive_response_logging()
        self.setup_tech_logging()

    def create_session_info_file(self):
        """Create session information file with metadata."""
        try:
            from config import (DEVELOPER_MODE, FOCUS_MODE, DESCRIPTIVE_LINE_LOGGING, 
                              COUNTDOWN_ENABLED, DESCRIPTIVE_COUNTDOWN_MINUTES, 
                              STROOP_COUNTDOWN_MINUTES, MATH_COUNTDOWN_MINUTES, 
                              TASK_SELECTION_MODE)
            
            session_info = {
                "participant_id": self.participant_id,
                "session_start_time": {
                    "local": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix_timestamp": time.time()
                },
                "application_version": "1.0",
                "configuration": {
                    "developer_mode": DEVELOPER_MODE,
                    "focus_mode": FOCUS_MODE,
                    "descriptive_line_logging": DESCRIPTIVE_LINE_LOGGING,
                    "countdown_enabled": COUNTDOWN_ENABLED,
                    "descriptive_countdown_minutes": DESCRIPTIVE_COUNTDOWN_MINUTES,
                    "stroop_countdown_minutes": STROOP_COUNTDOWN_MINUTES,
                    "math_countdown_minutes": MATH_COUNTDOWN_MINUTES,
                    "task_selection_mode": TASK_SELECTION_MODE
                },
                "file_structure": {
                    "actions_log": os.path.basename(self.action_log_file_path),
                    "descriptive_responses": os.path.basename(self.descriptive_response_file_path),
                    "tech_log": os.path.basename(self.tech_log_file_path),
                    "session_info": os.path.basename(self.session_info_file_path)
                }
            }

            with open(self.session_info_file_path, 'w') as f:
                json.dump(session_info, f, indent=2)

            self.tech_print(f"📋 Session info file created: {self.session_info_file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create session info file: {e}")

    def setup_action_logging(self):
        """Initialize the action logging system with JSONL format."""
        try:
            # JSONL format doesn't need headers - each line is a complete JSON object
            # Create empty file
            with open(self.action_log_file_path, 'w'):
                pass  # Create empty file
            self.tech_print(f"📊 Action log file created: {self.action_log_file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create action log file: {e}")

    def setup_descriptive_response_logging(self):
        """Initialize the descriptive response logging system with JSONL format."""
        try:
            # JSONL format doesn't need headers - each line is a complete JSON object
            # Create empty file
            with open(self.descriptive_response_file_path, 'w'):
                pass  # Create empty file
            self.tech_print(f"📝 Descriptive response file created: {self.descriptive_response_file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create descriptive response file: {e}")

    def setup_tech_logging(self):
        """Initialize the tech logging system with JSONL format."""
        try:
            # JSONL format doesn't need headers - each line is a complete JSON object
            # Create empty file
            with open(self.tech_log_file_path, 'w'):
                pass  # Create empty file
            print(f"🔧 Tech log file created: {self.tech_log_file_path}")  # Can't use tech_print here yet
        except Exception as e:
            print(f"⚠️ Warning: Could not create tech log file: {e}")

    def log_action(self, action, details="", current_screen="unknown"):
        """Log an action with local and UTC timestamps in JSONL format."""
        if not self.action_log_file_path:
            return

        try:
            now = datetime.now()
            now_utc = datetime.now(timezone.utc)

            log_entry = {
                "timestamp": {
                    "local": now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": now_utc.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix": time.time()
                },
                "participant_id": self.participant_id,
                "action_type": action,
                "details": details,
                "screen": current_screen,
                "session_duration_seconds": (now - self.session_start_time).total_seconds()
            }

            with open(self.action_log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            print(f"📊 Action logged: {action}")
        except Exception as e:
            print(f"⚠️ Warning: Could not log action: {e}")

    def log_descriptive_response(self, prompt_index, prompt_text, response_text):
        """Log descriptive task response to file in JSONL format."""
        if not self.descriptive_response_file_path:
            return

        try:
            now = datetime.now()
            now_utc = datetime.now(timezone.utc)

            response_entry = {
                "timestamp": {
                    "local": now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": now_utc.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix": time.time()
                },
                "participant_id": self.participant_id,
                "prompt_index": prompt_index + 1,
                "prompt_text": prompt_text,
                "response_text": response_text,
                "word_count": len(response_text.split()) if response_text else 0,
                "character_count": len(response_text) if response_text else 0,
                "session_duration_seconds": (now - self.session_start_time).total_seconds()
            }

            with open(self.descriptive_response_file_path, 'a') as f:
                f.write(json.dumps(response_entry) + '\n')

            print(f"📝 Descriptive response logged for prompt {prompt_index + 1}")
        except Exception as e:
            print(f"⚠️ Warning: Could not log descriptive response: {e}")

    def log_tech_message(self, message, level="INFO", current_screen="unknown"):
        """Log technical/console messages to tech log file in JSONL format."""
        if not hasattr(self, 'tech_log_file_path') or not self.tech_log_file_path:
            return

        try:
            now = datetime.now()
            now_utc = datetime.now(timezone.utc)

            tech_entry = {
                "timestamp": {
                    "local": now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": now_utc.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix": time.time()
                },
                "participant_id": self.participant_id or 'unknown',
                "level": level,
                "message": message,
                "screen": current_screen,
                "session_duration_seconds": (now - self.session_start_time).total_seconds() if hasattr(self, 'session_start_time') else 0
            }

            with open(self.tech_log_file_path, 'a') as f:
                f.write(json.dumps(tech_entry) + '\n')

        except Exception as e:
            # Fallback to regular print if tech logging fails
            print(f"⚠️ Warning: Could not write to tech log: {e}")

    def tech_print(self, message, level="INFO", current_screen="unknown"):
        """Print message to console and log it to tech log file."""
        # Print to console
        print(message)
        
        # Log to tech log file
        self.log_tech_message(message, level, current_screen)

    def log_sentence_completion(self, sentence):
        """Log when user completes a sentence using the action logging system."""
        from config import DESCRIPTIVE_LINE_LOGGING
        
        if not DESCRIPTIVE_LINE_LOGGING:
            return

        try:
            # Use the standard action logging system with sentence-specific details
            sentence_clean = sentence.strip()
            details = {
                "sentence": sentence_clean,
                "word_count": len(sentence_clean.split()),
                "character_count": len(sentence_clean)
            }

            self.log_action("SENTENCE_COMPLETED", json.dumps(details))
            print(f"📝 Sentence logged: {sentence_clean[:50]}...")
        except Exception as e:
            print(f"⚠️ Warning: Could not log sentence: {e}")

    def add_task_selection_to_session_info(self, task_name, selection_mode, distribution_stats):
        """Add task selection metadata to session_info file."""
        try:
            if not hasattr(self, 'session_info_file_path'):
                return
                
            # Read existing session info
            with open(self.session_info_file_path, 'r') as f:
                session_info = json.load(f)
            
            # Add task selection metadata
            session_info["task_selection"] = {
                "selected_task": task_name,
                "selection_mode": selection_mode,
                "task_description": {
                    "mandala": "drawing your figure",
                    "diary": "journal down your mind", 
                    "mindfulness": "watch a fun video"
                }.get(task_name, "unknown task"),
                "selection_timestamp": {
                    "local": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix_timestamp": time.time()
                },
                "task_distribution_at_selection": distribution_stats
            }
            
            # Save updated session info
            with open(self.session_info_file_path, 'w') as f:
                json.dump(session_info, f, indent=2)
                
            print(f"📋 Task selection added to session info: {task_name} ({selection_mode})")
            
        except Exception as e:
            print(f"⚠️ Error adding task selection to session info: {e}")

    def finalize_session(self):
        """Finalize session by updating session info with end time and statistics."""
        try:
            if not hasattr(self, 'session_info_file_path'):
                return

            # Read existing session info
            with open(self.session_info_file_path, 'r') as f:
                session_info = json.load(f)

            # Add session end information
            now = datetime.now()
            session_info["session_end_time"] = {
                "local": now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "unix_timestamp": time.time()
            }
            session_info["session_duration_seconds"] = (now - self.session_start_time).total_seconds()
            session_info["session_duration_minutes"] = session_info["session_duration_seconds"] / 60

            # Write updated session info
            with open(self.session_info_file_path, 'w') as f:
                json.dump(session_info, f, indent=2)

            print(f"📋 Session finalized: {session_info['session_duration_minutes']:.2f} minutes")
        except Exception as e:
            print(f"⚠️ Warning: Could not finalize session: {e}")

    def log_screen_transition(self, screen_name, details=""):
        """Helper method to log screen transitions consistently."""
        action_details = f"Transitioning to {screen_name}"
        if details:
            action_details += f" - {details}"
        self.log_action("SCREEN_TRANSITION", action_details)

    def log_screen_displayed(self, screen_name, details=""):
        """Helper method to log when screens are fully displayed."""
        action_details = f"{screen_name} screen displayed and ready"
        if details:
            action_details += f" - {details}"
        self.log_action("SCREEN_DISPLAYED", action_details)

    def log_user_input(self, input_type, details="", current_screen="unknown"):
        """Helper method to log user inputs (key presses, button clicks, etc.)."""
        self.log_action(input_type, details, current_screen)

    def log_window_event(self, event_type, window_name, details="", current_screen="unknown"):
        """Helper method to log window-specific events."""
        action_details = f"{window_name}: {details}" if details else window_name
        self.log_action(event_type, action_details, current_screen)

    def log_partial_text(self, text_content, countdown_remaining=None, current_prompt_index=0):
        """Log partial text content for crash recovery."""
        if not self.action_log_file_path:
            return

        try:
            partial_data = {
                "timestamp": {
                    "local": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "unix": time.time()
                },
                "participant_id": self.participant_id,
                "action_type": "PARTIAL_TEXT_UPDATE",
                "details": {
                    "text_content": text_content,
                    "text_length": len(text_content),
                    "word_count": len(text_content.split()) if text_content else 0,
                    "current_prompt_index": current_prompt_index,
                    "countdown_remaining": countdown_remaining
                },
                "screen": "descriptive_task",
                "session_duration_seconds": (datetime.now() - self.session_start_time).total_seconds()
            }

            with open(self.action_log_file_path, 'a') as f:
                f.write(json.dumps(partial_data) + '\n')

        except Exception as e:
            print(f"⚠️ Error logging partial text: {e}")

    def log_countdown_state(self, countdown_remaining, countdown_total, current_screen="unknown"):
        """Log countdown timer state for recovery."""
        countdown_data = {
            "remaining_seconds": countdown_remaining,
            "total_seconds": countdown_total,
            "percentage_complete": ((countdown_total - countdown_remaining) / countdown_total * 100) if countdown_total > 0 else 0
        }
        self.log_action("COUNTDOWN_STATE", json.dumps(countdown_data), current_screen)