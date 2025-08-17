#!/usr/bin/env python3

import tkinter as tk
import threading
import time
import random
import os
import signal
import atexit
import json
from datetime import datetime, timezone

# Import configuration and managers
from config import *
from logging_manager import LoggingManager
from recovery_manager import RecoveryManager
from video_manager import VideoManager
from countdown_manager import CountdownManager
from task_manager import TaskManager


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
        
        # Initialize managers
        self.logging_manager = LoggingManager()
        self.recovery_manager = RecoveryManager(self.logging_manager)
        self.video_manager = VideoManager()
        self.countdown_manager = CountdownManager(self.logging_manager)
        self.task_manager = TaskManager(self.logging_manager)
        
        # Configure managers
        self.video_manager.set_screen_dimensions(self.screen_width, self.screen_height)
        self.countdown_manager.set_current_screen_callback(lambda: self.current_screen)
        self.countdown_manager.set_timeout_callback(self.show_timeout_notification)
        self.countdown_manager.set_root_after_callback(self.root.after)
        self.countdown_manager.set_enabled(COUNTDOWN_ENABLED)
        
        # Descriptive task properties
        self.current_prompt_index = 0
        self.prompts = DESCRIPTIVE_PROMPTS.copy()
        
        # Math task properties
        self.current_number = MATH_STARTING_NUMBER
        self.math_history = []

        # Font settings for descriptive task
        self.descriptive_font_size = 16
        self.descriptive_font_family = 'Arial'
        
        # Task start flags
        self.descriptive_task_started = False
        self.stroop_task_started = False
        self.math_task_started = False
        
        # Text tracking for sentence logging
        self.last_sentence_position = 0
        self._last_text_length = 0
        self._last_logged_length = 0
        
        # Create main container
        self.setup_main_ui()

        # Set up crash detection
        self.setup_crash_detection()

        # Check for incomplete sessions before showing participant ID screen
        self.check_and_handle_recovery()

    def setup_crash_detection(self):
        """Set up crash detection and logging."""
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
        if hasattr(self.logging_manager, 'action_log_file_path') and self.logging_manager.action_log_file_path:
            try:
                crash_data = {
                    "timestamp": {
                        "local": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "utc": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "unix": time.time()
                    },
                    "participant_id": self.participant_id or 'UNKNOWN',
                    "action_type": "APPLICATION_CRASH",
                    "details": f"Application crashed with signal {signum}",
                    "screen": self.current_screen,
                    "session_duration_seconds": (datetime.now() - self.logging_manager.session_start_time).total_seconds()
                }

                with open(self.logging_manager.action_log_file_path, 'a') as f:
                    f.write(json.dumps(crash_data) + '\n')

                print("💾 Crash logged to file")
            except Exception as e:
                print(f"⚠️ Could not log crash: {e}")

        # Clean up and exit
        self.cleanup_resources()
        exit(1)

    def handle_app_exit(self):
        """Handle normal app exit."""
        if hasattr(self.logging_manager, 'action_log_file_path') and self.logging_manager.action_log_file_path:
            try:
                if not hasattr(self, '_exit_logged'):
                    print("🔚 Normal app exit detected")
            except:
                pass

    def cleanup_resources(self):
        """Clean up all resources."""
        try:
            self.video_manager.cleanup()
        except:
            pass

    def check_and_handle_recovery(self):
        """Check for incomplete sessions and handle recovery."""
        try:
            incomplete_session = self.recovery_manager.check_for_incomplete_sessions()
            if incomplete_session:
                print(f"🔄 Found incomplete session for {incomplete_session['participant_id']}")
                self.show_recovery_dialog(incomplete_session)
            else:
                self.show_participant_id_screen()
        except Exception as e:
            print(f"⚠️ Error during recovery check: {e}")
            self.show_participant_id_screen()
        
    def setup_main_ui(self):
        """Setup the main UI container."""
        self.main_frame = tk.Frame(self.root, bg=MAIN_FRAME_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def clear_screen(self):
        """Clear current screen content."""
        # Stop countdown timer first
        self.countdown_manager.stop_countdown()
        
        # Stop video if running
        self.video_manager.stop_video()
        
        # Clean up corner countdown if it exists
        if hasattr(self, 'corner_countdown_label'):
            try:
                self.corner_countdown_label.destroy()
                del self.corner_countdown_label
            except (tk.TclError, AttributeError):
                pass
            # Clear the reference in countdown manager
            self.countdown_manager.set_corner_countdown_label(None)
        
        # Clear all widgets from main frame safely
        if hasattr(self, 'main_frame'):
            try:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
            except tk.TclError:
                pass
        
        # Clear all key bindings
        keys_to_unbind = ['<KeyPress-space>', '<KeyPress-n>', '<KeyPress-N>', '<KeyPress-r>', 
                          '<KeyPress-R>', '<KeyPress-m>', '<KeyPress-M>', '<KeyPress-Escape>', 
                          '<KeyPress-q>', '<Return>', '<Control-Return>', '<Alt-Command-n>', 
                          '<Alt-Command-N>', '<Option-Command-n>', '<Option-Command-N>', 
                          '<Command-Alt-n>', '<Command-Alt-N>', '<Command-n>', '<Command-N>']
        
        for key in keys_to_unbind:
            self.root.unbind_all(key)
    
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
            insertbackground='black',
            selectbackground='lightblue',
            selectforeground='black',
            validate='key',
            validatecommand=validate_cmd
        )
        id_entry.pack(pady=20)
        id_entry.focus_set()
        
        # Bind key events to convert to uppercase
        def on_key_press(event):
            if event.char.isalpha():
                current_pos = id_entry.index(tk.INSERT)
                current_text = self.participant_id_var.get()
                new_text = current_text[:current_pos] + event.char.upper() + current_text[current_pos:]
                self.participant_id_var.set(new_text)
                id_entry.icursor(current_pos + 1)
                return 'break'
        
        id_entry.bind('<KeyPress>', on_key_press)
        
        # Submit button
        def submit_participant_id():
            participant_id = self.participant_id_var.get().strip()
            if participant_id:
                self.set_participant_id(participant_id)
                self.logging_manager.log_action("PARTICIPANT_ID_SUBMITTED", f"Participant ID: {participant_id}", self.current_screen)
                
                # Show consent screen if enabled, otherwise go directly to relaxation
                if CONSENT_ENABLED:
                    self.switch_to_consent()
                else:
                    self.switch_to_relaxation()
            else:
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
        self.root.bind_all('<Return>', lambda event: submit_participant_id())
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        print("✅ Participant ID screen ready")
    
    def set_participant_id(self, participant_id):
        """Set the participant ID and create log files."""
        self.participant_id = participant_id
        self.logging_manager.setup_logging_for_participant(participant_id)
        
        # Assign task based on configuration mode
        if TASK_SELECTION_MODE == "random_assigned":
            self.selected_task = self.task_manager.get_random_assigned_task(participant_id)
            print(f"🎯 Assigned task: {self.selected_task}")
            self.logging_manager.log_action("TASK_ASSIGNMENT", f"Randomly assigned task: {self.selected_task}", self.current_screen)
        else:
            # In self-selection mode, task will be set later during task selection screen
            self.selected_task = None
    
    # =================== CONSENT SCREEN ===================
    
    def switch_to_consent(self):
        """Switch to consent screen with PDF display."""
        print("📋 Switching to Consent Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Switching to consent screen", self.current_screen)
        self.clear_screen()
        self.current_screen = "consent"
        
        # Set neutral background for consent screen
        self.main_frame.configure(bg='white')
        
        # Title
        title = tk.Label(
            self.main_frame,
            text=CONSENT_TITLE,
            font=('Arial', 28, 'bold'),
            fg='black',
            bg='white'
        )
        title.pack(pady=20)
        
        # Instructions
        instruction = tk.Label(
            self.main_frame,
            text=CONSENT_INSTRUCTION,
            font=('Arial', 16),
            fg='black',
            bg='white',
            wraplength=800,
            justify='center'
        )
        instruction.pack(pady=10)
        
        # Create scrollable frame for PDF content
        self.setup_pdf_display()
        
        # Agreement text
        agreement_text = tk.Label(
            self.main_frame,
            text=CONSENT_AGREEMENT_TEXT,
            font=('Arial', 14, 'bold'),
            fg='red',
            bg='white',
            wraplength=600,
            justify='center'
        )
        agreement_text.pack(pady=(20, 10))
        
        # Consent button (initially disabled if scroll required)
        self.consent_button = tk.Button(
            self.main_frame,
            text=CONSENT_BUTTON_TEXT,
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='green' if not CONSENT_SCROLL_REQUIRED else 'gray',
            state='normal' if not CONSENT_SCROLL_REQUIRED else 'disabled',
            width=25,
            height=2,
            command=self.on_consent_given
        )
        self.consent_button.pack(pady=20)
        
        # Focus management
        if FOCUS_MODE:
            self.root.focus_force()
        
        print("✅ Consent screen ready")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Consent screen displayed and ready", self.current_screen)
    
    def setup_pdf_display(self):
        """Set up the PDF display area with scrolling."""
        # Create frame for PDF content
        pdf_frame = tk.Frame(self.main_frame, bg='white', relief='sunken', borderwidth=2)
        pdf_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(pdf_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(pdf_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Load and display PDF content
        self.load_pdf_content(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Set up scroll detection if required
        if CONSENT_SCROLL_REQUIRED:
            self.setup_scroll_detection()
        
        # Store references
        self.pdf_canvas = canvas
        self.pdf_scrollbar = scrollbar
    
    def load_pdf_content(self, parent_frame):
        """Load and display PDF content."""
        try:
            # Try to load PDF content
            pdf_content = self.read_pdf_file(CONSENT_PDF_PATH)
            
            # Display content in a text widget
            text_widget = tk.Text(
                parent_frame,
                wrap=tk.WORD,
                font=('Arial', 11),
                bg='white',
                fg='black',
                relief='flat',
                state='normal',
                height=25
            )
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Insert content
            text_widget.insert('1.0', pdf_content)
            text_widget.config(state='disabled')  # Make read-only
            
            # Store reference for scroll detection
            self.pdf_text_widget = text_widget
            
        except Exception as e:
            print(f"⚠️ Error loading PDF content: {e}")
            # Show error message
            error_label = tk.Label(
                parent_frame,
                text=f"Error loading PDF: {e}\n\nPlease check that {CONSENT_PDF_PATH} exists.",
                font=('Arial', 12),
                fg='red',
                bg='white',
                wraplength=600,
                justify='center'
            )
            error_label.pack(pady=50)
    
    def read_pdf_file(self, pdf_path):
        """Read PDF file content and return as text."""
        try:
            import os
            
            # Get absolute path
            abs_path = os.path.abspath(pdf_path)
            
            if os.path.exists(abs_path):
                try:
                    # Try to extract actual PDF content using PyPDF2
                    import PyPDF2
                    
                    pdf_text = ""
                    with open(abs_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        
                        # Extract text from all pages
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            pdf_text += page.extract_text() + "\n\n"
                    
                    # Clean up the text
                    pdf_text = pdf_text.strip()
                    
                    if pdf_text:
                        return pdf_text
                    else:
                        return f"PDF file exists but no text could be extracted from {pdf_path}.\n\nThis may be a scanned PDF or contain only images."
                        
                except ImportError:
                    return f"PyPDF2 library not available. Cannot extract text from {pdf_path}.\n\nPlease install PyPDF2 to read PDF content."
                except Exception as pdf_error:
                    return f"Error reading PDF {pdf_path}: {pdf_error}\n\nThe file may be corrupted or password protected."
            else:
                return f"ERROR: PDF file not found at {abs_path}"
                
        except Exception as e:
            return f"ERROR reading PDF file: {str(e)}"
    
    def setup_scroll_detection(self):
        """Set up scroll detection to enable consent button when user scrolls to bottom."""
        def on_scroll(*args):
            # Get scroll position from text widget
            if hasattr(self, 'pdf_text_widget'):
                # Get the view of the text widget
                top, bottom = self.pdf_text_widget.yview()
                
                # Enable button when scrolled near the bottom (95% or more)
                if bottom >= 0.95:
                    self.consent_button.config(state='normal', bg='green')
                    print("📋 User scrolled to bottom - consent button enabled")
                    self.logging_manager.log_action("CONSENT_SCROLL_COMPLETE", "User scrolled to bottom of consent document", self.current_screen)
        
        # Set up periodic check for scroll position
        def check_scroll():
            on_scroll()
            self.root.after(100, check_scroll)  # Check every 100ms
        
        # Start checking
        self.root.after(500, check_scroll)  # Start after 500ms delay
    
    def on_consent_given(self):
        """Handle when user gives consent."""
        print("✅ User gave consent - proceeding to relaxation")
        self.logging_manager.log_action("CONSENT_GIVEN", "User clicked consent button", self.current_screen)
        self.switch_to_relaxation()
    
    # =================== RECOVERY FUNCTIONALITY ===================
    
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
        from datetime import datetime
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
        
        # Set up session using recovery manager
        self.recovery_manager.setup_recovery_session(
            recovery_data, 
            lambda start_time: setattr(self.logging_manager, 'session_start_time', start_time)
        )
        
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
            self.show_recovery_notification(f"Restored {len(completed_responses)} previous responses")

    def reset_and_restore_descriptive(self, recovery_data):
        """Reset responses and countdown but restore to descriptive task."""
        print(f"🔄 Resetting and restoring descriptive task for participant {recovery_data['participant_id']}")
        
        # Set up session using recovery manager
        self.recovery_manager.setup_recovery_session(
            recovery_data, 
            lambda start_time: setattr(self.logging_manager, 'session_start_time', start_time)
        )
        
        # Reset descriptive task state
        self.current_prompt_index = 0
        self.prompts = DESCRIPTIVE_PROMPTS.copy()
        
        # Clear recovery state
        self.recovery_manager.reset_recovery_state()
        
        # Log the reset action
        self.logging_manager.log_action("RECOVERY_RESET_RESTORE", "User chose to reset responses and countdown, restoring to descriptive task", self.current_screen)
        
        # Go directly to descriptive task setup
        self._setup_descriptive_task()
        
        # Show notification
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
        self.root.after(3000, notification.destroy)

    def start_new_session(self):
        """Start a new session (normal flow)."""
        print("🆕 Starting new session")
        self.show_participant_id_screen()
    
    # =================== RELAXATION SCREEN ===================
    
    def switch_to_relaxation(self):
        """Switch to relaxation screen with video background."""
        print("🧘 Switching to Relaxation Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Switching to relaxation screen", self.current_screen)
        self.clear_screen()
        self.current_screen = "relaxation"
        
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
        text_item = None
        if SHOW_RELAXATION_TEXT:
            text_item = self.canvas.create_text(
                self.screen_width // 2, self.screen_height // 2,
                text=RELAXATION_TEXT,
                font=('Arial', 48, 'bold'),
                fill=COLORS['text_primary']
            )
        
        # Initialize and start video
        self.video_manager.init_video(RELAXATION_VIDEO_PATH)
        
        # Set up video completion callback for auto-transition
        self.video_manager.set_video_end_callback(lambda: self.on_relaxation_video_end())
        
        self.video_manager.start_video_loop(self.canvas, lambda: self.current_screen, text_item)
        
        # Bind keys
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_relaxation_enter)
        self.root.bind_all('<KeyPress-q>', self.on_quit)
        self.root.focus_set()
        
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Start hidden countdown for automatic transition
        self.start_relaxation_countdown(RELAXATION_COUNTDOWN_MINUTES)
        
        print("✅ Relaxation screen ready")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Relaxation screen displayed and ready", self.current_screen)
    
    def on_relaxation_enter(self, event):
        """Handle Enter key in relaxation screen."""
        print("🎯 Enter pressed - Going to Descriptive Task screen...")
        self.logging_manager.log_action("KEY_PRESS", "Enter key pressed in relaxation screen", self.current_screen)
        self.switch_to_descriptive_task()
    
    def on_relaxation_video_end(self):
        """Handle when relaxation video reaches its natural end."""
        if self.current_screen == "relaxation":
            print("🎬 Relaxation video finished - Auto-transitioning to descriptive task")
            self.logging_manager.log_action("VIDEO_END_TRANSITION", "Relaxation video completed, automatically transitioning to descriptive task", self.current_screen)
            self.switch_to_descriptive_task()
    
    def start_relaxation_countdown(self, minutes):
        """Start hidden countdown for relaxation screen auto-transition."""
        total_time = minutes * 60 * 1000
        
        def auto_transition():
            if self.current_screen == "relaxation":
                print(f"⏰ Relaxation countdown finished - Auto-transitioning to descriptive task")
                self.logging_manager.log_action("AUTO_TRANSITION", f"Relaxation countdown ({minutes} minutes) completed, transitioning to descriptive task", self.current_screen)
                self.switch_to_descriptive_task()
        
        self.root.after(total_time, auto_transition)
        self.logging_manager.log_action("RELAXATION_COUNTDOWN_STARTED", f"Hidden countdown started for {minutes} minutes", self.current_screen)
    
    # =================== COMMON METHODS ===================
    
    def on_quit(self, event=None):
        """Handle Q key - quit application."""
        print("🔌 Q pressed - Quitting application...")
        self.logging_manager.log_action("KEY_PRESS", "Q key pressed - quitting application", self.current_screen)
        self.quit_app()
    
    def quit_app(self):
        """Clean shutdown of application."""
        print("🔌 Shutting down Moly application...")
        self.logging_manager.log_action("APPLICATION_EXIT", "Application shutting down", self.current_screen)

        # Mark that we've logged the exit
        self._exit_logged = True

        self.logging_manager.finalize_session()
        self.running = False

        # Wait for threads to finish
        time.sleep(0.2)
        
        # Clean up resources
        self.cleanup_resources()
        
        # Destroy window
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Warning: Error destroying window: {e}")

    # =================== PLACEHOLDER METHODS (TO BE IMPLEMENTED) ===================
    
    def switch_to_descriptive_task(self):
        """Switch to descriptive task screen."""
        # Show transition screen first
        self.show_transition_screen(
            TRANSITION_MESSAGES['descriptive'],
            self._setup_descriptive_task
        )
    
    def _setup_descriptive_task(self):
        """Actually setup the descriptive task screen after confirmation."""
        print("🎯 Setting up Descriptive Task Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Setting up descriptive task screen", self.current_screen)
        self.clear_screen()
        self.current_screen = "descriptive_task"
        
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
        if COUNTDOWN_ENABLED and DESCRIPTIVE_COUNTDOWN_ENABLED:
            countdown_label = tk.Label(
                self.main_frame,
                text=f"⏰ You only have {DESCRIPTIVE_COUNTDOWN_MINUTES} minutes left!",
                font=('Arial', 16, 'bold'),
                fg=COLORS['countdown_normal'],
                bg=BACKGROUND_COLOR
            )
            countdown_label.pack(pady=10)
            
            # Set up countdown with countdown manager
            self.countdown_manager.setup_countdown_label(countdown_label)
            
            # Add corner countdown timer (top-right)
            self.setup_corner_countdown()
        
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
            insertbackground='black',
            insertwidth=2,
            selectbackground='lightblue',
            selectforeground='black',
            state='disabled'  # Initially disabled
        )
        
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=scrollbar.set)
        
        self.response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Word count display
        self.word_count_label = tk.Label(
            response_frame,
            text="Word count: 0",
            font=('Arial', 14),
            fg=COLORS['text_accent'],
            bg=BACKGROUND_COLOR
        )
        self.word_count_label.pack(anchor='e', pady=(5, 0))
        
        # Controls info (only show in developer mode)
        if DEVELOPER_MODE:
            controls = tk.Label(
                self.main_frame,
                text="ENTER - Stroop Task",
                font=('Arial', 14),
                fg=COLORS['text_secondary'],
                bg=BACKGROUND_COLOR
            )
            controls.pack(pady=10)
        
        # Bind keys (only allow navigation in developer mode OR when countdown has finished)
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_descriptive_enter)
        
        # Set initial focus to the start button
        self.descriptive_start_button.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Don't start countdown automatically - will start when user clicks START button
        # Initialize task as not started
        self.descriptive_task_started = False
        
        print("✅ Descriptive task screen ready")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Descriptive task screen displayed and ready", self.current_screen)
    
    def start_descriptive_task(self):
        """Start the descriptive task - enable textbox and start countdown."""
        if self.descriptive_task_started:
            return  # Already started
        
        print("🚀 Starting descriptive task...")
        self.logging_manager.log_action("TASK_STARTED", "Descriptive task started by user", self.current_screen)
        
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
        
        # Set up word count tracking
        self.setup_word_count_tracking()
        
        # Show the first prompt
        self.show_current_prompt()
        
        # Set focus to textbox
        self.response_text.focus_set()
        
        # Start countdown timer (if enabled)
        if COUNTDOWN_ENABLED and DESCRIPTIVE_COUNTDOWN_ENABLED:
            self.countdown_manager.start_countdown(DESCRIPTIVE_COUNTDOWN_MINUTES, "descriptive_task")
            
            if DEVELOPER_MODE:
                # In developer mode, auto-transition when countdown finishes
                self.countdown_manager.set_countdown_finish_callback(self.auto_transition_from_descriptive)
            else:
                # In production mode, enable Enter key only when countdown finishes
                self.countdown_manager.set_countdown_finish_callback(self.enable_descriptive_navigation)
    
    def show_current_prompt(self):
        """Show current descriptive prompt."""
        if self.current_prompt_index < len(self.prompts):
            prompt = self.prompts[self.current_prompt_index]
            self.prompt_label.config(text=prompt)
        else:
            self.prompt_label.config(text="Great job! You've completed all the descriptive tasks.")
    
    def setup_word_count_tracking(self):
        """Set up word count tracking for the descriptive response text."""
        def update_word_count(event=None):
            try:
                # Get text content
                text_content = self.response_text.get("1.0", tk.END)
                # Remove trailing newline and split into words
                words = text_content.strip().split()
                # Filter out empty strings
                word_count = len([word for word in words if word.strip()])
                # Update the label
                self.word_count_label.config(text=f"Word count: {word_count}")
            except:
                # If there's any error, just show 0
                self.word_count_label.config(text="Word count: 0")
        
        # Bind to various text change events
        self.response_text.bind('<KeyRelease>', update_word_count)
        self.response_text.bind('<Button-1>', update_word_count)  # Mouse click
        self.response_text.bind('<Control-v>', lambda e: self.root.after(10, update_word_count))  # Paste
        
        # Initial word count
        update_word_count()
    
    def setup_corner_countdown(self):
        """Set up the prominent corner countdown timer."""
        # Create corner countdown label with absolute positioning
        corner_countdown = tk.Label(
            self.root,  # Place on root instead of main_frame for absolute positioning
            text="0:00",
            font=('Arial', 48, 'bold'),  # Large, prominent font
            fg='#00FF00',  # Bright green initially
            bg=BACKGROUND_COLOR,
            relief='solid',
            borderwidth=2,
            padx=10,
            pady=5
        )
        
        # Position in top-right corner
        corner_countdown.place(x=self.screen_width-200, y=20, anchor='ne')
        
        # Set up with countdown manager
        self.countdown_manager.set_corner_countdown_label(corner_countdown)
        
        # Store reference to clean up later
        self.corner_countdown_label = corner_countdown
    
    def enable_descriptive_navigation(self):
        """Enable navigation for descriptive task when countdown finishes (production mode)."""
        if not DEVELOPER_MODE and self.current_screen == "descriptive_task":
            self.root.bind_all('<Return>', self.on_descriptive_enter)
            print("🔓 Navigation enabled - Press ENTER for Stroop Task")
    
    def auto_transition_from_descriptive(self):
        """Auto-transition from descriptive task when countdown finishes (developer mode)."""
        if DEVELOPER_MODE and self.current_screen == "descriptive_task":
            print("⏰ Descriptive task countdown finished - Auto-transitioning to Stroop task")
            self.logging_manager.log_action("AUTO_TRANSITION", "Descriptive task countdown completed in developer mode, automatically transitioning to stroop", self.current_screen)
            
            # Save final response before leaving descriptive task
            if hasattr(self, 'response_text'):
                try:
                    current_response = self.response_text.get("1.0", tk.END).strip()
                    if current_response:
                        current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                        self.logging_manager.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)
                except:
                    pass
            
            self.switch_to_stroop()
    
    def on_descriptive_enter(self, event):
        """Handle Enter key in descriptive task - go to Stroop screen."""
        print("🎬 Enter pressed - Going to Stroop screen...")
        self.logging_manager.log_action("KEY_PRESS", "Enter key pressed in descriptive task screen", self.current_screen)
        
        # Save final response before leaving descriptive task
        if hasattr(self, 'response_text'):
            try:
                current_response = self.response_text.get("1.0", tk.END).strip()
                if current_response:
                    current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                    self.logging_manager.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)
            except:
                pass
        
        self.switch_to_stroop()
    
    def switch_to_stroop(self):
        """Switch to stroop video screen."""
        # Show transition screen first
        self.show_transition_screen(
            TRANSITION_MESSAGES['stroop'],
            self._setup_stroop
        )
    
    def _setup_stroop(self):
        """Actually setup the stroop screen after confirmation."""
        print("🎬 Setting up Stroop Video Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Setting up stroop video screen", self.current_screen)
        self.clear_screen()
        self.current_screen = "stroop"
        
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
        if COUNTDOWN_ENABLED and STROOP_COUNTDOWN_ENABLED:
            countdown_label = tk.Label(
                self.main_frame,
                text=f"⏰ You only have {STROOP_COUNTDOWN_MINUTES} minutes left!",
                font=('Arial', 16, 'bold'),
                fg=COLORS['text_accent'],
                bg=BACKGROUND_COLOR
            )
            countdown_label.pack(pady=10)
            
            # Set up countdown with countdown manager
            self.countdown_manager.setup_countdown_label(countdown_label)
            
            # Add corner countdown timer (top-right)
            self.setup_corner_countdown()
        
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
        import os
        filename = os.path.basename(STROOP_VIDEO_PATH) if os.path.exists(STROOP_VIDEO_PATH) else "No video file found"
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
        self.video_manager.init_video(STROOP_VIDEO_PATH)
        
        # Set up video completion callback for auto-transition
        self.video_manager.set_video_end_callback(lambda: self.on_stroop_video_end())
        
        # Bind keys (only allow navigation in developer mode OR when countdown has finished)
        if DEVELOPER_MODE:
            self.root.bind_all('<Return>', self.on_stroop_enter)
        self.root.bind_all('<KeyPress-r>', self.on_stroop_restart)
        self.root.bind_all('<KeyPress-R>', self.on_stroop_restart)
        self.root.bind_all('<KeyPress-q>', self.on_quit)
        
        # Set focus to start button initially
        self.stroop_start_button.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Don't start countdown automatically - will start when user clicks START button
        # Initialize task as not started
        self.stroop_task_started = False
        
        print("✅ Stroop screen ready")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Stroop screen displayed and ready", self.current_screen)
    
    def start_stroop_task(self):
        """Start the Stroop task - begin video playback and start countdown."""
        if self.stroop_task_started:
            return  # Already started
        
        print("🚀 Starting Stroop task...")
        self.logging_manager.log_action("TASK_STARTED", "Stroop task started by user", self.current_screen)
        
        # Mark as started
        self.stroop_task_started = True
        
        # Hide the start button
        self.stroop_start_button.destroy()
        
        # Update status and start video
        self.update_stroop_status("Starting video...", '#66ff99')
        self.video_manager.toggle_video_playback(self.update_stroop_status)
        
        # Start stroop video loop
        def update_callback(new_frame):
            self.root.after(0, self.update_stroop_video_display, new_frame)
        
        self.video_manager.start_stroop_video_loop(
            self.canvas, 
            lambda: self.current_screen,
            update_callback
        )
        
        # Start countdown timer (if enabled)
        if COUNTDOWN_ENABLED and STROOP_COUNTDOWN_ENABLED:
            self.countdown_manager.start_countdown(STROOP_COUNTDOWN_MINUTES, "stroop")
            
            if DEVELOPER_MODE:
                # In developer mode, auto-transition when countdown finishes
                self.countdown_manager.set_countdown_finish_callback(self.auto_transition_from_stroop)
            else:
                # In production mode, enable Enter key only when countdown finishes
                self.countdown_manager.set_countdown_finish_callback(self.enable_stroop_navigation)
    
    def enable_stroop_navigation(self):
        """Enable navigation for stroop screen when countdown finishes (production mode)."""
        if not DEVELOPER_MODE and self.current_screen == "stroop":
            self.root.bind_all('<Return>', self.on_stroop_enter)
            print("🔓 Navigation enabled - Press ENTER for Math Task")
    
    def auto_transition_from_stroop(self):
        """Auto-transition from stroop task when countdown finishes (developer mode)."""
        if DEVELOPER_MODE and self.current_screen == "stroop":
            print("⏰ Stroop task countdown finished - Auto-transitioning to Math task")
            self.logging_manager.log_action("AUTO_TRANSITION", "Stroop task countdown completed in developer mode, automatically transitioning to math task", self.current_screen)
            self.switch_to_math_task()
    
    def update_stroop_status(self, text, color='#66ff99'):
        """Update status label for stroop screen."""
        if hasattr(self, 'status_label'):
            try:
                self.status_label.config(text=text, fg=color)
            except:
                pass
    
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
    
    def on_stroop_enter(self, event):
        """Handle Enter key in Stroop screen - go to math task."""
        print("🧮 Enter pressed - Going to Math Task...")
        self.logging_manager.log_action("KEY_PRESS", "Enter key pressed in stroop screen", self.current_screen)
        self.switch_to_math_task()
    
    def on_stroop_video_end(self):
        """Handle when stroop video reaches its natural end."""
        if self.current_screen == "stroop":
            print("🎬 Stroop video finished - Auto-transitioning to math task")
            self.logging_manager.log_action("VIDEO_END_TRANSITION", "Stroop video completed, automatically transitioning to math task", self.current_screen)
            self.switch_to_math_task()
    
    def on_stroop_restart(self, event):
        """Handle R key in stroop screen - restart video."""
        print("🔄 R pressed - Restarting video...")
        self.logging_manager.log_action("KEY_PRESS", "R key pressed - restarting stroop video", self.current_screen)
        self.video_manager.restart_video(self.update_stroop_status)
        # Auto-play after restart
        self.video_manager.toggle_video_playback(self.update_stroop_status)
    
    def switch_to_math_task(self):
        """Switch to math task screen - subtract 7s from 4000."""
        # Show transition screen first
        self.show_transition_screen(
            TRANSITION_MESSAGES['math'],
            self._setup_math_task
        )
    
    def _setup_math_task(self):
        """Actually setup the math task screen after confirmation."""
        print("🧮 Setting up Math Task Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Setting up math task screen", self.current_screen)
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
        if COUNTDOWN_ENABLED and MATH_COUNTDOWN_ENABLED:
            countdown_label = tk.Label(
                self.main_frame,
                text=f"⏰ You only have {MATH_COUNTDOWN_MINUTES} minutes left!",
                font=('Arial', 16, 'bold'),
                fg=COLORS['text_accent'],
                bg=BACKGROUND_COLOR
            )
            countdown_label.pack(pady=10)
            
            # Set up countdown with countdown manager
            self.countdown_manager.setup_countdown_label(countdown_label)
            
            # Add corner countdown timer (top-right)
            self.setup_corner_countdown()
        
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
        
        # Bind keys (only allow navigation in developer mode OR when countdown has finished)
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
        
        print("✅ Math task screen ready - ENTER=content performance")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Math task screen displayed and ready", self.current_screen)
    
    def start_math_task(self):
        """Start the Math task - show instructions and start countdown."""
        if self.math_task_started:
            return  # Already started
        
        print("🚀 Starting Math task...")
        self.logging_manager.log_action("TASK_STARTED", "Math task started by user", self.current_screen)
        
        # Mark as started
        self.math_task_started = True
        
        # Hide the start button
        self.math_start_button.destroy()
        
        # Show the actual task instructions
        self.math_prompt.config(text=MATH_INSTRUCTION_TEXT)
        
        # Start countdown timer (if enabled)
        if COUNTDOWN_ENABLED and MATH_COUNTDOWN_ENABLED:
            self.countdown_manager.start_countdown(MATH_COUNTDOWN_MINUTES, "math_task")
            
            if DEVELOPER_MODE:
                # In developer mode, auto-transition when countdown finishes
                self.countdown_manager.set_countdown_finish_callback(self.auto_transition_from_math)
            else:
                # In production mode, enable Enter key only when countdown finishes
                self.countdown_manager.set_countdown_finish_callback(self.enable_math_navigation)
    
    def enable_math_navigation(self):
        """Enable navigation for math task when countdown finishes (production mode)."""
        if not DEVELOPER_MODE and self.current_screen == "math_task":
            self.root.bind_all('<Return>', self.on_math_enter)
            print("🔓 Navigation enabled - Press ENTER for Content Performance Task")
    
    def auto_transition_from_math(self):
        """Auto-transition from math task when countdown finishes (developer mode)."""
        if DEVELOPER_MODE and self.current_screen == "math_task":
            print("⏰ Math task countdown finished - Auto-transitioning to Content Performance task")
            self.logging_manager.log_action("AUTO_TRANSITION", "Math task countdown completed in developer mode, automatically transitioning to content performance task", self.current_screen)
            self.switch_to_content_performance_task()
    
    def on_math_enter(self, event):
        """Handle Enter key in math task - go to content performance task."""
        print("📱 Enter pressed - Going to Content Performance Task...")
        self.logging_manager.log_action("KEY_PRESS", "Enter key pressed in math task screen", self.current_screen)
        self.switch_to_content_performance_task()
    
    def switch_to_content_performance_task(self):
        """Switch to content performance task screen."""
        # Show transition screen first
        self.show_transition_screen(
            "Get ready for content performance task",
            self._setup_content_performance_task
        )
    
    def _setup_content_performance_task(self):
        """Actually setup the content performance task screen after confirmation."""
        print("📱 Setting up Content Performance Task Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Setting up content performance task screen", self.current_screen)
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
        
        # Main instruction text
        if hasattr(self, 'selected_task') and self.selected_task:
            task_text = f"Now open the Content Performance Task and start the {self.selected_task.upper()} task."
        else:
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
        
        # Add prominent task assignment display if task is assigned
        if hasattr(self, 'selected_task') and self.selected_task:
            task_display = tk.Label(
                self.main_frame,
                text=f"ASSIGNED TASK: {self.selected_task.upper()}",
                font=('Arial', 24, 'bold'),
                fg='#FFFF00',  # Bright yellow
                bg=CONTENT_PERFORMANCE_BG_COLOR,
                relief='solid',
                borderwidth=2,
                padx=20,
                pady=10
            )
            task_display.pack(pady=20)
        
        # Next button
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
            controls = tk.Label(
                self.main_frame,
                text="ENTER - Continue to Rest",
                font=('Arial', 16),
                fg='#B8D4F0',
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
        
        print("✅ Content performance task screen ready - ENTER=rest")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Content performance task screen displayed and ready", self.current_screen)
    
    def on_content_performance_enter(self, event):
        """Handle Enter key in content performance task."""
        print("🎯 Enter pressed...")
        self.logging_manager.log_action("KEY_PRESS", "Enter key pressed in content performance task screen", self.current_screen)
        print("🧘 Going to Post-Study Rest...")
        self.switch_to_post_study_rest_with_transition()
    
    def on_content_performance_next(self):
        """Handle Next button in content performance task."""
        print("🎯 Next button pressed...")
        self.logging_manager.log_action("BUTTON_PRESS", "Continue to Post-Study Rest button pressed", self.current_screen)
        print("🧘 Going to Post-Study Rest...")
        self.switch_to_post_study_rest_with_transition()
    
    def switch_to_post_study_rest_with_transition(self):
        """Switch to post-study rest screen with transition."""
        # Show transition screen first
        bg_color = CONTENT_PERFORMANCE_BG_COLOR if self.current_screen == "content_performance" else None
        self.show_transition_screen(
            TRANSITION_MESSAGES['post_study_rest'],
            self.switch_to_post_study_rest,
            bg_color
        )
        
    def switch_to_post_study_rest(self):
        """Switch to post-study rest screen - same as relaxation but for post-study."""
        print("🧘 Switching to Post-Study Rest Screen")
        self.logging_manager.log_action("SCREEN_TRANSITION", "Switching to post-study rest screen", self.current_screen)
        self.clear_screen()
        self.current_screen = "post_study_rest"
        
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
        text_item = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2,
            text="Study Complete - Please Relax",
            font=('Arial', 48, 'bold'),
            fill=COLORS['text_primary']
        )
        
        # Initialize and start video (same as relaxation)
        self.video_manager.init_video(RELAXATION_VIDEO_PATH)
        
        # Set up video completion callback for auto-close
        self.video_manager.set_video_end_callback(lambda: self.on_post_study_video_end())
        
        self.video_manager.start_post_study_video_loop(self.canvas, lambda: self.current_screen, text_item)
        
        # Bind keys
        self.root.bind_all('<KeyPress-q>', self.on_quit)
        self.root.focus_set()
        
        # Maintain focus in focus mode
        if FOCUS_MODE:
            self.root.focus_force()
        
        # Start hidden countdown for automatic app closure
        self.start_post_study_countdown(RELAXATION_COUNTDOWN_MINUTES)
        
        print("✅ Post-study rest screen ready - Q=quit")
        self.logging_manager.log_action("SCREEN_DISPLAYED", "Post-study rest screen displayed and ready", self.current_screen)
    
    def on_post_study_video_end(self):
        """Handle when post-study video reaches its natural end."""
        if self.current_screen == "post_study_rest":
            print("🎬 Post-study video finished - Auto-closing application")
            self.logging_manager.log_action("VIDEO_END_CLOSE", "Post-study video completed, automatically closing application", self.current_screen)
            self.quit_app()
    
    def start_post_study_countdown(self, minutes):
        """Start hidden countdown for post-study rest screen auto-closure."""
        total_time = minutes * 60 * 1000  # Convert to milliseconds
        
        def auto_close():
            if self.current_screen == "post_study_rest":
                print(f"⏰ Post-study relaxation countdown finished - Auto-closing application")
                self.logging_manager.log_action("AUTO_CLOSE", f"Post-study relaxation countdown ({minutes} minutes) completed, closing application", self.current_screen)
                self.quit_app()
        
        # Schedule the automatic closure
        self.root.after(total_time, auto_close)
        self.logging_manager.log_action("POST_STUDY_COUNTDOWN_STARTED", f"Hidden countdown started for {minutes} minutes before auto-close", self.current_screen)
        
    def show_timeout_notification(self, screen_name):
        """Show timeout notification and handle automatic transitions."""
        print(f"⏰ TIME'S UP for {screen_name} screen!")
        
        if DEVELOPER_MODE:
            # In developer mode, just show the timeout notification
            # Find the countdown label and update it
            if hasattr(self, 'countdown_manager') and self.countdown_manager.countdown_label:
                try:
                    self.countdown_manager.countdown_label.config(
                        text="🚨 TIME'S UP! EVALUATION COMPLETE!",
                        fg='#ff0000',
                        font=('Arial', 20, 'bold')
                    )
                except:
                    pass
        else:
            # In production mode, automatically transition to next screen
            self.handle_automatic_timeout_transition(screen_name)
    
    def handle_automatic_timeout_transition(self, screen_name):
        """Handle automatic transitions when countdown expires in production mode."""
        print(f"🔄 Auto-transitioning from {screen_name} due to timeout...")
        self.logging_manager.log_action("AUTO_TIMEOUT_TRANSITION", f"Time expired on {screen_name}, automatically transitioning", self.current_screen)
        
        if screen_name == "descriptive_task":
            # Show timeout message
            if hasattr(self, 'countdown_manager') and self.countdown_manager.countdown_label:
                try:
                    self.countdown_manager.countdown_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
                except:
                    pass
            
            # Disable editing in descriptive writing task
            if hasattr(self, 'response_text'):
                try:
                    self.response_text.config(state='disabled', bg='lightgray', fg='gray')
                except:
                    pass
            
            # Save any current response before transitioning
            if hasattr(self, 'response_text'):
                try:
                    current_response = self.response_text.get("1.0", tk.END).strip()
                    if current_response:
                        current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                        self.logging_manager.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)
                except:
                    pass
            
            # Transition to Stroop task
            self.root.after(2000, self.switch_to_stroop)  # 2 second delay for user awareness
            
        elif screen_name == "stroop":
            # Show timeout message
            if hasattr(self, 'countdown_manager') and self.countdown_manager.countdown_label:
                try:
                    self.countdown_manager.countdown_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
                except:
                    pass
            
            # Stop the video
            self.video_manager.stop_video()
            
            # Transition to Math task
            self.root.after(2000, self.switch_to_math_task)  # 2 second delay
            
        elif screen_name == "math_task":
            # Show timeout message
            if hasattr(self, 'countdown_manager') and self.countdown_manager.countdown_label:
                try:
                    self.countdown_manager.countdown_label.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
                except:
                    pass
            
            # Show completion message on math prompt
            if hasattr(self, 'math_prompt'):
                try:
                    self.math_prompt.config(text="⏰ Time's up! Moving to next task...", fg='#ff6666')
                except:
                    pass
            
            # Transition to Content Performance task
            self.root.after(2000, self.switch_to_content_performance_task)  # 2 second delay
    
    def show_transition_screen(self, message, callback, bg_color=None):
        """Show a full-screen transition screen when transitioning between screens."""
        print(f"🚨 TRANSITION: {message}")
        self.logging_manager.log_action("TRANSITION_SCREEN_DISPLAYED", f"Transition screen shown: {message[:50]}...", self.current_screen)
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
                self.logging_manager.log_action("TRANSITION_CONFIRMED", "User confirmed transition - proceeding to next screen", self.current_screen)
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
            print("📖 Current screen: Participant ID")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🔌 Keyboard interrupt - Shutting down...")
            self.quit_app()
        finally:
            self.cleanup_resources()


def main():
    """Main entry point."""
    print("🧘 Moly - Relaxation Experience")
    print("=" * 40)
    
    app = MolyApp()
    app.run()
    
    print("👋 Thanks for using Moly!")


if __name__ == '__main__':
    main()