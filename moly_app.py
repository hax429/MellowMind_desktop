#!/usr/bin/env python3

import tkinter as tk
import threading
import time
import random
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime, timezone
import json
import glob
import signal
import atexit

# ========================================
# CONFIGURATION SECTION - MODIFY AS NEEDED
# ========================================

# APPLICATION SETTINGS
APP_TITLE = "Moly"
BACKGROUND_COLOR = '#220000'  # Dark red background for stress
MAIN_FRAME_COLOR = '#220000'  # Main container color

# MODE SETTINGS
DEVELOPER_MODE = True   # Show instructions (Press N for next prompt, etc.)
FOCUS_MODE = True      # Keep window always on top and maintain focus

# TASK SELECTION MODE
# Options: "self_selection" or "random_assigned"
TASK_SELECTION_MODE = "random_assigned"  # Choose between self selection and random assignment

# LOGGING SETTINGS
DESCRIPTIVE_LINE_LOGGING = True  # Log sentences when user types "." in descriptive task

# RELAXATION SCREEN SETTINGS
SHOW_RELAXATION_TEXT = True  # Whether to show text overlay on relaxation screen
RELAXATION_TEXT = "Please Relax"  # Text to display on relaxation screen
RELAXATION_VIDEO_PATH = "/Users/hax429/Developer/test/MellowMind_desktop/res/screen.mkv"

# COUNTDOWN TIMER SETTINGS
# Global countdown toggle (master switch)
COUNTDOWN_ENABLED = True

# Individual screen countdown toggles
DESCRIPTIVE_COUNTDOWN_ENABLED = True
STROOP_COUNTDOWN_ENABLED = True
MATH_COUNTDOWN_ENABLED = True

# Countdown durations (in minutes)
DESCRIPTIVE_COUNTDOWN_MINUTES = 1
STROOP_COUNTDOWN_MINUTES = 1
MATH_COUNTDOWN_MINUTES = 1
RELAXATION_COUNTDOWN_MINUTES = 1  # Hidden countdown for automatic transition

# DESCRIPTIVE TASK SETTINGS
DESCRIPTIVE_PROMPTS = [
    "Describe the colors you see around you in detail",
    "Notice five things you can hear right now",
    "Describe the texture of three objects within reach",
    "Name three scents you can detect in this moment",
    "Describe the temperature and feeling of the air on your skin",
    "List five things you are grateful for today",
    "Describe your breathing pattern in detail",
    "Notice the position of your body and how it feels",
    "Describe the lighting in your environment",
    "Think of a peaceful place and describe it in detail"
]

# STROOP SCREEN SETTINGS
STROOP_VIDEO_PATH = "/Users/hax429/Developer/test/MellowMind_desktop/res/stroop.mov"

# MATH TASK SETTINGS
MATH_STARTING_NUMBER = 4000
MATH_SUBTRACTION_VALUE = 7
MATH_INSTRUCTION_TEXT = "Please subtract 7s from 4000, and say it aloud"

# CONTENT PERFORMANCE TASK SETTINGS
CONTENT_PERFORMANCE_TEXT = "Follow the instructions by the instructor and finish your task on Samsung phone"
CONTENT_PERFORMANCE_BG_COLOR = '#2E5A87'  # Darker blue for content performance screen

# COLOR SCHEME
COLORS = {
    'title': '#ff4444',           # Bright red for titles
    'warning': '#ff6666',         # Red for warnings
    'text_primary': 'white',      # Primary text color
    'text_secondary': '#aa6666',  # Secondary text color
    'text_accent': '#ffaa44',     # Accent text color
    'button_bg': '#ff4444',       # Button background
    'button_active': '#aa0000',   # Button active state
    'notification_bg': '#440000', # Notification background
    'countdown_normal': '#ffaa44', # Countdown normal state
    'countdown_warning': '#ff6666', # Countdown warning state
    'countdown_critical': '#ff0000' # Countdown critical state
}

# TRANSITION SCREEN SETTINGS
TRANSITION_INSTRUCTION_TEXT = "Please listen carefully for the instructor on how to proceed to the next part."

# TRANSITION MESSAGES (content shown on transition screens)
TRANSITION_MESSAGES = {
    'descriptive': "You are entering the DESCRIPTIVE TASK evaluation phase. Your responses will be evaluated for accuracy and detail. Performance is being monitored.",
    'stroop': "You are now entering the stroop VIDEO evaluation phase. Your attention and responses are being monitored closely.",
    'math': "You are now in the MATH TASK evaluation phase. Your mathematical performance is being assessed. Say your answers aloud.",
    'post_study_rest': "Evaluation complete. You are now entering the POST-STUDY REST phase. Please relax and allow yourself to decompress from the evaluation tasks."
}

# ========================================
# END CONFIGURATION SECTION
# ========================================

class MolyApp:
    """
    Unified Moly relaxation application with multiple screens.
    Handles transitions between relaxation, descriptive tasks, and video screens.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # Apply focus mode settings
        if FOCUS_MODE:
            self.root.attributes('-topmost', True)
            self.root.attributes('-fullscreen', True)
            self.root.focus_force()
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        
        # Common properties
        self.current_screen = "participant_id"
        self.running = True
        
        # Participant tracking
        self.participant_id = None
        self.log_file_path = None

        # Logging system
        self.action_log_file_path = None
        self.descriptive_response_file_path = None
        self.session_start_time = datetime.now()
        self.last_sentence_position = 0  # Track position for sentence logging

        # Crash recovery system
        self.recovery_data = None
        self.is_recovering = False
        self.keystroke_buffer = ""  # Buffer for partial text logging
        
        # Video properties (for relaxation and stroop screens)
        self.relaxation_video = RELAXATION_VIDEO_PATH
        self.stroop_video = STROOP_VIDEO_PATH
        self.cap = None
        self.video_frame = None
        
        # Text display toggle
        self.show_text = SHOW_RELAXATION_TEXT
        
        # Descriptive task properties
        self.current_prompt_index = 0
        self.prompts = DESCRIPTIVE_PROMPTS
        
        # stroop properties
        self.is_playing = False
        self.is_paused = False
        
        # Math task properties
        self.current_number = MATH_STARTING_NUMBER
        self.math_history = []

        # Font settings for descriptive task
        self.descriptive_font_size = 16
        self.descriptive_font_family = 'Arial'
        
        # Countdown timer configuration
        self.countdown_enabled = COUNTDOWN_ENABLED  # Global toggle for all countdowns
        self.descriptive_countdown_minutes = DESCRIPTIVE_COUNTDOWN_MINUTES
        self.stroop_countdown_minutes = STROOP_COUNTDOWN_MINUTES
        self.math_countdown_minutes = MATH_COUNTDOWN_MINUTES
        
        # Countdown state
        self.countdown_remaining = 0
        self.countdown_thread = None
        self.countdown_label = None
        self.countdown_running = False
        
        # Create main container
        self.setup_main_ui()

        # Set up crash detection
        self.setup_crash_detection()

        # Check for incomplete sessions before showing participant ID screen
        self.check_and_handle_recovery()

    def setup_crash_detection(self):
        """Set up crash detection and logging."""
        # Log app startup
        print("🚀 App startup detected")

        # Register signal handlers for crash detection
        signal.signal(signal.SIGINT, self.handle_crash)
        signal.signal(signal.SIGTERM, self.handle_crash)

        # Register exit handler
        atexit.register(self.handle_app_exit)

    def handle_crash(self, signum, frame):
        """Handle application crash."""
        print(f"💥 Application crash detected (signal {signum})")

        # Log the crash if logging is set up
        if hasattr(self, 'action_log_file_path') and self.action_log_file_path:
            try:
                crash_data = {
                    "timestamp": {
                        "local": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "unix": time.time()
                    },
                    "participant_id": getattr(self, 'participant_id', 'UNKNOWN'),
                    "action_type": "APPLICATION_CRASH",
                    "details": f"Application crashed with signal {signum}",
                    "screen": getattr(self, 'current_screen', 'unknown'),
                    "session_duration_seconds": (datetime.now() - self.session_start_time).total_seconds()
                }

                with open(self.action_log_file_path, 'a') as f:
                    f.write(json.dumps(crash_data) + '\n')

                print("💾 Crash logged to file")
            except Exception as e:
                print(f"⚠️ Could not log crash: {e}")

        # Clean up and exit
        try:
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
        except:
            pass

        exit(1)

    def handle_app_exit(self):
        """Handle normal app exit."""
        # This is called on normal exit, not crashes
        if hasattr(self, 'action_log_file_path') and self.action_log_file_path:
            try:
                # Only log if we haven't already logged an exit
                if not hasattr(self, '_exit_logged'):
                    print("🔚 Normal app exit detected")
            except:
                pass

    def check_and_handle_recovery(self):
        """Check for incomplete sessions and handle recovery."""
        try:
            incomplete_session = self.check_for_incomplete_sessions()
            if incomplete_session:
                print(f"🔄 Found incomplete session for {incomplete_session['participant_id']}")
                self.show_recovery_dialog(incomplete_session)
            else:
                # No incomplete sessions, show normal participant ID screen
                self.show_participant_id_screen()
        except Exception as e:
            print(f"⚠️ Error during recovery check: {e}")
            # If recovery check fails, proceed normally
            self.show_participant_id_screen()
        
    def setup_main_ui(self):
        """Setup the main UI container."""
        # Main frame that will hold all screens
        self.main_frame = tk.Frame(self.root, bg=MAIN_FRAME_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def clear_screen(self):
        """Clear current screen content."""
        # Stop countdown timer first
        self.stop_countdown()
        
        # Stop video if running - improved cleanup to prevent double free
        if hasattr(self, 'running'):
            self.running = False

        # Wait a moment for video threads to finish
        time.sleep(0.1)

        # Clean up video capture safely
        if hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except Exception as e:
                print(f"Warning: Error releasing video capture: {e}")
            finally:
                self.cap = None
        
        # Clear video frame reference
        if hasattr(self, 'video_frame'):
            self.video_frame = None
        
        # Clear countdown label reference safely
        self.countdown_label = None
        
        # Clear all widgets from main frame safely
        if hasattr(self, 'main_frame'):
            try:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
            except tk.TclError:
                pass
        
        # Clear all key bindings
        self.root.unbind_all('<KeyPress-space>')
        self.root.unbind_all('<KeyPress-n>')
        self.root.unbind_all('<KeyPress-N>')
        self.root.unbind_all('<KeyPress-r>')
        self.root.unbind_all('<KeyPress-R>')
        self.root.unbind_all('<KeyPress-m>')
        self.root.unbind_all('<KeyPress-M>')
        self.root.unbind_all('<KeyPress-Escape>')
        self.root.unbind_all('<KeyPress-q>')
        self.root.unbind_all('<Return>')
        self.root.unbind_all('<Control-Return>')
        self.root.unbind_all('<Alt-Command-n>')
        self.root.unbind_all('<Alt-Command-N>')
        self.root.unbind_all('<Option-Command-n>')
        self.root.unbind_all('<Option-Command-N>')
        self.root.unbind_all('<Command-Alt-n>')
        self.root.unbind_all('<Command-Alt-N>')
        self.root.unbind_all('<Command-n>')
        self.root.unbind_all('<Command-N>')
    
    # =================== PARTICIPANT ID SCREEN ===================
    
    def show_participant_id_screen(self):
        """Show participant ID entry screen."""
        print("🆔 Showing Participant ID Entry Screen")
        self.clear_screen()
        self.current_screen = "participant_id"
        
        # Set neutral background for start screen
        self.main_frame.configure(bg='black')
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="Moly - Performance Evaluation",
            font=('Arial', 36, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=80)
        
        # Instructions
        instruction = tk.Label(
            self.main_frame,
            text="Please enter your participant ID to begin:",
            font=('Arial', 32),
            fg='white',
            bg='black'
        )
        instruction.pack(pady=30)
        
        # Participant ID entry
        self.participant_id_var = tk.StringVar()
        
        # Validation function for participant ID
        def validate_participant_id(char):
            """Allow only letters, numbers, underscore, and hyphen."""
            return char.isalnum() or char in ['_', '-']
        
        # Register validation function
        validate_cmd = (self.root.register(validate_participant_id), '%S')
        
        id_entry = tk.Entry(
            self.main_frame,
            textvariable=self.participant_id_var,
            font=('Arial', 20),
            width=20,
            justify='center',
            fg='black',
            bg='white',
            insertbackground='black',  # Cursor color
            selectbackground='lightblue',  # Selection highlight
            selectforeground='black',  # Selected text color
            validate='key',
            validatecommand=validate_cmd
        )
        id_entry.pack(pady=20)
        id_entry.focus_set()
        
        # Bind key events to convert to uppercase
        def on_key_press(event):
            if event.char.isalpha():
                # Convert alphabetic characters to uppercase
                current_pos = id_entry.index(tk.INSERT)
                current_text = self.participant_id_var.get()
                new_text = current_text[:current_pos] + event.char.upper() + current_text[current_pos:]
                self.participant_id_var.set(new_text)
                id_entry.icursor(current_pos + 1)
                return 'break'  # Prevent default behavior
        
        id_entry.bind('<KeyPress>', on_key_press)
        
        # Submit button
        def submit_participant_id():
            participant_id = self.participant_id_var.get().strip()
            if participant_id:
                self.set_participant_id(participant_id)
                self.log_action("PARTICIPANT_ID_SUBMITTED", f"Participant ID: {participant_id}")
                self.switch_to_relaxation()
            else:
                # Show error message briefly
                error_label = tk.Label(
                    self.main_frame,
                    text="⚠️ Please enter a valid participant ID",
                    font=('Arial', 16),
                    fg=COLORS['warning'],
                    bg='black'
                )
                error_label.pack(pady=10)
                self.root.after(3000, error_label.destroy)
        
        submit_button = tk.Button(
            self.main_frame,
            text="START SESSION",
            font=('Arial', 16, 'bold'),
            fg='black',
            bg=COLORS['button_bg'],
            activebackground=COLORS['button_active'],
            activeforeground='black',
            width=20,
            height=2,
            command=submit_participant_id
        )
        submit_button.pack(pady=30)
        
        # Bind Enter key to submit
        def on_enter(event):
            submit_participant_id()
        
        self.root.bind_all('<Return>', on_enter)
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        print("✅ Participant ID screen ready")
    
    def set_participant_id(self, participant_id):
        """Set the participant ID and create log files in organized folder structure."""
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

        # Create session info file (replaces the empty legacy log)
        self.create_session_info_file()

        # Create the action log file
        self.setup_action_logging()

        # Create the descriptive response file
        self.setup_descriptive_response_logging()

        # Create the tech log file
        self.setup_tech_logging()

    def create_session_info_file(self):
        """Create session information file with metadata."""
        try:
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
            with open(self.action_log_file_path, 'w') as f:
                pass  # Create empty file
            self.tech_print(f"📊 Action log file created: {self.action_log_file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create action log file: {e}")

    def setup_descriptive_response_logging(self):
        """Initialize the descriptive response logging system with JSONL format."""
        try:
            # JSONL format doesn't need headers - each line is a complete JSON object
            # Create empty file
            with open(self.descriptive_response_file_path, 'w') as f:
                pass  # Create empty file
            self.tech_print(f"📝 Descriptive response file created: {self.descriptive_response_file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create descriptive response file: {e}")

    def setup_tech_logging(self):
        """Initialize the tech logging system with JSONL format."""
        try:
            # JSONL format doesn't need headers - each line is a complete JSON object
            # Create empty file
            with open(self.tech_log_file_path, 'w') as f:
                pass  # Create empty file
            print(f"🔧 Tech log file created: {self.tech_log_file_path}")  # Can't use tech_print here yet
        except Exception as e:
            print(f"⚠️ Warning: Could not create tech log file: {e}")

    def log_action(self, action, details=""):
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
                "screen": self.current_screen,
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

    def log_tech_message(self, message, level="INFO"):
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
                "participant_id": getattr(self, 'participant_id', 'unknown'),
                "level": level,
                "message": message,
                "screen": getattr(self, 'current_screen', 'unknown'),
                "session_duration_seconds": (now - self.session_start_time).total_seconds() if hasattr(self, 'session_start_time') else 0
            }

            with open(self.tech_log_file_path, 'a') as f:
                f.write(json.dumps(tech_entry) + '\n')

        except Exception as e:
            # Fallback to regular print if tech logging fails
            print(f"⚠️ Warning: Could not write to tech log: {e}")

    def tech_print(self, message, level="INFO"):
        """Print message to console and log it to tech log file."""
        # Print to console
        print(message)
        
        # Log to tech log file
        self.log_tech_message(message, level)

    def log_sentence_completion(self, sentence):
        """Log when user completes a sentence using the action logging system."""
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

    # =================== REUSABLE LOGGING HELPERS ===================

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

    def log_user_input(self, input_type, details=""):
        """Helper method to log user inputs (key presses, button clicks, etc.)."""
        self.log_action(input_type, details)

    def log_window_event(self, event_type, window_name, details=""):
        """Helper method to log window-specific events."""
        action_details = f"{window_name}: {details}" if details else window_name
        self.log_action(event_type, action_details)

    def log_partial_text(self, text_content, countdown_remaining=None):
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
                    "current_prompt_index": getattr(self, 'current_prompt_index', 0),
                    "countdown_remaining": countdown_remaining
                },
                "screen": "descriptive_task",
                "session_duration_seconds": (datetime.now() - self.session_start_time).total_seconds()
            }

            with open(self.action_log_file_path, 'a') as f:
                f.write(json.dumps(partial_data) + '\n')

        except Exception as e:
            print(f"⚠️ Error logging partial text: {e}")

    def log_countdown_state(self, countdown_remaining, countdown_total):
        """Log countdown timer state for recovery."""
        countdown_data = {
            "remaining_seconds": countdown_remaining,
            "total_seconds": countdown_total,
            "percentage_complete": ((countdown_total - countdown_remaining) / countdown_total * 100) if countdown_total > 0 else 0
        }
        self.log_action("COUNTDOWN_STATE", json.dumps(countdown_data))

    # =================== CRASH RECOVERY SYSTEM ===================

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

    def show_recovery_dialog(self, recovery_data):
        """Show recovery dialog to user."""
        print("🔄 Crash Recovery - Incomplete session detected")
        self.clear_screen()
        self.current_screen = "recovery"

        # Set neutral background for recovery screen
        self.main_frame.configure(bg='black')

        # Title
        title = tk.Label(
            self.main_frame,
            text="🔄 Session Recovery",
            font=('Arial', 36, 'bold'),
            fg='orange',
            bg='black'
        )
        title.pack(pady=50)

        # Recovery info
        participant_id = recovery_data['participant_id']
        last_screen = recovery_data['last_screen']
        session_start = datetime.fromtimestamp(recovery_data['session_start_unix']).strftime('%Y-%m-%d %H:%M:%S')

        info_text = f"""An incomplete session was detected for participant {participant_id}.

Session started: {session_start}
Last screen: {last_screen}

Choose an option:"""

        info_label = tk.Label(
            self.main_frame,
            text=info_text,
            font=('Arial', 18),
            fg='white',
            bg='black',
            wraplength=800,
            justify='center'
        )
        info_label.pack(pady=30)

        # Button frame
        button_frame = tk.Frame(self.main_frame, bg='black')
        button_frame.pack(pady=40)

        # Resume button
        resume_button = tk.Button(
            button_frame,
            text="RESUME SESSION",
            font=('Arial', 14, 'bold'),
            fg='black',
            bg='lightgreen',
            activebackground='green',
            width=18,
            height=2,
            command=lambda: self.resume_session(recovery_data)
        )
        resume_button.pack(side=tk.LEFT, padx=10)

        # Reset & Restore button (only show if last screen was descriptive_task)
        if recovery_data['last_screen'] == 'descriptive_task':
            reset_button = tk.Button(
                button_frame,
                text="RESET & RESTORE\nTO DESCRIPTIVE",
                font=('Arial', 12, 'bold'),
                fg='black',
                bg='lightyellow',
                activebackground='yellow',
                width=18,
                height=2,
                command=lambda: self.reset_and_restore_descriptive(recovery_data)
            )
            reset_button.pack(side=tk.LEFT, padx=10)

        # New session button
        new_button = tk.Button(
            button_frame,
            text="START NEW SESSION",
            font=('Arial', 14, 'bold'),
            fg='black',
            bg='lightblue',
            activebackground='blue',
            width=18,
            height=2,
            command=self.start_new_session
        )
        new_button.pack(side=tk.RIGHT, padx=10)

        # Focus on resume button
        resume_button.focus_set()
        if FOCUS_MODE:
            self.root.focus_force()

    def resume_session(self, recovery_data):
        """Resume session from recovery data."""
        print(f"🔄 Resuming session for participant {recovery_data['participant_id']}")

        # Set up participant data
        self.participant_id = recovery_data['participant_id']
        self.log_dir = recovery_data['session_dir']
        self.session_info_file_path = recovery_data['session_info_path']

        # Set up log file paths (reuse existing files)
        timestamp = os.path.basename(recovery_data['session_info_path']).replace('session_info_', '').replace('.json', '')
        self.action_log_file_path = os.path.join(self.log_dir, f"actions_{timestamp}.jsonl")
        self.descriptive_response_file_path = os.path.join(self.log_dir, f"descriptive_responses_{timestamp}.jsonl")

        # Set session start time to original session start time for proper duration calculation
        original_start = recovery_data['session_info']['session_start_time']['unix_timestamp']
        self.session_start_time = datetime.fromtimestamp(original_start)

        # Set recovery flag
        self.is_recovering = True
        self.recovery_data = recovery_data

        # Log app reopening and recovery
        self.log_action("APPLICATION_REOPENED", f"Application reopened after crash, resuming from {recovery_data['last_screen']} screen")
        self.log_action("SESSION_RESUMED", f"Resumed session from {recovery_data['last_screen']} screen")

        # Resume to appropriate screen
        recovery_state = recovery_data['recovery_state']
        screen = recovery_state['screen']

        if screen == 'descriptive_task':
            self.resume_descriptive_task(recovery_state)
        elif screen == 'relaxation':
            self.switch_to_relaxation()
        elif screen == 'stroop':
            self.switch_to_stroop()
        elif screen == 'math_task':
            self.switch_to_math_task()
        elif screen == 'post_study_rest':
            self.switch_to_post_study_rest()
        else:
            # Default to participant ID screen
            self.show_participant_id_screen()

    def resume_descriptive_task(self, recovery_state):
        """Resume descriptive task with previous state."""
        # Restore prompt index
        self.current_prompt_index = recovery_state.get('current_prompt_index', 0)

        # Go directly to descriptive task setup (skip transition since we're resuming)
        self._setup_descriptive_task()

        # If there are completed responses, show a notification
        completed_responses = recovery_state.get('completed_responses', [])
        if completed_responses:
            # Show brief notification about restored responses
            self.show_recovery_notification(f"Restored {len(completed_responses)} previous responses")

    def reset_and_restore_descriptive(self, recovery_data):
        """Reset responses and countdown but restore to descriptive task."""
        print(f"🔄 Resetting and restoring descriptive task for participant {recovery_data['participant_id']}")
        
        # Set up participant data (keep the same participant ID and session files)
        self.participant_id = recovery_data['participant_id']
        self.log_dir = recovery_data['session_dir']
        self.session_info_file_path = recovery_data['session_info_path']
        
        # Set up log file paths (reuse existing files)
        timestamp = os.path.basename(recovery_data['session_info_path']).replace('session_info_', '').replace('.json', '')
        self.action_log_file_path = os.path.join(self.log_dir, f"actions_{timestamp}.jsonl")
        self.descriptive_response_file_path = os.path.join(self.log_dir, f"descriptive_responses_{timestamp}.jsonl")
        
        # Reset descriptive task state - start from beginning
        self.current_prompt_index = 0
        self.prompts = DESCRIPTIVE_PROMPTS.copy()
        
        # Reset countdown settings
        self.countdown_enabled = COUNTDOWN_ENABLED and DESCRIPTIVE_COUNTDOWN_ENABLED
        self.descriptive_countdown_minutes = DESCRIPTIVE_COUNTDOWN_MINUTES
        
        # Clear any recovery state
        self.is_recovering = False
        self.recovery_data = None
        
        # Log the reset action
        self.log_action("RECOVERY_RESET_RESTORE", "User chose to reset responses and countdown, restoring to descriptive task")
        
        # Go directly to descriptive task setup (skip transition)
        self._setup_descriptive_task()
        
        # Show notification about the reset
        self.show_recovery_notification("Reset complete - Starting fresh with all prompts and full countdown")

    def show_recovery_notification(self, message):
        """Show a brief recovery notification."""
        notification = tk.Label(
            self.main_frame,
            text=f"🔄 {message}",
            font=('Arial', 14, 'bold'),
            fg='lightgreen',
            bg=BACKGROUND_COLOR
        )
        notification.pack(pady=5)

        # Remove notification after 3 seconds
        self.root.after(3000, notification.destroy)

    def restore_current_prompt_text(self):
        """Restore text for current prompt if available from previous session."""
        if not self.recovery_data or not hasattr(self, 'response_text'):
            return

        # Look for the most recent partial text update for current prompt
        actions = self.recovery_data.get('actions', [])
        partial_text = ""
        countdown_remaining = None

        # Find the most recent partial text update for the current prompt
        current_prompt = getattr(self, 'current_prompt_index', 0)

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
            self.response_text.delete('1.0', tk.END)
            self.response_text.insert('1.0', partial_text)
            self.update_word_count()
            print(f"🔄 Restored {len(partial_text)} characters of partial text")

            # Position cursor at end
            self.response_text.mark_set(tk.INSERT, tk.END)
            self.response_text.focus_set()

        # Restore countdown timer if found and countdown is enabled
        if countdown_remaining and COUNTDOWN_ENABLED:
            try:
                if countdown_remaining > 0:
                    # Convert to milliseconds for consistency with the main countdown system
                    self.countdown_remaining = int(countdown_remaining * 1000)
                    self.countdown_running = True
                    print(f"🔄 Restored countdown: {countdown_remaining} seconds remaining")

                    # Start the countdown from where it left off (delay to ensure UI is ready)
                    if hasattr(self, 'countdown_label') and self.countdown_label:
                        self.root.after(200, self.start_restored_countdown)
            except Exception as e:
                print(f"⚠️ Could not restore countdown: {e}")

        # Show notification that we're in recovery mode
        recovery_msg = "Session restored"
        if partial_text:
            recovery_msg += f" - {len(partial_text.split())} words restored"
        if countdown_remaining:
            recovery_msg += f" - {int(countdown_remaining)}s remaining"

        self.show_recovery_notification(recovery_msg)

    def start_countdown_from_remaining(self):
        """Start countdown from remaining time (for recovery)."""
        if not hasattr(self, 'countdown_remaining') or self.countdown_remaining <= 0:
            return

        self.countdown_running = True

        def countdown_tick():
            if not self.countdown_running or not hasattr(self, 'countdown_label'):
                return

            if self.countdown_remaining > 0:
                minutes = self.countdown_remaining // 60
                seconds = self.countdown_remaining % 60
                self.countdown_label.config(text=f"⏱️ Time remaining: {minutes:02d}:{seconds:02d}")

                # Log countdown state periodically (every 30 seconds)
                if self.countdown_remaining % 30 == 0:
                    total_time = DESCRIPTIVE_COUNTDOWN_MINUTES * 60
                    self.log_countdown_state(self.countdown_remaining, total_time)

                self.countdown_remaining -= 1
                self.root.after(1000, countdown_tick)
            else:
                self.countdown_label.config(text="⏰ Time's up!", fg='red')
                self.countdown_running = False

        countdown_tick()

    def start_restored_countdown(self):
        """Start countdown from restored state (for recovery)."""
        if not hasattr(self, 'countdown_remaining') or self.countdown_remaining <= 0:
            return

        print(f"⏱️ Starting restored countdown with {self.countdown_remaining // 1000} seconds remaining")

        # Record start time for accurate timing
        import time
        start_time = time.time() * 1000  # Get current time in milliseconds
        initial_countdown = self.countdown_remaining
        
        def restored_countdown_loop():
            while (self.countdown_remaining > 0 and
                   self.countdown_running and
                   hasattr(self, 'countdown_label') and self.countdown_label):
                try:
                    # Calculate actual elapsed time and update countdown
                    current_time = time.time() * 1000
                    elapsed = current_time - start_time
                    self.countdown_remaining = max(0, initial_countdown - int(elapsed))
                    
                    # Update display
                    seconds = self.countdown_remaining // 1000
                    minutes = seconds // 60
                    secs = seconds % 60
                    self.countdown_label.config(text=f"⏱️ Time remaining: {minutes:02d}:{secs:02d}")

                    # Log countdown state periodically (every 30 seconds)
                    if seconds % 30 == 0 and self.countdown_remaining % 1000 < 100:
                        total_time = DESCRIPTIVE_COUNTDOWN_MINUTES * 60
                        self.log_countdown_state(seconds, total_time)

                    # Sleep for smooth display updates
                    time.sleep(0.1)  # Update every 100ms

                except Exception as e:
                    print(f"⚠️ Error in restored countdown: {e}")
                    break

            # Time's up notification
            if (self.countdown_remaining <= 0 and
                self.countdown_running and
                hasattr(self, 'countdown_label') and self.countdown_label):
                try:
                    self.countdown_label.config(text="⏰ Time's up!", fg='red')
                    self.countdown_running = False
                except:
                    pass

        # Start countdown in a separate thread
        countdown_thread = threading.Thread(target=restored_countdown_loop, daemon=True)
        countdown_thread.start()

    def start_new_session(self):
        """Start a new session (normal flow)."""
        print("🆕 Starting new session")
        self.show_participant_id_screen()
    
    # =================== RELAXATION SCREEN ===================
    
    def switch_to_relaxation(self):
        """Switch to relaxation screen with video background."""
        print("🧘 Switching to Relaxation Screen")
        self.log_action("SCREEN_TRANSITION", "Switching to relaxation screen")
        self.clear_screen()
        self.current_screen = "relaxation"
        self.running = True
        
        # Setup video canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.screen_width,
            height=self.screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create text overlay if enabled
        if self.show_text:
            self.text_item = self.canvas.create_text(
                self.screen_width // 2, self.screen_height // 2,
                text=RELAXATION_TEXT,
                font=('Arial', 48, 'bold'),
                fill=COLORS['text_primary']
            )
        
        # Initialize video
        self.init_video(self.relaxation_video)
        
        # Start video loop
        self.start_video_loop()
        
        # Bind keys (only allow navigation in developer mode)
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_relaxation_enter)
        self.root.bind_all('<KeyPress-q>', self.on_quit)
        self.root.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Start hidden countdown for automatic transition
        self.start_relaxation_countdown(RELAXATION_COUNTDOWN_MINUTES)
        
        self.tech_print("✅ Relaxation screen ready - Press ENTER for next screen")
        self.log_action("SCREEN_DISPLAYED", "Relaxation screen displayed and ready")
    
    def on_relaxation_enter(self, event):
        """Handle Enter key in relaxation screen - go to descriptive task screen."""
        print("🎯 Enter pressed - Going to Descriptive Task screen...")
        self.log_action("KEY_PRESS", "Enter key pressed in relaxation screen")
        self.switch_to_descriptive_task()
    
    def start_relaxation_countdown(self, minutes):
        """Start hidden countdown for relaxation screen auto-transition."""
        total_time = minutes * 60 * 1000  # Convert to milliseconds
        
        def auto_transition():
            if self.current_screen == "relaxation":
                print(f"⏰ Relaxation countdown finished - Auto-transitioning to descriptive task")
                self.log_action("AUTO_TRANSITION", f"Relaxation countdown ({minutes} minutes) completed, transitioning to descriptive task")
                self.switch_to_descriptive_task()
        
        # Schedule the automatic transition
        self.root.after(total_time, auto_transition)
        self.log_action("RELAXATION_COUNTDOWN_STARTED", f"Hidden countdown started for {minutes} minutes")
    
    # =================== DESCRIPTIVE TASK SCREEN ===================
    
    def switch_to_descriptive_task(self):
        """Switch to descriptive task screen."""
        # Show transition screen first
        self.show_transition_screen(
            TRANSITION_MESSAGES['descriptive'],
            self._setup_descriptive_task
        )
    
    def _setup_descriptive_task(self):
        """Actually setup the descriptive task screen after confirmation."""
        self.tech_print("🎯 Setting up Descriptive Task Screen")
        self.log_action("SCREEN_TRANSITION", "Setting up descriptive task screen")
        self.clear_screen()
        self.current_screen = "descriptive_task"
        self.last_sentence_position = 0  # Reset sentence tracking
        self._last_text_length = 0  # Reset text length tracking for sentence detection
        
        # Set dark red background for stress
        self.main_frame.configure(bg=BACKGROUND_COLOR)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="Descriptive Task",
            font=('Arial', 32, 'bold'),
            fg=COLORS['title'],
            bg=BACKGROUND_COLOR
        )
        title.pack(pady=30)
        
        # Evaluation hint
        evaluation_hint = tk.Label(
            self.main_frame,
            text="⚠️ Your responses will be evaluated for accuracy and detail",
            font=('Arial', 24, 'bold'),
            fg=COLORS['warning'],
            bg=BACKGROUND_COLOR
        )
        evaluation_hint.pack(pady=10)
        
        # Countdown timer (check both global and individual toggles)
        if self.countdown_enabled and DESCRIPTIVE_COUNTDOWN_ENABLED:
            self.countdown_label = tk.Label(
                self.main_frame,
                text=f"⏰ You only have {self.descriptive_countdown_minutes} minutes left!",
                font=('Arial', 16, 'bold'),
                fg=COLORS['countdown_normal'],
                bg=BACKGROUND_COLOR
            )
            self.countdown_label.pack(pady=10)
        
        # Start button
        self.descriptive_start_button = tk.Button(
            self.main_frame,
            text="START TASK",
            font=('Arial', 20, 'bold'),
            fg='black',
            bg='lightgreen',
            activebackground='green',
            width=15,
            height=2,
            command=self.start_descriptive_task
        )
        self.descriptive_start_button.pack(pady=20)
        
        # Current prompt display
        self.prompt_label = tk.Label(
            self.main_frame,
            text="Click START TASK to begin",
            font=('Arial', 32),
            fg=COLORS['text_primary'],
            bg=BACKGROUND_COLOR,
            wraplength=800,
            justify='center'
        )
        self.prompt_label.pack(pady=30)
        
        # Response textbox
        response_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        response_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        response_label = tk.Label(
            response_frame,
            text="Your Response:",
            font=('Arial', 16, 'bold'),
            fg=COLORS['text_primary'],
            bg=BACKGROUND_COLOR
        )
        response_label.pack(anchor='w', pady=(0, 5))
        
        # Text widget with scrollbar
        text_frame = tk.Frame(response_frame, bg=BACKGROUND_COLOR)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.response_text = tk.Text(
            text_frame,
            font=(self.descriptive_font_family, self.descriptive_font_size),
            fg='gray',
            bg='lightgray',
            wrap=tk.WORD,
            height=8,
            relief='solid',
            borderwidth=2,
            insertbackground='black',  # Cursor color
            insertwidth=2,            # Cursor width
            selectbackground='lightblue',  # Selection highlight
            selectforeground='black',
            state='disabled'  # Initially disabled
        )
        
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=scrollbar.set)
        
        self.response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind text change event for word count and sentence logging
        self.response_text.bind('<KeyRelease>', self.on_text_change)
        self.response_text.bind('<Button-1>', self.update_word_count)
        self.response_text.bind('<ButtonRelease-1>', self.update_word_count)
        
        # Focus the textbox so cursor appears immediately
        self.response_text.focus_set()
        
        # If recovering, restore any previous text for current prompt (use after to ensure UI is ready)
        if self.is_recovering and self.recovery_data:
            self.root.after(100, self.restore_current_prompt_text)  # Delay to ensure UI is ready
        
        # Word count display
        self.word_count_label = tk.Label(
            response_frame,
            text="Word count: 0",
            font=('Arial', 14),
            fg=COLORS['text_accent'],
            bg=BACKGROUND_COLOR
        )
        self.word_count_label.pack(anchor='e', pady=(5, 0))
        
        # Font controls frame
        font_controls_frame = tk.Frame(response_frame, bg=BACKGROUND_COLOR)
        font_controls_frame.pack(anchor='e', pady=(10, 0))

        font_label = tk.Label(
            font_controls_frame,
            text="Text Size:",
            font=('Arial', 12),
                fg=COLORS['text_secondary'],
                bg=BACKGROUND_COLOR
            )
        font_label.pack(side=tk.LEFT, padx=(0, 5))

        # Font size buttons
        decrease_font_btn = tk.Button(
            font_controls_frame,
            text="A-",
            font=('Arial', 10, 'bold'),
            fg='black',
            bg='#cccccc',
            activebackground='#aaaaaa',
            width=3,
            height=1,
            command=self.decrease_font_size
        )
        decrease_font_btn.pack(side=tk.LEFT, padx=2)

        self.font_size_label = tk.Label(
            font_controls_frame,
            text=str(self.descriptive_font_size),
            font=('Arial', 12, 'bold'),
            fg=COLORS['text_accent'],
            bg=BACKGROUND_COLOR,
            width=3
        )
        self.font_size_label.pack(side=tk.LEFT, padx=2)

        increase_font_btn = tk.Button(
            font_controls_frame,
            text="A+",
            font=('Arial', 10, 'bold'),
            fg='black',
            bg='#cccccc',
            activebackground='#aaaaaa',
            width=3,
            height=1,
            command=self.increase_font_size
        )
        increase_font_btn.pack(side=tk.LEFT, padx=2)
        
        # Show first prompt
        self.show_current_prompt()
        
        # Button frame for navigation
        button_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(side=tk.BOTTOM, pady=20)

        # Next prompt button (only show in developer mode)
        if DEVELOPER_MODE:
            next_prompt_button = tk.Button(
                button_frame,
                text="Next Prompt",
                font=('Arial', 14, 'bold'),
                fg='black',
                bg=COLORS['button_bg'],
                activebackground=COLORS['button_active'],
                activeforeground='black',
                width=15,
                height=2,
                command=self.on_next_prompt_button
            )
            next_prompt_button.pack(side=tk.LEFT, padx=10)

        # Proceed to Stroop button (only show in developer mode)
        if DEVELOPER_MODE:
            stroop_button = tk.Button(
                button_frame,
                text="Proceed to Stroop Task",
                font=('Arial', 14, 'bold'),
                fg='black',
                bg=COLORS['button_bg'],
                activebackground=COLORS['button_active'],
                activeforeground='black',
                width=20,
                height=2,
                command=self.on_descriptive_enter_button
            )
            stroop_button.pack(side=tk.RIGHT, padx=10)
        
        # Set initial focus to the start button
        self.descriptive_start_button.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Don't start countdown automatically - will start when user clicks START button
        # Initialize task as not started
        self.descriptive_task_started = False
        
        print("✅ Descriptive task screen ready - Use buttons to navigate")
        self.log_action("SCREEN_DISPLAYED", "Descriptive task screen displayed and ready")
    
    def show_current_prompt(self):
        """Show current descriptive prompt."""
        if self.current_prompt_index < len(self.prompts):
            prompt = self.prompts[self.current_prompt_index]
            self.prompt_label.config(text=prompt)
        else:
            self.prompt_label.config(text="Great job! You've completed all the descriptive tasks.")
    
    def start_descriptive_task(self):
        """Start the descriptive task - enable textbox and start countdown."""
        if self.descriptive_task_started:
            return  # Already started
        
        print("🚀 Starting descriptive task...")
        self.log_action("TASK_STARTED", "Descriptive task started by user")
        
        # Mark as started
        self.descriptive_task_started = True
        
        # Hide the start button
        self.descriptive_start_button.destroy()
        
        # Enable the textbox
        self.response_text.config(
            state='normal',
            fg='black',
            bg='white'
        )
        
        # Show the first prompt
        self.show_current_prompt()
        
        # Set focus to textbox
        self.response_text.focus_set()
        
        # Start countdown timer (if enabled and not recovering)
        if self.countdown_enabled and DESCRIPTIVE_COUNTDOWN_ENABLED and not self.is_recovering:
            self.start_countdown(self.descriptive_countdown_minutes, "descriptive_task")
    
    def on_next_prompt_button(self):
        """Handle Next Prompt button - next prompt."""
        print(f"📝 Next Prompt button pressed - Next prompt ({self.current_prompt_index + 1})")
        self.log_action("BUTTON_PRESS", f"Next Prompt button pressed (moving to prompt {self.current_prompt_index + 1})")

        # Save current response before moving to next prompt
        if hasattr(self, 'response_text'):
            current_response = self.response_text.get("1.0", tk.END).strip()
            if current_response:
                current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                self.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)

        self.current_prompt_index += 1
        self.show_current_prompt()

    def on_descriptive_enter_button(self):
        """Handle Proceed to Stroop button - go to Stroop screen."""
        print("🎬 Proceed to Stroop button pressed - Going to Stroop screen...")
        self.log_action("BUTTON_PRESS", "Proceed to Stroop Task button pressed")

        # Save final response before leaving descriptive task
        if hasattr(self, 'response_text'):
            current_response = self.response_text.get("1.0", tk.END).strip()
            if current_response:
                current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                self.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)

        self.switch_to_stroop()  # Use proper transition screen
    
    def on_next_prompt(self, event):
        """Handle Cmd+N key - next prompt."""
        print(f"📝 Cmd+N pressed - Next prompt ({self.current_prompt_index + 1})")
        self.current_prompt_index += 1
        self.show_current_prompt()
    
    def on_descriptive_enter(self, event):
        """Handle Ctrl+Enter key in descriptive task - go to Stroop screen."""
        print("🎬 Ctrl+Enter pressed - Going to Stroop screen...")
        self.switch_to_stroop()  # Use proper transition screen
    
    def on_descriptive_escape(self, event):
        """Handle escape in descriptive task - go to relaxation."""
        print("🧘 Escape pressed - Going to Relaxation screen...")
        self.switch_to_relaxation()
    
    def on_text_change(self, event=None):
        """Handle text changes in descriptive task - update word count and check for sentences."""
        self.update_word_count(event)

        # Log partial text for crash recovery (every few characters to avoid spam)
        if hasattr(self, 'response_text'):
            current_text = self.response_text.get('1.0', tk.END).strip()

            # Only log if text has changed significantly (every 10 characters or so)
            if not hasattr(self, '_last_logged_length'):
                self._last_logged_length = 0

            text_length = len(current_text)
            if text_length > 0 and (text_length - self._last_logged_length >= 10 or text_length % 50 == 0):
                # Get current countdown state if available (convert to seconds)
                countdown_remaining = None
                if hasattr(self, 'countdown_remaining'):
                    countdown_remaining = self.countdown_remaining // 1000  # Convert milliseconds to seconds

                self.log_partial_text(current_text, countdown_remaining)
                self._last_logged_length = text_length

        self.check_for_sentence_completion(event)
    
    def update_word_count(self, event=None):
        """Update word count for descriptive task response."""
        if hasattr(self, 'response_text') and hasattr(self, 'word_count_label'):
            try:
                text_content = self.response_text.get("1.0", tk.END).strip()
                if text_content:
                    word_count = len(text_content.split())
                else:
                    word_count = 0
                self.word_count_label.config(text=f"Word count: {word_count}")
            except tk.TclError:
                pass
    
    def check_for_sentence_completion(self, event=None):
        """Check if user completed a sentence by typing '.'"""
        if not DESCRIPTIVE_LINE_LOGGING or not hasattr(self, 'response_text'):
            return

        try:
            # Get current text content
            text_content = self.response_text.get("1.0", tk.END)

            # Check if a period was just typed (multiple ways to detect)
            period_typed = False
            if event:
                # Check for period key or character
                if event.keysym == 'period' or event.char == '.':
                    period_typed = True

            # Also check if text ends with a period that wasn't there before
            if not period_typed and text_content.strip().endswith('.'):
                # Check if this is a new period by comparing length
                if not hasattr(self, '_last_text_length'):
                    self._last_text_length = 0

                if len(text_content) > self._last_text_length:
                    period_typed = True

                self._last_text_length = len(text_content)

            if period_typed:
                # Find the sentence that was just completed
                text_clean = text_content.strip()
                if text_clean.endswith('.'):
                    # Find the start of the current sentence
                    sentence_start = max(
                        text_clean.rfind('.', 0, -1) + 1,  # Find previous period, excluding the last one
                        text_clean.rfind('!') + 1,
                        text_clean.rfind('?') + 1,
                        0
                    )

                    # Extract the completed sentence
                    completed_sentence = text_clean[sentence_start:].strip()

                    if completed_sentence and completed_sentence != '.' and len(completed_sentence) > 1:
                        self.log_sentence_completion(completed_sentence)

        except Exception as e:
            print(f"⚠️ Warning: Error in sentence completion check: {e}")

    def increase_font_size(self):
        """Increase font size of the descriptive task text."""
        if self.descriptive_font_size < 32:  # Maximum font size
            old_size = self.descriptive_font_size
            self.descriptive_font_size += 2
            self.update_descriptive_font()
            self.log_action("FONT_CHANGE", f"Font size increased from {old_size} to {self.descriptive_font_size}")

    def decrease_font_size(self):
        """Decrease font size of the descriptive task text."""
        if self.descriptive_font_size > 8:  # Minimum font size
            old_size = self.descriptive_font_size
            self.descriptive_font_size -= 2
            self.update_descriptive_font()
            self.log_action("FONT_CHANGE", f"Font size decreased from {old_size} to {self.descriptive_font_size}")

    def update_descriptive_font(self):
        """Update the font of the descriptive task text widget."""
        if hasattr(self, 'response_text'):
            try:
                new_font = (self.descriptive_font_family, self.descriptive_font_size)
                self.response_text.config(font=new_font)

                # Update the font size label
                if hasattr(self, 'font_size_label'):
                    self.font_size_label.config(text=str(self.descriptive_font_size))

                print(f"📝 Font size changed to {self.descriptive_font_size}")
            except tk.TclError:
                pass
    
    # =================== stroop SCREEN ===================
    
    def switch_to_stroop(self):
        """Switch to stroop video screen."""
        # Show transition screen first
        self.show_transition_screen(
            TRANSITION_MESSAGES['stroop'],
            self._setup_stroop
        )
    
    def _setup_stroop(self):
        """Actually setup the stroop screen after confirmation."""
        self.tech_print("🎬 Setting up stroop Video Screen")
        self.log_action("SCREEN_TRANSITION", "Setting up stroop video screen")
        self.clear_screen()
        self.current_screen = "stroop"
        self.running = True
        self.is_playing = False
        self.is_paused = False
        
        # Set dark red background for stress
        self.main_frame.configure(bg=BACKGROUND_COLOR)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="Stroop Video Experience",
            font=('Arial', 32, 'bold'),
            fg=COLORS['title'],
            bg=BACKGROUND_COLOR
        )
        title.pack(pady=20)
        
        # Evaluation hint
        evaluation_hint = tk.Label(
            self.main_frame,
            text="⚠️ Your attention and responses are being monitored",
            font=('Arial', 24, 'bold'),
            fg=COLORS['warning'],
            bg=BACKGROUND_COLOR
        )
        evaluation_hint.pack(pady=10)
        
        # Countdown timer (check both global and individual toggles)
        if self.countdown_enabled and STROOP_COUNTDOWN_ENABLED:
            self.countdown_label = tk.Label(
                self.main_frame,
                text=f"⏰ You only have {self.stroop_countdown_minutes} minutes left!",
                font=('Arial', 16, 'bold'),
                fg=COLORS['text_accent'],
                bg=BACKGROUND_COLOR
            )
            self.countdown_label.pack(pady=10)
        
        # Start button
        self.stroop_start_button = tk.Button(
            self.main_frame,
            text="START VIDEO",
            font=('Arial', 20, 'bold'),
            fg='black',
            bg='lightgreen',
            activebackground='green',
            width=15,
            height=2,
            command=self.start_stroop_task
        )
        self.stroop_start_button.pack(pady=20)
        
        # Video canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=800,
            height=450,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Click START VIDEO to begin",
            font=('Arial', 28),
            fg=COLORS['text_accent'],
            bg=BACKGROUND_COLOR
        )
        self.status_label.pack(pady=20)
        
        # File info
        filename = os.path.basename(self.stroop_video) if os.path.exists(self.stroop_video) else "No video file found"
        file_label = tk.Label(
            self.main_frame,
            text=f"File: {filename}",
            font=('Arial', 16),
            fg='#ffaa00',
            bg=BACKGROUND_COLOR
        )
        file_label.pack(pady=5)
        
        # Controls info (only show in developer mode)
        if DEVELOPER_MODE:
            controls = tk.Label(
                self.main_frame,
                text="ENTER - Math Task • R - Restart",
                font=('Arial', 14),
                fg=COLORS['text_secondary'],
                bg=BACKGROUND_COLOR
            )
            controls.pack(pady=10)
        
        # Initialize video but don't start playing
        self.init_video(self.stroop_video, 180)
        
        # Bind keys (only allow navigation in developer mode)
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_stroop_enter)
        self.root.bind_all('<KeyPress-r>', self.on_stroop_restart)
        # ESC key disabled
        self.root.bind_all('<KeyPress-q>', self.on_quit)
        
        # Set focus to start button initially
        self.stroop_start_button.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Don't start countdown automatically - will start when user clicks START button
        # Initialize task as not started
        self.stroop_task_started = False
        
        self.tech_print("✅ Stroop screen ready - ENTER=math, R=restart")
        self.log_action("SCREEN_DISPLAYED", "Stroop screen displayed and ready")
    
    def start_stroop_task(self):
        """Start the Stroop task - begin video playback and start countdown."""
        if self.stroop_task_started:
            return  # Already started
        
        print("🚀 Starting Stroop task...")
        self.log_action("TASK_STARTED", "Stroop task started by user")
        
        # Mark as started
        self.stroop_task_started = True
        
        # Hide the start button
        self.stroop_start_button.destroy()
        
        # Update status and start video
        self.update_status("Starting video...", '#66ff99')
        self.toggle_video_playback()
        
        # Start countdown timer (if enabled)
        if self.countdown_enabled and STROOP_COUNTDOWN_ENABLED:
            self.start_countdown(self.stroop_countdown_minutes, "stroop")
    
    def on_stroop_enter(self, event):
        """Handle Enter key in Stroop screen - go to math task."""
        print("🧮 Enter pressed - Going to Math Task...")
        self.log_action("KEY_PRESS", "Enter key pressed in stroop screen")
        self.switch_to_math_task()  # Use proper transition screen
    
    def on_stroop_restart(self, event):
        """Handle R key in stroop screen - restart video."""
        print("🔄 R pressed - Restarting video...")
        self.log_action("KEY_PRESS", "R key pressed - restarting stroop video")
        self.restart_video()
    
    def on_stroop_escape(self, event):
        """Handle escape in stroop screen - return to descriptive task."""
        print("🎯 Escape pressed - Returning to Descriptive Task...")
        self.switch_to_descriptive_task()
    
    def toggle_video_playback(self):
        """Toggle video playback in stroop screen."""
        if self.cap is None:
            self.update_status("❌ Video file not found", '#ff6666')
            return
        
        try:
            if not self.is_playing and not self.is_paused:
                # Start playing
                self.is_playing = True
                self.update_status("🎬 Playing...", '#66ff99')
                self.start_stroop_video_loop()
                
            elif self.is_playing and not self.is_paused:
                # Pause
                self.is_paused = True
                self.update_status("⏸️ Paused", '#ffff66')
                
            elif self.is_paused:
                # Resume
                self.is_paused = False
                self.update_status("🎬 Playing...", '#66ff99')
                
        except Exception as e:
            self.update_status(f"❌ Video error: {str(e)}", '#ff6666')
    
    def restart_video(self):
        """Restart video from beginning."""
        if self.cap and (self.is_playing or self.is_paused):
            self.is_playing = False
            self.is_paused = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.update_status("🔄 Restarted", '#66ccff')
            # Auto-play after restart
            self.toggle_video_playback()
    
    def update_status(self, text, color='#66ff99'):
        """Update status label."""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=text, fg=color)
    
    def start_stroop_video_loop(self):
        """Start stroop video playback loop."""
        def video_loop():
            while self.running and self.is_playing and self.current_screen == "stroop":
                try:
                    if not self.is_paused and hasattr(self, 'cap') and self.cap:
                        new_frame = self.get_stroop_video_frame()
                        if new_frame:
                            # Update canvas with new frame
                            self.root.after(0, self.update_stroop_video_display, new_frame)
                    time.sleep(1/30)  # 30 FPS
                except (tk.TclError, AttributeError):
                    # Window closed or object destroyed
                    break
        
        thread = threading.Thread(target=video_loop, daemon=True)
        thread.start()
    
    def get_stroop_video_frame(self):
        """Get current video frame for stroop screen."""
        try:
            if self.cap is None:
                return None
                
            ret, frame = self.cap.read()
            if not ret:
                # Loop video - restart from beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return None
            
            # Resize frame to fit canvas (800x450)
            frame = cv2.resize(frame, (800, 450))
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image then PhotoImage
            pil_image = Image.fromarray(frame)
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print(f"Warning: Error reading stroop video frame: {e}")
            return None
    
    def update_stroop_video_display(self, new_frame):
        """Update stroop video display on canvas."""
        try:
            if hasattr(self, 'canvas'):
                # Remove old frame
                self.canvas.delete("video_frame")
                
                # Add new frame
                self.canvas.create_image(
                    400, 225,  # Center of 800x450 canvas
                    image=new_frame,
                    tags="video_frame"
                )
                
                # Keep reference to prevent garbage collection
                self.video_frame = new_frame
        except (tk.TclError, AttributeError):
            # Canvas or window was destroyed
            pass
    
    # =================== MATH TASK SCREEN ===================
    
    def switch_to_math_task(self):
        """Switch to math task screen - subtract 7s from 4000."""
        # Show transition screen first
        self.show_transition_screen(
            TRANSITION_MESSAGES['math'],
            self._setup_math_task
        )
    
    def _setup_math_task(self):
        """Actually setup the math task screen after confirmation."""
        self.tech_print("🧮 Setting up Math Task Screen")
        self.log_action("SCREEN_TRANSITION", "Setting up math task screen")
        self.clear_screen()
        self.current_screen = "math_task"
        
        # Set dark red background for stress
        self.main_frame.configure(bg=BACKGROUND_COLOR)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="Math Task",
            font=('Arial', 32, 'bold'),
            fg=COLORS['title'],
            bg=BACKGROUND_COLOR
        )
        title.pack(pady=20)
        
        # Evaluation hint
        evaluation_hint = tk.Label(
            self.main_frame,
            text="⚠️ Your mathematical performance is being assessed",
            font=('Arial', 24, 'bold'),
            fg=COLORS['warning'],
            bg=BACKGROUND_COLOR
        )
        evaluation_hint.pack(pady=10)
        
        # Countdown timer (check both global and individual toggles)
        if self.countdown_enabled and MATH_COUNTDOWN_ENABLED:
            self.countdown_label = tk.Label(
                self.main_frame,
                text=f"⏰ You only have {self.math_countdown_minutes} minutes left!",
                font=('Arial', 16, 'bold'),
                fg=COLORS['text_accent'],
                bg=BACKGROUND_COLOR
            )
            self.countdown_label.pack(pady=10)
        
        # Start button
        self.math_start_button = tk.Button(
            self.main_frame,
            text="START MATH TASK",
            font=('Arial', 20, 'bold'),
            fg='black',
            bg='lightgreen',
            activebackground='green',
            width=18,
            height=2,
            command=self.start_math_task
        )
        self.math_start_button.pack(pady=20)
        
        # Main prompt
        self.math_prompt = tk.Label(
            self.main_frame,
            text="Click START MATH TASK to begin",
            font=('Arial', 36),
            fg=COLORS['text_primary'],
            bg=BACKGROUND_COLOR,
            wraplength=800,
            justify='center'
        )
        self.math_prompt.pack(expand=True)
        
        # Controls info (only show in developer mode)
        if DEVELOPER_MODE:
            controls = tk.Label(
                self.main_frame,
                text="ENTER - Content Performance Task",
                font=('Arial', 16),
                fg=COLORS['text_secondary'],
                bg=BACKGROUND_COLOR
            )
            controls.pack(side=tk.BOTTOM, pady=20)
        
        # Bind keys (only allow navigation in developer mode)
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_math_enter)
        # ESC key disabled
        # Note: Q key disabled in math task to prevent accidental quit
        
        # Set focus to start button initially
        self.math_start_button.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Don't start countdown automatically - will start when user clicks START button
        # Initialize task as not started
        self.math_task_started = False
        
        self.tech_print("✅ Math task screen ready - ENTER=content performance")
        self.log_action("SCREEN_DISPLAYED", "Math task screen displayed and ready")
    
    def start_math_task(self):
        """Start the Math task - show instructions and start countdown."""
        if self.math_task_started:
            return  # Already started
        
        print("🚀 Starting Math task...")
        self.log_action("TASK_STARTED", "Math task started by user")
        
        # Mark as started
        self.math_task_started = True
        
        # Hide the start button
        self.math_start_button.destroy()
        
        # Show the actual task instructions
        self.math_prompt.config(text=MATH_INSTRUCTION_TEXT)
        
        # Start countdown timer (if enabled)
        if self.countdown_enabled and MATH_COUNTDOWN_ENABLED:
            self.start_countdown(self.math_countdown_minutes, "math_task")
    
    def on_math_enter(self, event):
        """Handle Enter key in math task - go to content performance task."""
        print("📱 Enter pressed - Going to Content Performance Task...")
        self.log_action("KEY_PRESS", "Enter key pressed in math task screen")
        self.switch_to_content_performance_task()
    
    def on_math_escape(self, event):
        """Handle escape in math task - return to Stroop screen."""
        print("🎬 Escape pressed - Returning to Stroop screen...")
        self.switch_to_stroop()
    
    # =================== CONTENT PERFORMANCE TASK SCREEN ===================
    
    def switch_to_content_performance_task(self):
        """Switch to content performance task screen."""
        # Show transition screen first
        self.show_transition_screen(
            "Get ready for content performance task",
            self._setup_content_performance_task
        )
    
    def _setup_content_performance_task(self):
        """Actually setup the content performance task screen after confirmation."""
        self.tech_print("📱 Setting up Content Performance Task Screen")
        self.log_action("SCREEN_TRANSITION", "Setting up content performance task screen")
        self.log_action("CONTENT_PERFORMANCE_ENTER", "Entered content performance task screen")
        self.clear_screen()
        self.current_screen = "content_performance"
        
        # Set darker blue background for better readability
        self.main_frame.configure(bg=CONTENT_PERFORMANCE_BG_COLOR)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="Content Performance Task",
            font=('Arial', 32, 'bold'),
            fg='white',
            bg=CONTENT_PERFORMANCE_BG_COLOR
        )
        title.pack(pady=40)
        
        # Main instruction text (conditional based on task selection mode)
        if TASK_SELECTION_MODE == "random_assigned":
            # Get assigned task for this participant
            assigned_task = self.get_random_assigned_task()
            self.selected_task = assigned_task  # Store for later use
            
            # Get current distribution stats and add to session info
            distribution_stats = self.get_task_distribution_stats()
            self.add_task_selection_to_session_info(assigned_task, TASK_SELECTION_MODE, distribution_stats)
            
            # Create task-specific message
            task_text = f"Now open the Content Performance Task and start the {assigned_task} task."
            
            # Log the assignment
            self.log_action("TASK_SELECTION_MODE", f"Mode: random_assigned | Assigned task: {assigned_task}")
            self.log_action("TASK_ASSIGNED", f"System assigned task: {assigned_task} | Participant: {self.participant_id}")
            
        else:
            # Use default text for self-selection mode
            task_text = CONTENT_PERFORMANCE_TEXT
        
        instruction = tk.Label(
            self.main_frame,
            text=task_text,
            font=('Arial', 32),
            fg='white',
            bg=CONTENT_PERFORMANCE_BG_COLOR,
            wraplength=800,
            justify='center'
        )
        instruction.pack(pady=60)
        
        # Next button (always visible)
        next_button = tk.Button(
            self.main_frame,
            text="CONTINUE TO POST-STUDY REST",
            font=('Arial', 16, 'bold'),
            fg='black',
            bg='lightgreen',
            activebackground='green',
            width=25,
            height=2,
            command=self.on_content_performance_next
        )
        next_button.pack(pady=30)
        
        # Controls info (only show in developer mode)
        if DEVELOPER_MODE:
            if TASK_SELECTION_MODE == "random_assigned":
                control_text = "ENTER - Continue to Rest"
            else:
                control_text = "ENTER - Choose Task"
            
            controls = tk.Label(
                self.main_frame,
                text=control_text,
                font=('Arial', 16),
                fg='#B8D4F0',  # Lighter blue for secondary text
                bg=CONTENT_PERFORMANCE_BG_COLOR
            )
            controls.pack(side=tk.BOTTOM, pady=20)
        
        # Bind keys (only allow navigation in developer mode)
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_content_performance_enter)
        self.root.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        if TASK_SELECTION_MODE == "random_assigned":
            self.tech_print(f"✅ Content performance task screen ready - Task: {self.selected_task} - ENTER=rest")
        else:
            self.tech_print("✅ Content performance task screen ready - ENTER=choose task")
        self.log_action("SCREEN_DISPLAYED", "Content performance task screen displayed and ready")
    
    def on_content_performance_enter(self, event):
        """Handle Enter key in content performance task."""
        print("🎯 Enter pressed...")
        self.log_action("KEY_PRESS", "Enter key pressed in content performance task screen")
        self.log_action("CONTENT_PERFORMANCE_EXIT", "Exited content performance task screen")
        
        if TASK_SELECTION_MODE == "random_assigned":
            # Task already assigned in content performance setup, go directly to post-study rest
            print("🧘 Going directly to Post-Study Rest (task already assigned)...")
            self.switch_to_post_study_rest_with_transition()
        else:
            # Self-selection mode, go to task selection screen
            print("🎯 Going to Task Selection...")
            self.handle_task_selection()
    
    def on_content_performance_next(self):
        """Handle Next button in content performance task."""
        print("🎯 Next button pressed...")
        self.log_action("BUTTON_PRESS", "Continue to Post-Study Rest button pressed")
        self.log_action("CONTENT_PERFORMANCE_EXIT", "Exited content performance task screen via button")
        
        if TASK_SELECTION_MODE == "random_assigned":
            # Task already assigned in content performance setup, go directly to post-study rest
            print("🧘 Going directly to Post-Study Rest (task already assigned)...")
            self.switch_to_post_study_rest_with_transition()
        else:
            # Self-selection mode, go to task selection screen
            print("🎯 Going to Task Selection...")
            self.handle_task_selection()
    
    # =================== TASK SELECTION SYSTEM ===================
    
    def handle_task_selection(self):
        """Handle task selection based on configuration mode."""
        # This method is only called for self_selection mode now
        # (random_assigned mode is handled in content performance screen)
        
        if TASK_SELECTION_MODE == "self_selection":
            # Get current distribution stats before showing selection screen
            stats = self.get_task_distribution_stats()
            
            # Log task selection mode and current distribution
            self.log_action("TASK_SELECTION_MODE", f"Mode: self_selection | Current distribution - Total: {stats['total_assignments']}, Mandala: {stats['mandala_count']} ({stats['mandala_percent']}%), Diary: {stats['diary_count']} ({stats['diary_percent']}%), Mindfulness: {stats['mindfulness_count']} ({stats['mindfulness_percent']}%)")
            self.show_task_selection_screen()
        else:
            # This shouldn't happen anymore, but just in case
            print("⚠️ Warning: handle_task_selection called in random_assigned mode")
            self.switch_to_post_study_rest_with_transition()
    
    def show_task_selection_screen(self):
        """Show task selection screen for self-selection mode."""
        self.tech_print("🎯 Setting up Task Selection Screen")
        self.log_action("SCREEN_TRANSITION", "Setting up task selection screen")
        self.clear_screen()
        self.current_screen = "task_selection"
        
        # Set same blue background as content performance
        self.main_frame.configure(bg=CONTENT_PERFORMANCE_BG_COLOR)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="Choose Your Activity",
            font=('Arial', 32, 'bold'),
            fg='white',
            bg=CONTENT_PERFORMANCE_BG_COLOR
        )
        title.pack(pady=40)
        
        # Instruction text
        instruction = tk.Label(
            self.main_frame,
            text="You can choose among the tasks:",
            font=('Arial', 32),
            fg='white',
            bg=CONTENT_PERFORMANCE_BG_COLOR
        )
        instruction.pack(pady=20)
        
        # Task options with descriptions
        tasks_frame = tk.Frame(self.main_frame, bg=CONTENT_PERFORMANCE_BG_COLOR)
        tasks_frame.pack(pady=40)
        
        # Mandala option
        mandala_btn = tk.Button(
            tasks_frame,
            text="🎨 Mandala\n(drawing your figure)",
            font=('Arial', 24, 'bold'),
            fg='black',
            bg='#87CEEB',  # Sky blue
            activebackground='#B0E0E6',
            width=25,
            height=3,
            command=lambda: self.select_task("mandala")
        )
        mandala_btn.pack(pady=10)
        
        # Diary option
        diary_btn = tk.Button(
            tasks_frame,
            text="📝 Diary\n(journal down your mind)",
            font=('Arial', 24, 'bold'),
            fg='black',
            bg='#98FB98',  # Pale green
            activebackground='#90EE90',
            width=25,
            height=3,
            command=lambda: self.select_task("diary")
        )
        diary_btn.pack(pady=10)
        
        # Mindfulness option
        mindfulness_btn = tk.Button(
            tasks_frame,
            text="🧘 Mindfulness\n(watch a fun video)",
            font=('Arial', 24, 'bold'),
            fg='black',
            bg='#FFB6C1',  # Light pink
            activebackground='#FFC0CB',
            width=25,
            height=3,
            command=lambda: self.select_task("mindfulness")
        )
        mindfulness_btn.pack(pady=10)
        
        # Focus on first button
        mandala_btn.focus_set()
        
        if FOCUS_MODE:
            self.root.focus_force()
        
        print("✅ Task selection screen ready")
        self.log_action("SCREEN_DISPLAYED", "Task selection screen displayed and ready")
    
    def select_task(self, task_name):
        """Handle task selection by user."""
        print(f"🎯 User selected task: {task_name}")
        
        # Get distribution stats after selection
        # First, save the selection to get updated stats
        import json
        assignments_file = "/Users/hax429/Developer/Internship/moly/task_assignments.json"
        
        try:
            # Load and update assignments file
            with open(assignments_file, 'r') as f:
                data = json.load(f)
            
            data["assignments"][self.participant_id] = task_name
            
            with open(assignments_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving task selection: {e}")
        
        # Get updated stats
        updated_stats = self.get_task_distribution_stats()
        
        # Log detailed selection information
        self.log_action("TASK_SELECTED", f"User selected task: {task_name} | Participant: {self.participant_id} | Selection mode: self_selection")
        self.log_action("TASK_DISTRIBUTION_AFTER_SELECTION", f"After selection - Total: {updated_stats['total_assignments']}, Mandala: {updated_stats['mandala_count']} ({updated_stats['mandala_percent']}%), Diary: {updated_stats['diary_count']} ({updated_stats['diary_percent']}%), Mindfulness: {updated_stats['mindfulness_count']} ({updated_stats['mindfulness_percent']}%)")
        
        self.proceed_to_assigned_task(task_name)
    
    def get_task_distribution_stats(self):
        """Get current task distribution statistics."""
        import json
        
        assignments_file = "/Users/hax429/Developer/Internship/moly/task_assignments.json"
        
        try:
            with open(assignments_file, 'r') as f:
                data = json.load(f)
            
            assignments = data.get("assignments", {})
            total_assignments = len(assignments)
            
            if total_assignments == 0:
                return {
                    "total_assignments": 0,
                    "mandala_count": 0,
                    "diary_count": 0,
                    "mindfulness_count": 0,
                    "mandala_percent": 0,
                    "diary_percent": 0,
                    "mindfulness_percent": 0
                }
            
            # Count each task type
            task_counts = {"mandala": 0, "diary": 0, "mindfulness": 0}
            for task in assignments.values():
                if task in task_counts:
                    task_counts[task] += 1
            
            # Calculate percentages
            stats = {
                "total_assignments": total_assignments,
                "mandala_count": task_counts["mandala"],
                "diary_count": task_counts["diary"],
                "mindfulness_count": task_counts["mindfulness"],
                "mandala_percent": round((task_counts["mandala"] / total_assignments) * 100, 1),
                "diary_percent": round((task_counts["diary"] / total_assignments) * 100, 1),
                "mindfulness_percent": round((task_counts["mindfulness"] / total_assignments) * 100, 1)
            }
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Error calculating task distribution: {e}")
            return {
                "total_assignments": 0,
                "mandala_count": 0,
                "diary_count": 0,
                "mindfulness_count": 0,
                "mandala_percent": 0,
                "diary_percent": 0,
                "mindfulness_percent": 0
            }
    
    def get_random_assigned_task(self):
        """Get the next task in rotation for random assignment mode."""
        import json
        
        assignments_file = "/Users/hax429/Developer/Internship/moly/task_assignments.json"
        
        try:
            # Load current assignments
            with open(assignments_file, 'r') as f:
                data = json.load(f)
            
            # Get next task in rotation
            task_rotation = data["task_rotation"]
            last_index = data["last_assigned_index"]
            next_index = (last_index + 1) % len(task_rotation)
            assigned_task = task_rotation[next_index]
            
            # Update assignments
            data["last_assigned_index"] = next_index
            data["assignments"][self.participant_id] = assigned_task
            
            # Save updated assignments
            with open(assignments_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.tech_print(f"🎯 System assigned task: {assigned_task} (rotation index: {next_index})")
            return assigned_task
            
        except Exception as e:
            print(f"⚠️ Error in task assignment: {e}")
            # Default to mandala if there's an error
            return "mandala"
    
    def proceed_to_assigned_task(self, task_name):
        """Proceed to post-study rest with the assigned task information."""
        print(f"🧘 Proceeding to post-study rest with {task_name} task...")
        
        # Store the selected task for use in post-study rest
        self.selected_task = task_name
        
        # Get current distribution stats for session_info metadata
        distribution_stats = self.get_task_distribution_stats()
        
        # Add task selection metadata to session_info
        self.add_task_selection_to_session_info(task_name, TASK_SELECTION_MODE, distribution_stats)
        
        # Log the final task that will be performed
        task_descriptions = {
            "mandala": "drawing your figure",
            "diary": "journal down your mind", 
            "mindfulness": "watch a fun video"
        }
        
        description = task_descriptions.get(task_name, "unknown task")
        self.log_action("TASK_TO_PERFORM", f"Participant will perform: {task_name} ({description}) | Selection mode: {TASK_SELECTION_MODE}")
        
        self.switch_to_post_study_rest_with_transition()
    
    # =================== POST-STUDY REST SCREEN ===================
    
    def switch_to_post_study_rest_with_transition(self):
        """Switch to post-study rest screen with transition."""
        # Show transition screen first
        # Use content performance background color if transitioning from content performance
        bg_color = CONTENT_PERFORMANCE_BG_COLOR if self.current_screen == "content_performance" else None
        self.show_transition_screen(
            TRANSITION_MESSAGES['post_study_rest'],
            self.switch_to_post_study_rest,
            bg_color
        )
    
    def switch_to_post_study_rest(self):
        """Switch to post-study rest screen - same as relaxation but for post-study."""
        print("🧘 Switching to Post-Study Rest Screen")
        self.log_action("SCREEN_TRANSITION", "Switching to post-study rest screen")
        self.clear_screen()
        self.current_screen = "post_study_rest"
        self.running = True
        
        # Setup video canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.screen_width,
            height=self.screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create text overlay
        self.text_item = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2,
            text="Study Complete - Please Relax",
            font=('Arial', 48, 'bold'),
            fill=COLORS['text_primary']
        )
        
        # Initialize video (same as relaxation)
        self.init_video(self.relaxation_video)
        
        # Start video loop
        self.start_post_study_video_loop()
        
        # Bind keys
        self.root.bind_all('<KeyPress-q>', self.on_quit)
        self.root.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Start hidden countdown for automatic app closure
        self.start_post_study_countdown(RELAXATION_COUNTDOWN_MINUTES)
        
        print("✅ Post-study rest screen ready - Q=quit")
        self.log_action("SCREEN_DISPLAYED", "Post-study rest screen displayed and ready")
    
    def start_post_study_video_loop(self):
        """Start video loop for post-study rest screen."""
        def video_loop():
            while self.running and self.current_screen == "post_study_rest":
                try:
                    if self.running and hasattr(self, 'cap') and self.cap:
                        self.update_post_study_video_background()
                    time.sleep(1/30)  # 30 FPS
                except (tk.TclError, AttributeError):
                    # Window closed or object destroyed
                    break
        
        thread = threading.Thread(target=video_loop, daemon=True)
        thread.start()
    
    def update_post_study_video_background(self):
        """Update video background for post-study rest screen."""
        if self.current_screen != "post_study_rest":
            return
            
        try:
            new_frame = self.get_video_frame()
            if new_frame and hasattr(self, 'canvas'):
                # Remove old frame
                if hasattr(self, 'video_bg_item'):
                    self.canvas.delete(self.video_bg_item)
                
                # Add new frame as background, centered
                self.video_bg_item = self.canvas.create_image(
                    self.screen_width // 2, self.screen_height // 2, 
                    anchor=tk.CENTER, image=new_frame
                )
                # Keep reference to prevent garbage collection
                self.video_frame = new_frame
                
                # Bring text to front
                if hasattr(self, 'text_item'):
                    self.canvas.tag_raise(self.text_item)
        except (tk.TclError, AttributeError):
            # Canvas or window was destroyed
            pass
    
    def start_post_study_countdown(self, minutes):
        """Start hidden countdown for post-study rest screen auto-closure."""
        total_time = minutes * 60 * 1000  # Convert to milliseconds
        
        def auto_close():
            if self.current_screen == "post_study_rest":
                print(f"⏰ Post-study relaxation countdown finished - Auto-closing application")
                self.log_action("AUTO_CLOSE", f"Post-study relaxation countdown ({minutes} minutes) completed, closing application")
                self.on_quit()
        
        # Schedule the automatic closure
        self.root.after(total_time, auto_close)
        self.log_action("POST_STUDY_COUNTDOWN_STARTED", f"Hidden countdown started for {minutes} minutes before auto-close")
    
    # =================== COMMON VIDEO METHODS ===================
    
    def init_video(self, video_path, start_time=0):
        """Initialize video capture.
        
        Args:
            video_path: Path to the video file
            start_time: Starting time in seconds (default: 0)
        """
        if os.path.exists(video_path):
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                print(f"Warning: Could not open video file {video_path}")
                self.cap = None
            else:
                # Set starting position if specified
                if start_time > 0:
                    fps = self.cap.get(cv2.CAP_PROP_FPS)
                    start_frame = int(start_time * fps)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    print(f"✅ Video initialized: {os.path.basename(video_path)} (starting at {start_time}s)")
                else:
                    print(f"✅ Video initialized: {os.path.basename(video_path)}")
        else:
            print(f"Warning: Video file not found at {video_path}")
            self.cap = None
    
    def get_video_frame(self):
        """Get current video frame for relaxation screen."""
        try:
            if self.cap is None:
                return None
                
            ret, frame = self.cap.read()
            if not ret:
                # Loop video - restart from beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return None
            
            # Get original video dimensions
            video_height, video_width = frame.shape[:2]
            
            # Calculate aspect ratios
            video_aspect = video_width / video_height
            screen_aspect = self.screen_width / self.screen_height
            
            # Scale to fit screen while maintaining aspect ratio
            if video_aspect > screen_aspect:
                # Video is wider - scale by height
                new_height = self.screen_height
                new_width = int(self.screen_height * video_aspect)
            else:
                # Video is taller - scale by width
                new_width = self.screen_width
                new_height = int(self.screen_width / video_aspect)
            
            # Resize frame
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            # Convert to PhotoImage
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print(f"Warning: Error reading video frame: {e}")
            return None
    
    def update_video_background(self):
        """Update video background for relaxation screen."""
        if self.current_screen != "relaxation":
            return
            
        try:
            new_frame = self.get_video_frame()
            if new_frame and hasattr(self, 'canvas'):
                # Remove old frame
                if hasattr(self, 'video_bg_item'):
                    self.canvas.delete(self.video_bg_item)
                
                # Add new frame as background, centered
                self.video_bg_item = self.canvas.create_image(
                    self.screen_width // 2, self.screen_height // 2, 
                    anchor=tk.CENTER, image=new_frame
                )
                # Keep reference to prevent garbage collection
                self.video_frame = new_frame
                
                # Bring text to front if it exists
                if hasattr(self, 'text_item'):
                    self.canvas.tag_raise(self.text_item)
        except (tk.TclError, AttributeError):
            # Canvas or window was destroyed
            pass
    
    def start_video_loop(self):
        """Start video loop for relaxation screen."""
        def video_loop():
            while self.running and self.current_screen == "relaxation":
                try:
                    if self.running and hasattr(self, 'cap') and self.cap:
                        self.update_video_background()
                    time.sleep(1/30)  # 30 FPS
                except (tk.TclError, AttributeError):
                    # Window closed or object destroyed
                    break
        
        thread = threading.Thread(target=video_loop, daemon=True)
        thread.start()
    
    # =================== COMMON METHODS ===================
    
    def on_quit(self, event):
        """Handle Q key - quit application."""
        print("🔌 Q pressed - Quitting application...")
        self.log_action("KEY_PRESS", "Q key pressed - quitting application")
        self.quit_app()
    
    def quit_app(self):
        """Clean shutdown of application."""
        print("🔌 Shutting down Moly application...")
        self.log_action("APPLICATION_EXIT", "Application shutting down")

        # Mark that we've logged the exit (for crash detection)
        self._exit_logged = True

        self.finalize_session()
        self.running = False

        # Wait a moment for threads to finish
        time.sleep(0.2)
        
        # Clean up video resources
        if hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except Exception as e:
                print(f"Warning: Error releasing video capture during shutdown: {e}")
            finally:
                self.cap = None
        
        # Clear video frame reference
        if hasattr(self, 'video_frame'):
            self.video_frame = None
        
        # Destroy window
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Warning: Error destroying window: {e}")
    
    # =================== COUNTDOWN TIMER METHODS ===================
    
    def start_countdown(self, minutes, screen_name):
        """Start countdown timer for a screen with milliseconds precision."""
        if not self.countdown_enabled:
            return
        
        # Stop any existing countdown first
        self.stop_countdown()
        
        self.countdown_remaining = minutes * 60 * 1000  # Convert to milliseconds
        self.countdown_running = True
        
        # Record start time for accurate timing
        import time
        start_time = time.time() * 1000  # Get current time in milliseconds
        initial_countdown = self.countdown_remaining
        
        def countdown_loop():
            while (self.countdown_remaining > 0 and 
                   self.countdown_running and 
                   self.current_screen == screen_name):
                try:
                    if self.countdown_running:  # Double-check before updating
                        # Calculate actual elapsed time and update countdown
                        current_time = time.time() * 1000
                        elapsed = current_time - start_time
                        self.countdown_remaining = max(0, initial_countdown - int(elapsed))
                        
                        self.update_countdown_display()

                        # Log countdown state every 30 seconds for recovery
                        seconds_remaining = self.countdown_remaining // 1000
                        if seconds_remaining % 30 == 0 and self.countdown_remaining % 1000 < 100:
                            total_seconds = minutes * 60
                            self.log_countdown_state(seconds_remaining, total_seconds)

                    time.sleep(0.01)  # Update every 10ms for smooth display
                except (tk.TclError, AttributeError):
                    break
            
            # Time's up notification
            if (self.countdown_remaining <= 0 and 
                self.countdown_running and 
                self.current_screen == screen_name):
                try:
                    self.root.after(0, self.show_timeout_notification, screen_name)
                except (tk.TclError, AttributeError):
                    pass
        
        self.countdown_thread = threading.Thread(target=countdown_loop, daemon=True)
        self.countdown_thread.start()
    
    def update_countdown_display(self):
        """Update the countdown display with milliseconds precision."""
        if not self.countdown_label or not self.countdown_enabled or not self.countdown_running:
            return
        
        # Convert milliseconds to minutes, seconds, and milliseconds
        total_seconds = self.countdown_remaining // 1000
        milliseconds = (self.countdown_remaining % 1000) // 10  # Show centiseconds (0-99)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # Create stressful message based on remaining time (in milliseconds)
        if self.countdown_remaining > 60000:  # More than 1 minute
            stress_msg = f"⏰ You only have {minutes:01d}:{seconds:02d}.{milliseconds:02d} left!"
        elif self.countdown_remaining > 30000:  # 30-60 seconds
            stress_msg = f"⚠️ HURRY! Only {seconds}.{milliseconds:02d} seconds remaining!"
        elif self.countdown_remaining > 10000:  # 10-30 seconds
            stress_msg = f"🚨 CRITICAL! {seconds}.{milliseconds:02d} seconds left!"
        else:  # Less than 10 seconds
            stress_msg = f"🚨 TIME RUNNING OUT! {seconds}.{milliseconds:02d}s!"
        
        # Color based on urgency (using milliseconds)
        if self.countdown_remaining > 120000:  # More than 2 minutes
            color = '#ffaa44'
        elif self.countdown_remaining > 60000:  # 1-2 minutes
            color = '#ff6666'
        else:  # Less than 1 minute
            color = '#ff0000'
        
        self.root.after(0, self.update_countdown_label, stress_msg, color)
    
    def update_countdown_label(self, text, color):
        """Update countdown label safely in main thread."""
        if self.countdown_label and self.countdown_running:
            try:
                # Double-check the label still exists before updating
                if hasattr(self.countdown_label, 'config'):
                    self.countdown_label.config(text=text, fg=color)
            except (tk.TclError, AttributeError):
                # Label was destroyed, stop trying to update it
                self.countdown_label = None
    
    def show_timeout_notification(self, screen_name):
        """Show timeout notification and handle automatic transitions."""
        print(f"⏰ TIME'S UP for {screen_name} screen!")
        
        if DEVELOPER_MODE:
            # In developer mode, just show the timeout notification
            if self.countdown_label:
                self.countdown_label.config(
                    text="🚨 TIME'S UP! EVALUATION COMPLETE!",
                    fg='#ff0000',
                    font=('Arial', 20, 'bold')
                )
        else:
            # In production mode, automatically transition to next screen
            self.handle_automatic_timeout_transition(screen_name)
    
    def handle_automatic_timeout_transition(self, screen_name):
        """Handle automatic transitions when countdown expires in production mode."""
        print(f"🔄 Auto-transitioning from {screen_name} due to timeout...")
        self.log_action("AUTO_TIMEOUT_TRANSITION", f"Time expired on {screen_name}, automatically transitioning")
        
        if screen_name == "descriptive_task":
            # Show timeout message
            if hasattr(self, 'countdown_label'):
                self.countdown_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
            
            # Disable editing in descriptive writing task
            if hasattr(self, 'response_text'):
                self.response_text.config(state='disabled', bg='lightgray', fg='gray')
            
            # Save any current response before transitioning
            if hasattr(self, 'response_text'):
                current_response = self.response_text.get("1.0", tk.END).strip()
                if current_response:
                    current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                    self.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)
            
            # Transition to Stroop task
            self.root.after(2000, self.switch_to_stroop)  # 2 second delay for user awareness
            
        elif screen_name == "stroop":
            # Show timeout message on countdown label
            if hasattr(self, 'countdown_label'):
                self.countdown_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
            
            # Stop the video
            self.is_playing = False
            self.is_paused = True
            if hasattr(self, 'status_label'):
                self.status_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
            
            # Transition to Math task
            self.root.after(2000, self.switch_to_math_task)  # 2 second delay
            
        elif screen_name == "math_task":
            # Show timeout message on countdown label
            if hasattr(self, 'countdown_label'):
                self.countdown_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
            
            # Show completion message on math prompt
            if hasattr(self, 'math_prompt'):
                self.math_prompt.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
            
            # Transition to Content Performance task
            self.root.after(2000, self.switch_to_content_performance_task)  # 2 second delay
    
    def stop_countdown(self):
        """Stop the current countdown safely."""
        # Signal countdown to stop
        self.countdown_running = False
        
        # Wait for thread to finish with timeout
        if self.countdown_thread and self.countdown_thread.is_alive():
            try:
                self.countdown_thread.join(timeout=0.5)
            except:
                pass
        
        # Clear the thread reference
        self.countdown_thread = None
    
    def show_transition_screen(self, message, callback, bg_color=None):
        """Show a full-screen transition screen when transitioning between screens."""
        print(f"🚨 TRANSITION: {message}")
        self.log_action("TRANSITION_SCREEN_DISPLAYED", f"Transition screen shown: {message[:50]}...")
        self.clear_screen()
        self.current_screen = "transition"
        
        # Use provided background color or default
        transition_bg = bg_color if bg_color else BACKGROUND_COLOR
        self.main_frame.configure(bg=transition_bg)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="⚠️ EVALUATION NOTICE ⚠️",
            font=('Arial', 36, 'bold'),
            fg=COLORS['title'],
            bg=transition_bg
        )
        title.pack(pady=50)
        
        # Instruction text
        instruction = tk.Label(
            self.main_frame,
            text=TRANSITION_INSTRUCTION_TEXT,
            font=('Arial', 32),
            fg=COLORS['text_accent'],
            bg=transition_bg,
            wraplength=800,
            justify='center'
        )
        instruction.pack(pady=30)
        
        # Transition message
        message_label = tk.Label(
            self.main_frame,
            text=message,
            font=('Arial', 20),
            fg=COLORS['text_primary'],
            bg=transition_bg,
            wraplength=900,
            justify='center'
        )
        message_label.pack(pady=40, expand=True)
        
        # Confirmation prompt
        confirm_prompt = tk.Label(
            self.main_frame,
            text="You MUST confirm to proceed with the evaluation:",
            font=('Arial', 18, 'bold'),
            fg=COLORS['warning'],
            bg=transition_bg
        )
        confirm_prompt.pack(pady=20)
        
        # Confirmation button
        def confirm_and_proceed():
            try:
                self.log_action("TRANSITION_CONFIRMED", "User confirmed transition - proceeding to next screen")
                # Execute the callback to actually perform the screen transition
                callback()
                # Restore focus in focus mode
                if FOCUS_MODE:
                    self.root.focus_force()
                    self.root.lift()
            except Exception as e:
                print(f"Error in transition: {e}")
        
        confirm_button = tk.Button(
            self.main_frame,
            text="I UNDERSTAND - PROCEED",
            font=('Arial', 16, 'bold'),
            fg='black',
            bg=COLORS['button_bg'],
            activebackground=COLORS['button_active'],
            activeforeground='black',
            width=30,
            height=3,
            command=confirm_and_proceed
        )
        confirm_button.pack(pady=30)
        
        # Focus on the button
        confirm_button.focus_set()
        if FOCUS_MODE:
            self.root.focus_force()
    
    def run(self):
        """Run the application."""
        try:
            print("🚀 Starting Moly Relaxation Application")
            print("📖 Current screen: Relaxation")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🔌 Keyboard interrupt - Shutting down...")
            self.quit_app()
        finally:
            # Final cleanup
            if hasattr(self, 'cap') and self.cap:
                try:
                    self.cap.release()
                except:
                    pass

def main():
    """Main entry point."""
    print("🧘 Moly - Relaxation Experience")
    print("=" * 40)
    
    app = MolyApp()
    app.run()
    
    print("👋 Thanks for using Moly!")

if __name__ == '__main__':
    main()