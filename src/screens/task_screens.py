#!/usr/bin/env python3

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter
import os
import cv2
from .base_screen import BaseScreen


class RelaxationScreen(BaseScreen):
    """Screen for relaxation with video background."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.video_widget = None
        self.background_color = 'black'
    
    def setup_screen(self):
        """Setup the relaxation screen with video background, centered text, and responsive layout."""
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive sizes
        video_min_width = max(600, int(screen_width * 0.6))
        video_min_height = max(450, int(screen_height * 0.6))
        text_font_size = max(32, min(96, int(screen_width * 0.05)))
        
        # Setup video display area - responsive sizing
        self.video_widget = QLabel()
        self.video_widget.setStyleSheet(f"background-color: {self.background_color}; border: 2px solid #444444; border-radius: 8px;")
        self.video_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_widget.setMinimumSize(video_min_width, video_min_height)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.video_widget)
        self.add_widget(self.video_widget)
        
        # Create text overlay if enabled - emphasized and responsive
        try:
            from config import SHOW_RELAXATION_TEXT, RELAXATION_TEXT, COLORS
        except ImportError:
            SHOW_RELAXATION_TEXT = True
            RELAXATION_TEXT = "Please Relax"
            COLORS = {'relaxation_text': '#ffffff'}
            
        if SHOW_RELAXATION_TEXT:
            relaxation_label = QLabel(RELAXATION_TEXT)
            relaxation_label.setFont(QFont('Arial', text_font_size, QFont.Weight.Bold))
            relaxation_label.setStyleSheet(f"""
                color: {COLORS['relaxation_text']}; 
                background-color: rgba(0, 0, 0, 100); 
                padding: 20px; 
                border-radius: 15px;
                font-size: {text_font_size}px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            """)
            relaxation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(relaxation_label)
            self.add_widget(relaxation_label)
        
        # Initialize and start video - try to load actual video
        try:
            from config import RELAXATION_VIDEO_PATH, RELAXATION_COUNTDOWN_MINUTES
            
            # Check if video file exists
            video_path = RELAXATION_VIDEO_PATH
            if os.path.exists(video_path):
                print(f"📹 Loading relaxation video from: {video_path}")
                self.app.video_manager.init_video(video_path)
                
                # Set up video completion callback for auto-transition
                self.app.video_manager.set_video_end_callback(lambda: self.on_video_end())
                
                # Start video playback using PyQt6 timer with specific screen name
                self.app.video_manager.start_pyqt_video_loop(self.video_widget, lambda: self.app.current_screen, "relaxation")
            else:
                print(f"⚠️ Video file not found: {video_path}, using placeholder")
                placeholder_label = QLabel("Please Relax\n\nVideo Background")
                placeholder_label.setFont(QFont('Arial', 36, QFont.Weight.Bold))
                placeholder_label.setStyleSheet(f"color: {COLORS.get('relaxation_text', 'white')}; background-color: transparent;")
                placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.layout.addWidget(placeholder_label)
                self.add_widget(placeholder_label)
                
            # Start hidden countdown for automatic transition
            self.start_relaxation_countdown(RELAXATION_COUNTDOWN_MINUTES)
            
        except (ImportError, Exception) as e:
            print(f"⚠️ Error setting up video: {e}, using placeholder")
            # Config or video not available, show placeholder
            placeholder_label = QLabel("Please Relax\n\n(Calm Environment)")
            placeholder_label.setFont(QFont('Arial', 36, QFont.Weight.Bold))
            placeholder_label.setStyleSheet(f"color: {COLORS.get('relaxation_text', 'white')}; background-color: transparent;")
            placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(placeholder_label)
            self.add_widget(placeholder_label)
        
        # Bind keys
        try:
            from config import DEVELOPER_MODE
            if DEVELOPER_MODE:
                self.bind_key('<Return>', self.on_enter_pressed)
        except ImportError:
            pass
            
        self.bind_key('<KeyPress-q>', self.on_quit_pressed)
        self.setFocus()
        
        # Log screen display
        self.log_action("RELAXATION_SCREEN_DISPLAYED", "Relaxation screen displayed with video/placeholder")
    
    def on_video_end(self):
        """Handle when relaxation video reaches its natural end."""
        if self.app.current_screen == self.screen_name:
            print("🎬 Relaxation video finished - Auto-transitioning to descriptive task")
            self.log_action("VIDEO_END_TRANSITION", "Relaxation video completed, automatically transitioning to descriptive task")
            self.transition_to_next_screen()
    
    def on_enter_pressed(self):
        """Handle Enter key in relaxation screen."""
        print("🎯 Enter pressed - Going to Descriptive Task screen...")
        self.log_action("RELAXATION_ENTER_KEY", "Enter key pressed - skipping relaxation to descriptive task")
        self.transition_to_next_screen()
    
    def on_quit_pressed(self):
        """Handle Q key - quit application."""
        print("🔌 Q pressed - Quitting application...")
        self.log_action("KEY_PRESS", "Q key pressed - quitting application")
        self.app.quit_app()
    
    def start_relaxation_countdown(self, minutes):
        """Start hidden countdown for relaxation screen auto-transition."""
        total_time = minutes * 60 * 1000
        
        def auto_transition():
            if self.app.current_screen == self.screen_name:
                print(f"⏰ Relaxation countdown finished - Auto-transitioning to descriptive task")
                self.log_action("RELAXATION_COUNTDOWN_AUTO_TRANSITION", f"Relaxation countdown ({minutes} minutes) completed, transitioning to descriptive task")
                self.transition_to_next_screen()
        
        QTimer.singleShot(total_time, auto_transition)
        self.log_action("RELAXATION_COUNTDOWN_STARTED", f"Hidden countdown started for {minutes} minutes")
    
    def transition_to_next_screen(self):
        """Transition to the next screen (descriptive task)."""
        print("🧘 Relaxation transition: Moving to descriptive task")
        self.app.switch_to_descriptive_task()


class DescriptiveTaskScreen(BaseScreen):
    """Screen for descriptive writing task."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.response_text = None
        self.prompt_label = None
        self.word_count_label = None
        self.descriptive_start_button = None
        self.corner_countdown_label = None
        self.task_started = False
        
        # Load configuration or use defaults
        try:
            from config import (BACKGROUND_COLOR, COLORS, COUNTDOWN_ENABLED, 
                              DESCRIPTIVE_COUNTDOWN_ENABLED, DESCRIPTIVE_COUNTDOWN_MINUTES,
                              DESCRIPTIVE_PROMPTS, DEVELOPER_MODE)
            self.background_color = BACKGROUND_COLOR
            self.colors = COLORS
            self.countdown_enabled = COUNTDOWN_ENABLED and DESCRIPTIVE_COUNTDOWN_ENABLED
            self.countdown_minutes = DESCRIPTIVE_COUNTDOWN_MINUTES
            self.prompts = DESCRIPTIVE_PROMPTS.copy()
            self.developer_mode = DEVELOPER_MODE
        except ImportError:
            # Fallback values
            self.background_color = '#8B0000'
            self.colors = {'title': 'white', 'warning': '#ff6666', 'text_primary': 'white', 
                          'text_accent': '#cccccc', 'text_secondary': '#999999', 'countdown_normal': '#00ff00'}
            self.countdown_enabled = True
            self.countdown_minutes = 10
            self.prompts = ["Describe your current thoughts and feelings."]
            self.developer_mode = False
            
        self.current_prompt_index = 0
        self.descriptive_font_size = 16
        self.descriptive_font_family = 'Arial'
    
    def setup_screen(self):
        """Setup the descriptive task screen with responsive layout."""
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive font sizes
        title_font_size = max(20, min(40, int(screen_width * 0.022)))
        warning_font_size = max(14, min(22, int(screen_width * 0.012)))
        countdown_font_size = max(20, min(36, int(screen_width * 0.018)))
        corner_countdown_font_size = max(60, min(120, int(screen_width * 0.06)))
        button_font_size = max(16, min(28, int(screen_width * 0.015)))
        prompt_font_size = max(18, min(32, int(screen_width * 0.018)))
        
        # Title - emphasized and responsive
        title = self.create_title(
            "Descriptive Task",
            font_size=title_font_size,
            color=self.colors['title'],
            bg_color=self.background_color
        )
        self.layout.addWidget(title)
        self.layout.addStretch(1)
        
        # Evaluation hint - responsive
        evaluation_hint = self.create_instruction(
            "⚠️ Your responses will be evaluated for accuracy and detail",
            font_size=warning_font_size,
            color=self.colors['warning'],
            bg_color=self.background_color
        )
        self.layout.addWidget(evaluation_hint)
        self.layout.addStretch(1)
        
        # Countdown timer (if enabled) - responsive and emphasized
        if self.countdown_enabled:
            # Create main countdown display - emphasized
            self.countdown_label = QLabel(f"⏰ You have {self.countdown_minutes} minutes for this task")
            self.countdown_label.setFont(QFont('Arial', countdown_font_size, QFont.Weight.Bold))
            self.countdown_label.setStyleSheet(f"""
                color: {self.colors['countdown_normal']}; 
                background-color: rgba(0, 0, 0, 150); 
                padding: 15px; 
                border-radius: 10px;
                font-size: {countdown_font_size}px;
                border: 2px solid {self.colors['countdown_normal']};
            """)
            self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.countdown_label)
            self.layout.addStretch(1)
            
            # Create corner countdown timer (top-right) - responsive and emphasized
            self.corner_countdown_label = QLabel(self)
            self.corner_countdown_label.setText("0:00")
            self.corner_countdown_label.setFont(QFont('Arial', corner_countdown_font_size, QFont.Weight.Bold))
            self.corner_countdown_label.setStyleSheet(f"""
                QLabel {{
                    color: #00FF00;
                    background-color: rgba(0, 0, 0, 200);
                    border: 4px solid white;
                    padding: 20px;
                    border-radius: 15px;
                    font-size: {corner_countdown_font_size}px;
                }}
            """)
            self.corner_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Position will be set after screen is shown
            
            # Store references for the countdown manager
            self.add_widget(self.countdown_label)
            self.add_widget(self.corner_countdown_label)
        
        # Start button - emphasized and responsive
        button_width = max(150, min(300, int(screen_width * 0.15)))
        button_height = max(50, min(100, int(screen_height * 0.08)))
        
        self.descriptive_start_button = self.create_button(
            "START TASK",
            command=self.start_descriptive_task,
            font_size=button_font_size,
            width=button_width,
            height=button_height,
            bg_color='#4CAF50',  # More prominent green
            fg_color='white'
        )
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.descriptive_start_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.layout.addStretch(1)
        
        # Current prompt display - emphasized and responsive
        self.prompt_label = self.create_instruction(
            "Click START TASK to begin",
            font_size=prompt_font_size,
            color=self.colors['text_primary']
        )
        self.layout.addWidget(self.prompt_label)
        self.layout.addStretch(1)
        
        # Response textbox
        self.setup_response_textbox()
        
        # Controls info (only show in developer mode)
        if self.developer_mode:
            controls = self.create_instruction(
                "ENTER - Stroop Task",
                font_size=max(12, min(20, int(screen_width * 0.010))),
                color=self.colors['text_secondary'],
                bg_color=self.background_color
            )
            self.layout.addWidget(controls)
            self.layout.addStretch(1)
        
        # Bind keys (only allow navigation in developer mode OR when countdown has finished)
        if self.developer_mode:
            self.bind_key('<Return>', self.on_enter_pressed)
        
        # Set initial focus to the start button
        self.descriptive_start_button.setFocus()
        
        # Log screen display
        self.log_action("DESCRIPTIVE_TASK_SCREEN_DISPLAYED", f"Descriptive task screen displayed with {len(self.prompts)} prompts available")
    
    def setup_response_textbox(self):
        """Setup the response textbox area with responsive sizing."""
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive sizes
        label_font_size = max(12, min(20, int(screen_width * 0.011)))
        text_font_size = max(10, min(18, int(screen_width * 0.009)))
        textbox_height = max(300, min(600, int(screen_height * 0.35)))
        word_count_font_size = max(10, min(16, int(screen_width * 0.008)))
        
        # Response label - responsive
        response_label = QLabel("Your Response:")
        response_label.setFont(QFont('Arial', label_font_size, QFont.Weight.Bold))
        response_label.setStyleSheet(f"color: {self.colors['text_primary']}; background-color: transparent; font-size: {label_font_size}px;")
        self.layout.addWidget(response_label)
        
        # Text edit widget - responsive sizing
        self.response_text = QTextEdit()
        self.response_text.setFont(QFont(self.descriptive_font_family, text_font_size))
        self.response_text.setStyleSheet(f"""
            QTextEdit {{
                color: gray;
                background-color: lightgray;
                border: 3px solid black;
                border-radius: 8px;
                padding: 10px;
                font-size: {text_font_size}px;
                line-height: 1.4;
            }}
        """)
        self.response_text.setMinimumHeight(textbox_height)
        self.response_text.setMaximumHeight(int(screen_height * 0.4))
        self.response_text.setEnabled(False)  # Initially disabled
        
        self.layout.addWidget(self.response_text)
        self.add_widget(self.response_text)
        
        # Word count display - responsive
        self.word_count_label = QLabel("Word count: 0")
        self.word_count_label.setFont(QFont('Arial', word_count_font_size))
        self.word_count_label.setStyleSheet(f"color: {self.colors['text_accent']}; background-color: transparent; font-size: {word_count_font_size}px;")
        self.layout.addWidget(self.word_count_label)
        self.add_widget(self.word_count_label)
        self.layout.addStretch(1)
    
    def position_corner_countdown(self):
        """Position the corner countdown timer after the screen is shown."""
        if hasattr(self, 'corner_countdown_label') and self.corner_countdown_label:
            # Calculate position based on parent widget size
            parent_width = self.width() if self.width() > 0 else self.app.screen_width
            print(f"🎯 DEBUG: Positioning corner countdown - parent_width:{parent_width}, screen_width:{self.app.screen_width}")
            
            # Position in top-right corner
            x_pos = parent_width - 220
            y_pos = 20
            width = 250
            height = 150

            print(f"🎯 DEBUG: Setting corner countdown geometry to: x:{x_pos}, y:{y_pos}, w:{width}, h:{height}")
            self.corner_countdown_label.setGeometry(x_pos, y_pos, width, height)
            self.corner_countdown_label.show()
            self.corner_countdown_label.raise_()
            print(f"🎯 DEBUG: Corner countdown positioned and shown")
        else:
            print(f"🎯 DEBUG: Cannot position corner countdown - label does not exist")
    
    def start_descriptive_task(self):
        """Start the descriptive task - enable textbox and start countdown."""
        if self.task_started:
            return  # Already started
        
        print("🚀 Starting descriptive task...")
        self.log_action("TASK_STARTED", "Descriptive task started by user")
        
        # Mark as started
        self.task_started = True
        
        # Hide the start button
        self.descriptive_start_button.deleteLater()
        self.widgets.remove(self.descriptive_start_button)
        
        # Enable the textbox
        self.response_text.setEnabled(True)
        self.response_text.setStyleSheet("color: black; background-color: white;")
        
        # Set up word count tracking
        self.setup_word_count_tracking()
        
        # Show the first prompt
        self.show_current_prompt()
        
        # Set focus to textbox
        self.response_text.setFocus()
        
        # Log task started
        current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "No prompt available"
        self.log_action("DESCRIPTIVE_TASK_STARTED", f"Task started with prompt: {current_prompt[:50]}...")
        
        # Position corner countdown if it exists
        if hasattr(self, 'corner_countdown_label'):
            self.position_corner_countdown()
        
        # Start countdown timer (if enabled) with new system
        if self.countdown_enabled:
            print(f"🎯 DEBUG: Setting up countdown labels...")
            
            # Set up countdown manager with our labels
            if hasattr(self, 'countdown_label'):
                print(f"🎯 DEBUG: Main countdown label exists: {self.countdown_label is not None}")
                print(f"🎯 DEBUG: Main label text: {self.countdown_label.text() if self.countdown_label else 'None'}")
                self.app.countdown_manager.setup_countdown_label(self.countdown_label)
            else:
                print(f"🎯 DEBUG: No main countdown label found!")
                
            if hasattr(self, 'corner_countdown_label'):
                print(f"🎯 DEBUG: Corner countdown label exists: {self.corner_countdown_label is not None}")
                print(f"🎯 DEBUG: Corner label text: {self.corner_countdown_label.text() if self.corner_countdown_label else 'None'}")
                print(f"🎯 DEBUG: Corner label parent: {self.corner_countdown_label.parent() if self.corner_countdown_label else 'None'}")
                self.app.countdown_manager.set_corner_countdown_label(self.corner_countdown_label)
            else:
                print(f"🎯 DEBUG: No corner countdown label found!")
            
            # Start the countdown
            print(f"🎯 DEBUG: Starting countdown with {self.countdown_minutes} minutes...")
            print(f"🎯 DEBUG: Using screen name: {self.screen_name}")
            self.app.countdown_manager.start_countdown(self.countdown_minutes, self.screen_name)
            
            # Always auto-transition when countdown finishes, regardless of mode
            self.app.countdown_manager.set_countdown_finish_callback(self.auto_transition_from_descriptive)
    
    def show_current_prompt(self):
        """Show current descriptive prompt."""
        if self.current_prompt_index < len(self.prompts):
            prompt = self.prompts[self.current_prompt_index]
            self.prompt_label.setText(prompt)
        else:
            self.prompt_label.setText("Great job! You've completed all the descriptive tasks.")
    
    def setup_word_count_tracking(self):
        """Set up word count tracking for the descriptive response text."""
        def update_word_count(event=None):
            try:
                # Get text content
                text_content = self.response_text.toPlainText()
                # Remove trailing newline and split into words
                words = text_content.strip().split()
                # Filter out empty strings
                word_count = len([word for word in words if word.strip()])
                # Update the label
                self.word_count_label.setText(f"Word count: {word_count}")
            except:
                # If there's any error, just show 0
                self.word_count_label.setText("Word count: 0")
        
        # Connect to text change events in PyQt6
        self.response_text.textChanged.connect(update_word_count)
        self.response_text.textChanged.connect(self.log_text_activity)
        
        # Initial word count
        update_word_count()
    
    def log_text_activity(self):
        """Log text activity in descriptive task."""
        try:
            text_content = self.response_text.toPlainText()
            word_count = len([word for word in text_content.strip().split() if word.strip()])
            
            # Log periodically based on word count milestones
            if word_count > 0 and word_count % 10 == 0:
                self.log_action("DESCRIPTIVE_TEXT_PROGRESS", f"Word count reached: {word_count}")
            
            # Log when sentences are completed (rough detection)
            if text_content.endswith('.') or text_content.endswith('!') or text_content.endswith('?'):
                self.log_action("DESCRIPTIVE_SENTENCE_COMPLETED", f"Sentence completed, total words: {word_count}")
        except:
            pass  # Don't let logging errors interrupt text input
    
    def enable_navigation(self):
        """Enable navigation when countdown finishes (production mode)."""
        if not self.developer_mode and self.app.current_screen == self.screen_name:
            self.bind_key('<Return>', self.on_enter_pressed)
            print("🔓 Navigation enabled - Press ENTER for Stroop Task")
            self.log_action("DESCRIPTIVE_COUNTDOWN_FINISHED", "Countdown finished - navigation enabled for production mode")
    
    def auto_transition_from_descriptive(self):
        """Auto-transition when countdown finishes (both developer and production modes)."""
        if self.app.current_screen == self.screen_name:
            mode_text = "developer mode" if self.developer_mode else "production mode"
            print(f"⏰ Descriptive task countdown finished - Auto-transitioning to Stroop task ({mode_text})")
            self.log_action("DESCRIPTIVE_COUNTDOWN_AUTO_TRANSITION", f"Descriptive task countdown completed in {mode_text}, automatically transitioning to stroop")
            self.save_current_response()
            self.transition_to_next_screen()
    
    def on_enter_pressed(self):
        """Handle Enter key in descriptive task - skip countdown and go to next screen."""
        if self.developer_mode:
            print("🎬 Enter pressed in developer mode - Skipping countdown and going to next screen...")
            
            # Stop the countdown timer
            if hasattr(self.app, 'countdown_manager'):
                self.app.countdown_manager.stop_countdown()
                print("⏰ Countdown stopped by developer mode Enter key")
            
            self.log_action("DESCRIPTIVE_ENTER_KEY_DEVELOPER", "Enter key pressed - developer mode countdown skip")
        else:
            print("🎬 Enter pressed - Going to next screen...")
            self.log_action("DESCRIPTIVE_ENTER_KEY_NORMAL", "Enter key pressed - normal mode navigation")
        
        self.save_current_response()
        self.transition_to_next_screen()
    
    def save_current_response(self):
        """Save the current response before leaving the screen."""
        if hasattr(self, 'response_text') and self.response_text:
            try:
                current_response = self.response_text.toPlainText().strip()
                if current_response:
                    current_prompt = self.prompts[self.current_prompt_index] if self.current_prompt_index < len(self.prompts) else "Unknown prompt"
                    self.app.logging_manager.log_descriptive_response(self.current_prompt_index, current_prompt, current_response)
            except Exception as e:
                print(f"Error saving response: {e}")
    
    def transition_to_next_screen(self):
        """Transition to the next screen (Stroop)."""
        print("📝 Descriptive task transition: Moving to Stroop task")
        if hasattr(self.app, 'stroop_screen'):
            print("🔍 Using app.stroop_screen for navigation")
            self.app.switch_to_screen(self.app.stroop_screen)
        else:
            print("🔍 Using switch_to_stroop() method")
            # Fallback to direct method call
            self.app.switch_to_stroop()


class StroopScreen(BaseScreen):
    """Screen for Stroop video task."""
    
    def __init__(self, app_instance, logging_manager=None):
        print("🎬 DEBUG: Creating StroopScreen instance")
        super().__init__(app_instance, logging_manager)
        print(f"🎬 DEBUG: StroopScreen initialized with screen_name: {self.screen_name}")
        self.video_widget = None
        self.task_started = False
        self.corner_countdown_label = None
        self.stroop_start_button = None
        
        # Load configuration or use defaults
        try:
            from config import (BACKGROUND_COLOR, COLORS, COUNTDOWN_ENABLED, 
                              STROOP_COUNTDOWN_ENABLED, STROOP_COUNTDOWN_MINUTES,
                              STROOP_VIDEO_PATH, DEVELOPER_MODE)
            self.background_color = BACKGROUND_COLOR
            self.colors = COLORS
            self.countdown_enabled = COUNTDOWN_ENABLED and STROOP_COUNTDOWN_ENABLED
            self.countdown_minutes = STROOP_COUNTDOWN_MINUTES
            self.video_path = STROOP_VIDEO_PATH
            self.developer_mode = DEVELOPER_MODE
        except ImportError:
            # Fallback values
            self.background_color = '#8B0000'
            self.colors = {'title': 'white', 'text_primary': 'white'}
            self.countdown_enabled = True
            self.countdown_minutes = 1
            self.video_path = "res/stroop.mov"
            self.developer_mode = False
    
    def setup_screen(self):
        """Setup the Stroop task screen with responsive layout."""
        print(f"🎬 DEBUG: Setting up Stroop screen with name: {self.screen_name}")
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive font sizes
        title_font_size = max(24, min(56, int(screen_width * 0.030)))
        instruction_font_size = max(14, min(24, int(screen_width * 0.013)))
        video_text_font_size = max(20, min(48, int(screen_width * 0.025)))
        button_font_size = max(16, min(28, int(screen_width * 0.015)))
        corner_countdown_font_size = max(70, min(140, int(screen_width * 0.07)))
        
        # Calculate responsive sizes
        video_min_width = max(600, int(screen_width * 0.7))
        video_min_height = max(400, int(screen_height * 0.55))
        
        # Title - emphasized and responsive
        title = self.create_title(
            "Stroop Task",
            font_size=title_font_size,
            color=self.colors['title']
        )
        self.layout.addWidget(title)
        self.layout.addStretch(1)
        
        # Instructions - responsive
        instruction = self.create_instruction(
            "Watch the video and follow the instructions. The task will begin automatically.",
            font_size=instruction_font_size,
            color=self.colors['text_primary']
        )
        self.layout.addWidget(instruction)
        self.layout.addStretch(1)
        
        # Corner countdown timer (top-right) - responsive and emphasized
        if self.countdown_enabled:
            self.corner_countdown_label = QLabel(self)
            self.corner_countdown_label.setText("0:00")
            self.corner_countdown_label.setFont(QFont('Arial', corner_countdown_font_size, QFont.Weight.Bold))
            self.corner_countdown_label.setStyleSheet(f"""
                QLabel {{
                    color: #00FF00;
                    background-color: rgba(0, 0, 0, 200);
                    border: 5px solid white;
                    padding: 20px;
                    border-radius: 15px;
                    font-size: {corner_countdown_font_size}px;
                }}
            """)
            self.corner_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.add_widget(self.corner_countdown_label)
        
        # Video display area - responsive sizing and emphasized
        self.video_widget = QLabel()
        self.video_widget.setStyleSheet(f"background-color: black; border: 3px solid #444444; border-radius: 8px;")
        self.video_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_widget.setMinimumSize(video_min_width, video_min_height)
        self.video_widget.setMaximumSize(int(screen_width * 0.9), int(screen_height * 0.7))
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.video_widget)
        self.add_widget(self.video_widget)
        
        # Only initialize video, don't start it automatically
        try:
            print(f"📹 Preparing stroop video from: {self.video_path}")
            
            # Check if video file exists
            if os.path.exists(self.video_path):
                print(f"📹 Initializing stroop video from: {self.video_path}")
                self.app.video_manager.init_video(self.video_path)
                
                # Video will start only after button press - responsive text
                self.video_widget.setText("Stroop Video Task\n\n(Press START to begin)")
                self.video_widget.setStyleSheet(f"""
                    background-color: black; 
                    border: 3px solid #444444; 
                    border-radius: 8px;
                    color: white;
                    font-size: {video_text_font_size}px;
                    font-weight: bold;
                """)
            else:
                print(f"⚠️ Stroop video file not found: {self.video_path}, using placeholder")
                self.video_widget.setText("Stroop Video Task\n\n(Video not available)")
                
        except (ImportError, Exception) as e:
            print(f"⚠️ Error setting up stroop video: {e}")
            self.video_widget.setText("Stroop Video Task\n\n(Error loading)")
        
        # Bind keys for developer mode
        if self.developer_mode:
            self.bind_key('<Return>', self.on_enter_pressed)
        
        # Set initial focus
        self.setFocus()
        
        # Start button - emphasized and responsive
        button_width = max(150, min(300, int(screen_width * 0.15)))
        button_height = max(50, min(100, int(screen_height * 0.08)))
        
        self.stroop_start_button = self.create_button(
            "START TASK",
            command=self.start_stroop_task,
            font_size=button_font_size,
            width=button_width,
            height=button_height,
            bg_color='#4CAF50',  # More prominent green
            fg_color='white'
        )
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.stroop_start_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.layout.addStretch(1)
        self.add_widget(self.stroop_start_button)
        
        # Set initial focus to start button
        self.stroop_start_button.setFocus()
        
        # Log screen display
        self.log_action("STROOP_SCREEN_DISPLAYED", "Stroop task screen displayed with video/placeholder")
    
    def position_corner_countdown(self):
        """Position the corner countdown timer after the screen is shown."""
        if hasattr(self, 'corner_countdown_label') and self.corner_countdown_label:
            # Calculate position based on parent widget size
            parent_width = self.width() if self.width() > 0 else self.app.screen_width
            
            # Position in top-right corner
            x_pos = parent_width - 320
            y_pos = 20
            width = 250
            height = 150

            self.corner_countdown_label.setGeometry(x_pos, y_pos, width, height)
            self.corner_countdown_label.show()
            self.corner_countdown_label.raise_()
    
    def start_stroop_task(self):
        """Start the Stroop task with countdown and video."""
        if self.task_started:
            return  # Already started
            
        print("🚀 Stroop task STARTED by user...")
        self.log_action("STROOP_TASK_STARTED", "Stroop task started by user button press")
        
        # Hide start button
        if hasattr(self, 'stroop_start_button') and self.stroop_start_button:
            self.stroop_start_button.hide()
            self.stroop_start_button.deleteLater()
            self.widgets.remove(self.stroop_start_button)
            
        # Clear placeholder text and start video
        self.task_started = True
        
        if os.path.exists(self.video_path):
            # Start video playback from 3-minute mark (180 seconds)
            fps = self.app.video_manager.cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(180 * fps)  # 180 seconds * fps
            self.app.video_manager.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.app.video_manager.start_pyqt_video_loop(self.video_widget, lambda: self.app.current_screen, "stroop")
            print("🎬 Stroop video started from 3-minute mark")
            self.log_action("STROOP_VIDEO_STARTED_3_MIN", "Stroop video started from 3:00 mark")
        
        # Start countdown if enabled
        if self.countdown_enabled:
            # Set up countdown labels
            if hasattr(self, 'corner_countdown_label'):
                self.app.countdown_manager.set_corner_countdown_label(self.corner_countdown_label)
                self.position_corner_countdown()
            
            # Always auto-transition when countdown finishes
            self.app.countdown_manager.set_countdown_finish_callback(self.auto_transition_from_stroop)
            self.app.countdown_manager.start_countdown(self.countdown_minutes, self.screen_name)
            
        # Set focus to main content
        self.setFocus()
    
    def on_enter_pressed(self):
        """Handle Enter key in developer mode."""
        if self.developer_mode:
            print("🎯 Enter pressed in Stroop task - Skipping to Math task...")
            self.log_action("STROOP_ENTER_KEY_DEVELOPER", "Enter key pressed - developer mode skip")
            self.transition_to_next_screen()
    
    def auto_transition_from_stroop(self):
        """Auto-transition when countdown finishes."""
        if self.app.current_screen == self.screen_name:
            mode_text = "developer mode" if self.developer_mode else "production mode"
            print(f"⏰ Stroop task countdown finished - Auto-transitioning to Math task ({mode_text})")
            self.log_action("STROOP_COUNTDOWN_AUTO_TRANSITION", f"Stroop task countdown completed in {mode_text}, automatically transitioning to math")
            self.transition_to_next_screen()
    
    def transition_to_next_screen(self):
        """Transition to the next screen (Math task)."""
        print("🎬 Stroop transition: Moving to Math task")
        if hasattr(self.app, 'math_screen'):
            self.app.switch_to_screen(self.app.math_screen)
        else:
            self.app.switch_to_math_task()


class MathTaskScreen(BaseScreen):
    """Screen for Math subtraction task."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.task_started = False
        self.corner_countdown_label = None
        self.math_start_button = None
        
        # Load configuration or use defaults
        try:
            from config import (BACKGROUND_COLOR, COLORS, COUNTDOWN_ENABLED, 
                              MATH_COUNTDOWN_ENABLED, MATH_COUNTDOWN_MINUTES,
                              MATH_STARTING_NUMBER, MATH_SUBTRACTION_VALUE,
                              MATH_INSTRUCTION_TEXT, DEVELOPER_MODE)
            self.background_color = BACKGROUND_COLOR
            self.colors = COLORS
            self.countdown_enabled = COUNTDOWN_ENABLED and MATH_COUNTDOWN_ENABLED
            self.countdown_minutes = MATH_COUNTDOWN_MINUTES
            self.starting_number = MATH_STARTING_NUMBER
            self.subtraction_value = MATH_SUBTRACTION_VALUE
            self.instruction_text = MATH_INSTRUCTION_TEXT
            self.developer_mode = DEVELOPER_MODE
        except ImportError:
            # Fallback values
            self.background_color = '#8B0000'
            self.colors = {'title': 'white', 'text_primary': 'white'}
            self.countdown_enabled = True
            self.countdown_minutes = 1
            self.starting_number = 4000
            self.subtraction_value = 7
            self.instruction_text = "Please subtract 7s from 4000, and say it aloud"
            self.developer_mode = False
    
    def setup_screen(self):
        """Setup the Math task screen with improved UI and responsive layout."""
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive font sizes
        title_font_size = max(20, min(48, int(screen_width * 0.025)))
        instruction_font_size = max(16, min(28, int(screen_width * 0.015)))
        countdown_font_size = max(20, min(36, int(screen_width * 0.018)))
        corner_countdown_font_size = max(60, min(120, int(screen_width * 0.06)))
        button_font_size = max(16, min(28, int(screen_width * 0.015)))
        math_display_font_size = max(18, min(36, int(screen_width * 0.020)))
        
        # Title - emphasized and responsive
        title = self.create_title(
            "Math Task",
            font_size=title_font_size,
            color=self.colors['title']
        )
        self.layout.addWidget(title)
        self.layout.addStretch(1)
        
        # Combined instructions with math display - improved UI
        combined_instruction = f"{self.instruction_text}\n\nStart with: {self.starting_number} and subtract {self.subtraction_value} repeatedly"
        
        instruction_widget = self.create_instruction(
            combined_instruction,
            font_size=instruction_font_size,
            color=self.colors['text_primary']
        )
        instruction_widget.setStyleSheet(f"""
            color: {self.colors['text_primary']}; 
            background-color: rgba(0, 0, 0, 150); 
            padding: 25px; 
            border-radius: 15px;
            border: 3px solid {self.colors['text_primary']};
            font-size: {instruction_font_size}px;
            font-weight: bold;
            line-height: 1.4;
        """)
        self.layout.addWidget(instruction_widget)
        self.layout.addStretch(1)
        
        # Countdown timer with urgent messaging (if enabled)
        if self.countdown_enabled:
            # Create main countdown display with urgent messaging
            self.countdown_label = QLabel(f"⏰ You have {self.countdown_minutes} minute(s) for this task")
            self.countdown_label.setFont(QFont('Arial', countdown_font_size, QFont.Weight.Bold))
            self.countdown_label.setStyleSheet(f"""
                color: {self.colors['countdown_normal']}; 
                background-color: rgba(0, 0, 0, 150); 
                padding: 15px; 
                border-radius: 10px;
                font-size: {countdown_font_size}px;
                border: 2px solid {self.colors['countdown_normal']};
            """)
            self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.countdown_label)
            self.layout.addStretch(1)
            
            # Create corner countdown timer (top-right) - responsive and emphasized
            self.corner_countdown_label = QLabel(self)
            self.corner_countdown_label.setText("0:00")
            self.corner_countdown_label.setFont(QFont('Arial', corner_countdown_font_size, QFont.Weight.Bold))
            self.corner_countdown_label.setStyleSheet(f"""
                QLabel {{
                    color: #00FF00;
                    background-color: rgba(0, 0, 0, 200);
                    border: 4px solid white;
                    padding: 20px;
                    border-radius: 15px;
                    font-size: {corner_countdown_font_size}px;
                }}
            """)
            self.corner_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.add_widget(self.corner_countdown_label)
            self.add_widget(self.countdown_label)
        
        # Start button - emphasized and responsive
        button_width = max(150, min(300, int(screen_width * 0.15)))
        button_height = max(50, min(100, int(screen_height * 0.08)))
        
        self.math_start_button = self.create_button(
            "START TASK",
            command=self.start_math_task,
            font_size=button_font_size,
            width=button_width,
            height=button_height,
            bg_color='#4CAF50',  # More prominent green
            fg_color='white'
        )
        
        # Center the button
        from PyQt6.QtWidgets import QHBoxLayout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.math_start_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.layout.addStretch(2)
        
        # Set initial focus to the start button
        self.math_start_button.setFocus()
        
        # Bind keys for developer mode
        if self.developer_mode:
            self.bind_key('<Return>', self.on_enter_pressed)
        
        # Log screen display
        self.log_action("MATH_SCREEN_DISPLAYED", "Math task screen displayed")
    
    def position_corner_countdown(self):
        """Position the corner countdown timer in the top-right corner."""
        try:
            if hasattr(self, 'corner_countdown_label') and self.corner_countdown_label:
                # Get screen dimensions
                screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
                
                # Calculate responsive size
                width = max(180, min(300, int(screen_width * 0.15)))
                height = max(80, min(150, int(screen_width * 0.08)))
                
                # Position in top-right corner with margin
                margin = 20
                x_pos = screen_width - width - margin
                y_pos = margin

                self.corner_countdown_label.setGeometry(x_pos, y_pos, width, height)
                self.corner_countdown_label.show()
                self.corner_countdown_label.raise_()
                print(f"🎯 Math corner countdown positioned at ({x_pos}, {y_pos}) with size ({width}, {height})")
            else:
                print(f"🎯 Math corner countdown not available for positioning")
        except Exception as e:
            print(f"⚠️ Error positioning math corner countdown: {e}")
    
    def start_math_task(self):
        """Start the Math task with countdown."""
        self.task_started = True
        self.log_action("MATH_TASK_STARTED", "Math task started")
        
        # Hide the start button
        if hasattr(self, 'math_start_button'):
            self.math_start_button.setVisible(False)
        
        # Update countdown label to show task is active
        if self.countdown_enabled and hasattr(self, 'countdown_label'):
            self.countdown_label.setText("⚠️ Task in progress - perform mental math!")
            self.countdown_label.setStyleSheet(f"""
                color: #FFA500; 
                background-color: rgba(0, 0, 0, 150); 
                padding: 15px; 
                border-radius: 10px;
                border: 2px solid #FFA500;
                font-weight: bold;
            """)
        
        # Start countdown if enabled
        if self.countdown_enabled:
            try:
                # Set up countdown labels
                if hasattr(self, 'corner_countdown_label'):
                    self.app.countdown_manager.set_corner_countdown_label(self.corner_countdown_label)
                if hasattr(self, 'countdown_label'):
                    self.app.countdown_manager.set_countdown_label(self.countdown_label)
                
                # Always auto-transition when countdown finishes
                self.app.countdown_manager.set_countdown_finish_callback(self.auto_transition_from_math)
                # Set up urgency styling updates
                self.app.countdown_manager.set_countdown_update_callback(self.update_countdown_urgency)
                self.app.countdown_manager.start_countdown(self.countdown_minutes, self.screen_name)
                
                # Position corner countdown after screen is shown
                if hasattr(self, 'corner_countdown_label'):
                    self.position_corner_countdown()
            except Exception as e:
                print(f"⚠️ Error setting up math task countdown: {e}")
                # Continue without countdown instead of crashing
                pass
    
    def on_enter_pressed(self):
        """Handle Enter key in developer mode."""
        if self.developer_mode:
            print("🧮 Enter pressed in Math task - Skipping to Post-study relaxation...")
            self.log_action("MATH_ENTER_KEY_DEVELOPER", "Enter key pressed - developer mode skip")
            self.transition_to_next_screen()
    
    def update_countdown_urgency(self, remaining_seconds):
        """Update countdown display styling based on urgency - similar to descriptive task."""
        if not hasattr(self, 'countdown_label') or not self.countdown_label:
            return
            
        try:
            # Update styling based on remaining time
            if remaining_seconds > 60:
                # Normal state - green
                color = "#4CAF50"
                background = "rgba(0, 100, 0, 100)"
            elif remaining_seconds > 30:
                # Warning state - orange
                color = "#FFA500" 
                background = "rgba(255, 165, 0, 150)"
            elif remaining_seconds > 10:
                # Critical state - red
                color = "#FF0000"
                background = "rgba(255, 0, 0, 150)"
            else:
                # Emergency state - flashing red
                color = "#FF0000"
                background = "rgba(255, 0, 0, 200)"
            
            # Apply updated styling
            self.countdown_label.setStyleSheet(f"""
                color: {color}; 
                background-color: {background}; 
                padding: 15px; 
                border-radius: 10px;
                border: 3px solid {color};
                font-weight: bold;
                font-size: 20px;
            """)
        except Exception as e:
            print(f"⚠️ Error updating countdown urgency: {e}")
    
    def auto_transition_from_math(self):
        """Auto-transition when countdown finishes."""
        if self.app.current_screen == self.screen_name:
            mode_text = "developer mode" if self.developer_mode else "production mode"
            print(f"⏰ Math task countdown finished - Auto-transitioning to Post-study relaxation ({mode_text})")
            self.log_action("MATH_COUNTDOWN_AUTO_TRANSITION", f"Math task countdown completed in {mode_text}, automatically transitioning to post-study relaxation")
            self.transition_to_next_screen()
    
    def transition_to_next_screen(self):
        """Transition to the next screen (Content Performance Task)."""
        try:
            print("🧮 Math transition: Moving to Content Performance Task")
            if hasattr(self.app, 'content_performance_screen'):
                self.app.switch_to_screen(self.app.content_performance_screen)
            else:
                self.app.switch_to_content_performance()
        except Exception as e:
            print(f"⚠️ Error in math task transition: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            # Try to gracefully continue by calling the fallback method
            try:
                self.app.switch_to_content_performance()
            except Exception as fallback_error:
                print(f"⚠️ Fallback transition also failed: {fallback_error}")


class ContentPerformanceScreen(BaseScreen):
    """Screen for showing the assigned content performance task."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.assigned_task = None
        self.content_label = None
        
        try:
            from config import CONTENT_PERFORMANCE_TEXT, CONTENT_PERFORMANCE_BG_COLOR, COLORS
            self.instruction_text = CONTENT_PERFORMANCE_TEXT
            self.background_color = CONTENT_PERFORMANCE_BG_COLOR
            self.colors = COLORS
        except ImportError:
            # Fallback values
            self.instruction_text = "Follow the instructions by the instructor and finish your task on Samsung phone"
            self.background_color = '#2E5A87'
            self.colors = {'title': 'white', 'text_primary': 'white'}
    
    def setup_screen(self):
        """Setup the content performance task screen."""
        try:
            from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QPushButton
            from PyQt6.QtGui import QFont
            from config import TASK_SELECTION_MODE
            
            self.set_background_color(self.background_color)
            
            # Get task instructions from task manager
            if hasattr(self.app, 'task_manager') and hasattr(self.app, 'participant_id'):
                task_info = self.app.task_manager.get_content_performance_instructions(self.app.participant_id)
            else:
                # Fallback if no task manager or participant ID
                task_info = {
                    "mode": "unknown",
                    "instruction_text": "Please follow the instructions on the Samsung phone to complete your task.",
                    "assigned_task": "mandala",
                    "show_task_options": False
                }
            
            # Title
            title = self.create_title(
                "Content Performance Task",
                font_size=32,
                color=self.colors['title']
            )
            self.layout.addWidget(title)
            self.layout.addSpacing(20)
            
            # Main instruction text
            instruction_label = QLabel(task_info["instruction_text"])
            instruction_label.setFont(QFont('Arial', 18))
            instruction_label.setStyleSheet(f"color: {self.colors['text_primary']}; background-color: transparent; line-height: 1.4;")
            instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            instruction_label.setWordWrap(True)
            self.layout.addWidget(instruction_label)
            self.layout.addSpacing(30)
            
            # Handle different selection modes
            if task_info["mode"] == "self_selection" and task_info["show_task_options"]:
                # Self-selection mode: show task selection buttons
                self.setup_task_selection_buttons(task_info["task_options"])
            else:
                # Random assignment mode: show assigned task info and continue button
                if task_info.get("assigned_task"):
                    self.assigned_task = task_info["assigned_task"]
                    # Show specific task information if available
                    if task_info.get("assigned_task_info"):
                        task_specific_label = QLabel(f"Task: {task_info['assigned_task_info']['brief']}")
                        task_specific_label.setFont(QFont('Arial', 22, QFont.Weight.Bold))
                        task_specific_label.setStyleSheet(f"color: {self.colors['title']}; background-color: rgba(0, 0, 0, 100); padding: 15px; border-radius: 10px;")
                        task_specific_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.layout.addWidget(task_specific_label)
                        self.layout.addSpacing(20)
                
                # Continue button for assigned tasks
                self.setup_continue_button()
            
            # Log screen display with task information
            self.log_action("CONTENT_PERFORMANCE_SCREEN_DISPLAYED", 
                           f"Content performance screen displayed - Mode: {task_info['mode']}, Task: {task_info.get('assigned_task', 'selection')}")
                           
        except Exception as e:
            print(f"⚠️ Error setting up content performance screen: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            # Fallback to simple screen
            self.setup_fallback_screen()
    
    def setup_task_selection_buttons(self, task_options):
        """Setup task selection buttons for self-selection mode."""
        try:
            from PyQt6.QtWidgets import QVBoxLayout, QPushButton
            
            selection_label = QLabel("Please select your preferred task:")
            selection_label.setFont(QFont('Arial', 20, QFont.Weight.Bold))
            selection_label.setStyleSheet(f"color: {self.colors['title']}; background-color: transparent;")
            selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(selection_label)
            self.layout.addSpacing(20)
            
            # Create buttons for each task option
            for task_key, task_info in task_options.items():
                task_button = QPushButton(f"{task_info['name']}\n{task_info['brief']}")
                task_button.setFont(QFont('Arial', 16))
                task_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 2px solid #45a049;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                    }
                """)
                task_button.setMinimumHeight(80)
                task_button.clicked.connect(lambda checked, task=task_key: self.on_task_selected(task))
                
                # Center the button
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                button_layout.addWidget(task_button)
                button_layout.addStretch()
                self.layout.addLayout(button_layout)
                self.layout.addSpacing(10)
                
        except Exception as e:
            print(f"⚠️ Error setting up task selection buttons: {e}")
            self.setup_continue_button()  # Fallback to continue button
    
    def setup_continue_button(self):
        """Setup continue button for assigned tasks."""
        try:
            from PyQt6.QtWidgets import QHBoxLayout
            
            continue_button = self.create_button(
                "CONTINUE TO TASK",
                command=self.transition_to_post_study_rest,
                font_size=20,
                width=200,
                height=60,
                bg_color='#4CAF50',
                fg_color='white'
            )
            
            # Center the button
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(continue_button)
            button_layout.addStretch()
            self.layout.addLayout(button_layout)
            
        except Exception as e:
            print(f"⚠️ Error setting up continue button: {e}")
    
    def setup_fallback_screen(self):
        """Setup a simple fallback screen if there are errors."""
        try:
            from PyQt6.QtWidgets import QLabel, QHBoxLayout
            
            fallback_label = QLabel("Please complete your assigned task on the Samsung phone.")
            fallback_label.setFont(QFont('Arial', 20))
            fallback_label.setStyleSheet(f"color: {self.colors['text_primary']}; background-color: transparent;")
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(fallback_label)
            
            self.setup_continue_button()
            
        except Exception as e:
            print(f"⚠️ Even fallback screen failed: {e}")
    
    def on_task_selected(self, selected_task):
        """Handle task selection in self-selection mode."""
        try:
            print(f"🎯 User selected task: {selected_task}")
            
            # Save the selection using task manager
            if hasattr(self.app, 'task_manager') and hasattr(self.app, 'participant_id'):
                success = self.app.task_manager.save_self_selected_task(self.app.participant_id, selected_task)
                if success:
                    self.assigned_task = selected_task
                    self.log_action("TASK_SELF_SELECTED", f"User selected task: {selected_task}")
                    
                    # Proceed to post-study rest
                    self.transition_to_post_study_rest()
                else:
                    print("⚠️ Failed to save task selection")
            else:
                print("⚠️ No task manager or participant ID available")
                # Fallback: still proceed but log the issue
                self.assigned_task = selected_task
                self.log_action("TASK_SELF_SELECTED_FALLBACK", f"User selected task: {selected_task} (fallback mode)")
                self.transition_to_post_study_rest()
                
        except Exception as e:
            print(f"⚠️ Error handling task selection: {e}")
            # Proceed anyway to avoid blocking the user
            self.assigned_task = selected_task
            self.transition_to_post_study_rest()
    
    def transition_to_post_study_rest(self):
        """Transition to post-study relaxation screen."""
        try:
            print("📱 Content performance transition: Moving to Post-study relaxation")
            self.log_action("CONTENT_PERFORMANCE_COMPLETED", 
                           f"Content performance task completed for: {self.assigned_task}")
            
            if hasattr(self.app, 'post_study_rest_screen'):
                self.app.switch_to_screen(self.app.post_study_rest_screen)
            else:
                self.app.switch_to_post_study_rest()
        except Exception as e:
            print(f"⚠️ Error in content performance transition: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            # Try to gracefully continue by calling the fallback method
            try:
                self.app.switch_to_post_study_rest()
            except Exception as fallback_error:
                print(f"⚠️ Fallback transition also failed: {fallback_error}")


class PostStudyRestScreen(BaseScreen):
    """Screen for post-study relaxation with video background."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.video_widget = None
        self.background_color = 'black'
        
        # Load configuration or use defaults
        try:
            from config import DEVELOPER_MODE, COLORS, RELAXATION_COUNTDOWN_MINUTES
            self.developer_mode = DEVELOPER_MODE
            self.colors = COLORS
            self.countdown_minutes = RELAXATION_COUNTDOWN_MINUTES
        except ImportError:
            self.developer_mode = False
            self.colors = {'title': 'white', 'text_primary': 'white', 'relaxation_text': '#ffffff'}
            self.countdown_minutes = 10
    
    def setup_screen(self):
        """Setup the post-study relaxation screen with video background and responsive layout."""
        try:
            from PyQt6.QtWidgets import QLabel
            from PyQt6.QtGui import QFont
            from PyQt6.QtCore import QTimer
            
            self.set_background_color(self.background_color)
            
            # Get screen dimensions for responsive scaling
            screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
            screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
            
            # Calculate responsive sizes
            video_min_width = max(600, int(screen_width * 0.6))
            video_min_height = max(450, int(screen_height * 0.6))
            text_font_size = max(32, min(96, int(screen_width * 0.05)))
            
            # Setup video display area - responsive sizing
            self.video_widget = QLabel()
            self.video_widget.setStyleSheet(f"background-color: {self.background_color}; border: 2px solid #444444; border-radius: 8px;")
            self.video_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.video_widget.setMinimumSize(video_min_width, video_min_height)
            self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.layout.addWidget(self.video_widget)
            self.add_widget(self.video_widget)
            
            # Add some spacing before the text
            self.layout.addSpacing(30)
            
            # Create text overlay - post-study message with better sizing
            try:
                from config import COLORS
            except ImportError:
                COLORS = {'relaxation_text': '#ffffff'}
            
            # Calculate better font size for the overlay text
            overlay_font_size = max(24, min(48, int(screen_width * 0.025)))
                
            relaxation_label = QLabel("Study Complete - Thank You!")
            relaxation_label.setFont(QFont('Arial', overlay_font_size, QFont.Weight.Bold))
            relaxation_label.setStyleSheet(f"""
                color: {COLORS.get('relaxation_text', '#ffffff')}; 
                background-color: rgba(0, 0, 0, 150); 
                padding: 20px; 
                border-radius: 15px;
                font-size: {overlay_font_size}px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                border: 2px solid rgba(255, 255, 255, 0.3);
            """)
            relaxation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            relaxation_label.setWordWrap(True)
            self.layout.addWidget(relaxation_label)
            self.add_widget(relaxation_label)
            
            # Add spacing
            self.layout.addSpacing(20)
            
            # Secondary message
            secondary_font_size = max(16, min(24, int(screen_width * 0.015)))
            secondary_label = QLabel("Please relax and continue to the final survey when ready.")
            secondary_label.setFont(QFont('Arial', secondary_font_size))
            secondary_label.setStyleSheet(f"""
                color: {COLORS.get('relaxation_text', '#ffffff')}; 
                background-color: rgba(0, 0, 0, 100); 
                padding: 15px; 
                border-radius: 10px;
                font-size: {secondary_font_size}px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            """)
            secondary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            secondary_label.setWordWrap(True)
            self.layout.addWidget(secondary_label)
            self.add_widget(secondary_label)
            
            # Initialize and start video - try to load actual video
            try:
                from config import RELAXATION_VIDEO_PATH
                
                # Check if video file exists
                video_path = RELAXATION_VIDEO_PATH
                if os.path.exists(video_path):
                    print(f"📹 Loading post-study relaxation video from: {video_path}")
                    self.app.video_manager.init_video(video_path)
                    
                    # Set up video completion callback for auto-transition
                    self.app.video_manager.set_video_end_callback(lambda: self.on_video_end())
                    
                    # Start video playback using PyQt6 timer with specific screen name
                    self.app.video_manager.start_pyqt_video_loop(self.video_widget, lambda: self.app.current_screen, "poststudyrest")
                else:
                    print(f"⚠️ Post-study video file not found: {video_path}, using placeholder")
                    # Replace the video area with a pleasant placeholder
                    self.video_widget.setText("Relaxing Environment")
                    self.video_widget.setStyleSheet(f"""
                        background-color: #2c3e50; 
                        border: 2px solid #444444; 
                        border-radius: 8px;
                        color: white;
                        font-size: 24px;
                        font-weight: bold;
                    """)
                    
                # Start hidden countdown for automatic transition to survey
                self.start_post_study_countdown(self.countdown_minutes)
                
            except (ImportError, Exception) as e:
                print(f"⚠️ Error setting up post-study video: {e}, using placeholder")
                # Config or video not available, show placeholder in video widget
                self.video_widget.setText("Peaceful Environment")
                self.video_widget.setStyleSheet(f"""
                    background-color: #2c3e50; 
                    border: 2px solid #444444; 
                    border-radius: 8px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                """)
            
            # Bind keys for developer mode
            if self.developer_mode:
                self.bind_key('<Return>', self.on_enter_pressed)
            
            self.bind_key('<KeyPress-q>', self.on_quit_pressed)
            self.setFocus()
            
            # Log screen display
            self.log_action("POST_STUDY_REST_SCREEN_DISPLAYED", "Post-study relaxation screen displayed with video/placeholder")
        except Exception as e:
            print(f"⚠️ Error setting up post-study rest screen: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            # Create a minimal fallback screen
            try:
                from PyQt6.QtWidgets import QLabel
                from PyQt6.QtGui import QFont
                
                fallback_label = QLabel("Study Complete - Thank You!")
                fallback_label.setFont(QFont('Arial', 32, QFont.Weight.Bold))
                fallback_label.setStyleSheet("""
                    color: white; 
                    background-color: rgba(0, 0, 0, 150); 
                    padding: 30px; 
                    border-radius: 15px;
                    border: 2px solid white;
                """)
                fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.layout.addWidget(fallback_label)
                
                # Add spacing
                self.layout.addSpacing(20)
                
                # Secondary message for fallback
                secondary_fallback = QLabel("Please continue to the final survey when ready.")
                secondary_fallback.setFont(QFont('Arial', 18))
                secondary_fallback.setStyleSheet("""
                    color: white; 
                    background-color: rgba(0, 0, 0, 100); 
                    padding: 20px; 
                    border-radius: 10px;
                """)
                secondary_fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.layout.addWidget(secondary_fallback)
                
                self.log_action("POST_STUDY_REST_FALLBACK", "Fallback post-study screen created due to setup error")
            except Exception as fallback_error:
                print(f"⚠️ Even fallback screen failed: {fallback_error}")
    
    def on_video_end(self):
        """Handle when post-study relaxation video reaches its natural end."""
        if self.app.current_screen == self.screen_name:
            print("🎬 Post-study relaxation video finished - Auto-transitioning to survey")
            self.log_action("POST_STUDY_VIDEO_END_TRANSITION", "Post-study relaxation video completed, automatically transitioning to survey")
            self.transition_to_poststudy_survey()
    
    def start_post_study_countdown(self, minutes):
        """Start hidden countdown for post-study relaxation screen auto-transition."""
        from PyQt6.QtCore import QTimer
        total_time = minutes * 60 * 1000
        
        def auto_transition():
            if self.app.current_screen == self.screen_name:
                print(f"⏰ Post-study relaxation countdown finished - Auto-transitioning to survey")
                self.log_action("POST_STUDY_COUNTDOWN_AUTO_TRANSITION", f"Post-study relaxation countdown ({minutes} minutes) completed, transitioning to survey")
                self.transition_to_poststudy_survey()
        
        QTimer.singleShot(total_time, auto_transition)
        self.log_action("POST_STUDY_COUNTDOWN_STARTED", f"Hidden countdown started for {minutes} minutes")
    
    def on_quit_pressed(self):
        """Handle Q key - quit application."""
        print("🔌 Q pressed - Quitting application...")
        self.log_action("KEY_PRESS", "Q key pressed - quitting application")
        self.app.quit_app()
    
    def transition_to_poststudy_survey(self):
        """Transition to the poststudy survey."""
        try:
            print("📊 Post-study rest transition: Moving to Poststudy Survey")
            self.log_action("POST_STUDY_REST_TO_SURVEY", "Transitioning to poststudy survey")
            
            if hasattr(self.app, 'switch_to_poststudy_survey'):
                self.app.switch_to_poststudy_survey()
            else:
                print("⚠️ No poststudy survey method available")
        except Exception as e:
            print(f"⚠️ Error in post-study rest transition: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
    
    def on_enter_pressed(self):
        """Handle Enter key - go to poststudy survey."""
        print("🔚 Enter pressed in Post-study rest - Going to poststudy survey...")
        self.log_action("POST_STUDY_ENTER_KEY", "Enter key pressed - going to poststudy survey")
        self.transition_to_poststudy_survey()