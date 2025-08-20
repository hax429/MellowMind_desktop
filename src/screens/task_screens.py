#!/usr/bin/env python3

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter
import os
import cv2
import random
from .base_screen import BaseScreen
from countdown_widget import CountdownWidget


class TransitionScreen(BaseScreen):
    """Screen for displaying transition instructions before tasks."""
    
    def __init__(self, app_instance, logging_manager=None, task_type=None, next_screen_callback=None):
        super().__init__(app_instance, logging_manager)
        self.task_type = task_type
        self.next_screen_callback = next_screen_callback
        
        # Load configuration or use defaults
        try:
            from config import (COLORS, TRANSITION_INSTRUCTION_TEXT, 
                              TRANSITION_MESSAGES, TRANSITION_IMAGES, UI_SETTINGS)
            self.background_color = COLORS['background_primary']
            self.colors = COLORS
            self.ui_settings = UI_SETTINGS
            self.instruction_text = TRANSITION_INSTRUCTION_TEXT
            self.messages = TRANSITION_MESSAGES
            self.images = TRANSITION_IMAGES
        except ImportError:
            # Fallback values
            self.background_color = '#220000'
            self.colors = {'title': 'white', 'text_primary': 'white', 'text_accent': '#ffaa44'}
            self.ui_settings = {'border_radius_large': '15px', 'line_height_normal': '1.4'}
            self.instruction_text = "Please listen carefully for the instructor on how to proceed to the next part."
            self.messages = {}
            self.images = {}
    
    def setup_screen(self):
        """Setup the transition screen with responsive layout."""
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive font sizes
        title_font_size = max(24, min(48, int(screen_width * 0.025)))
        instruction_font_size = max(16, min(28, int(screen_width * 0.015)))
        message_font_size = max(18, min(32, int(screen_width * 0.017)))
        button_font_size = max(16, min(28, int(screen_width * 0.015)))
        
        # Title
        title = self.create_title(
            "Task Transition",
            font_size=title_font_size,
            color=self.colors['title']
        )
        self.layout.addWidget(title)
        self.layout.addStretch(1)
        
        # Main instruction text
        instruction_label = self.create_instruction(
            self.instruction_text,
            font_size=instruction_font_size,
            color=self.colors['text_primary']
        )
        instruction_label.setStyleSheet(f"""
            color: {self.colors['text_primary']}; 
            background-color: {self.colors['background_overlay']}; 
            padding: {self.ui_settings.get('padding_medium', '20px')}; 
            border-radius: {self.ui_settings.get('border_radius_large', '15px')};
            font-size: {instruction_font_size}px;
            font-weight: bold;
            line-height: {self.ui_settings.get('line_height_normal', '1.4')};
        """)
        self.layout.addWidget(instruction_label)
        self.layout.addStretch(1)
        
        # Task-specific message
        if self.task_type and self.task_type in self.messages:
            task_message = self.create_instruction(
                self.messages[self.task_type],
                font_size=message_font_size,
                color=self.colors['text_accent']
            )
            task_message.setStyleSheet(f"""
                color: {self.colors['text_accent']}; 
                background-color: {self.colors['background_overlay_light']}; 
                padding: {self.ui_settings.get('padding_large', '25px')}; 
                border-radius: {self.ui_settings.get('border_radius_large', '15px')};
                font-size: {message_font_size}px;
                font-weight: bold;
                line-height: {self.ui_settings.get('line_height_normal', '1.4')};
            """)
            self.layout.addWidget(task_message)
            self.layout.addStretch(1)
        
        # Add image for specific tasks (like stroop)
        if self.task_type and self.task_type in self.images:
            self.add_task_image(self.images[self.task_type])
        
        # Go to next session button
        button_width = max(200, min(400, int(screen_width * 0.2)))
        button_height = max(60, min(120, int(screen_height * 0.1)))
        
        next_button = self.create_button(
            "GO TO NEXT SESSION",
            command=self.on_next_button_pressed,
            font_size=button_font_size,
            width=button_width,
            height=button_height
            # Colors now come from config via base_screen.py
        )
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(next_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.layout.addStretch(2)
        
        # Set initial focus to the button
        next_button.setFocus()
        
        # Log screen display
        self.log_action("TRANSITION_SCREEN_DISPLAYED", f"Transition screen displayed for {self.task_type} task")
    
    def add_task_image(self, image_path):
        """Add a task-specific image to the screen."""
        try:
            if os.path.exists(image_path):
                # Create image label
                image_label = QLabel()
                pixmap = QPixmap(image_path)
                
                # Scale image to fit screen while maintaining aspect ratio
                screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
                max_width = min(400, int(screen_width * 0.3))
                max_height = 300
                
                scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image_label.setStyleSheet("border: 2px solid #444444; border-radius: 8px; background-color: rgba(0, 0, 0, 50);")
                
                self.layout.addWidget(image_label)
                self.add_widget(image_label)
                self.layout.addStretch(1)
                
                print(f"📸 Added image for {self.task_type} task: {image_path}")
            else:
                print(f"⚠️ Image not found: {image_path}")
        except Exception as e:
            print(f"⚠️ Error adding image: {e}")
    
    def on_next_button_pressed(self):
        """Handle next button press."""
        print(f"▶️ Transition complete - Moving to {self.task_type} task")
        self.log_action("TRANSITION_COMPLETED", f"User clicked next button - transitioning to {self.task_type} task")
        
        if self.next_screen_callback:
            self.next_screen_callback()
        else:
            print("⚠️ No next screen callback provided")
    
    def set_task_info(self, task_type, next_screen_callback):
        """Set the task type and callback for this transition screen."""
        self.task_type = task_type
        self.next_screen_callback = next_screen_callback


class RelaxationScreen(BaseScreen):
    """Screen for relaxation with video background."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.video_widget = None
        try:
            from config import COLORS
            self.background_color = COLORS['background_secondary']
        except ImportError:
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
        try:
            from config import COLORS, UI_SETTINGS
            border_color = COLORS['border_default']
            border_radius = UI_SETTINGS['border_radius_medium']
        except ImportError:
            border_color = '#444444'
            border_radius = '8px'
        self.video_widget.setStyleSheet(f"background-color: {self.background_color}; border: 2px solid {border_color}; border-radius: {border_radius};")
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
        """Transition to the next screen (during-study survey 1)."""
        print("🧘 Relaxation transition: Moving to during-study survey 1")
        self.app.switch_to_duringstudy1_survey()


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
        self.developer_skip_button = None
        
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
            
        # Select a random prompt instead of using index 0
        import random
        self.current_prompt_index = random.randint(0, len(self.prompts) - 1) if self.prompts else 0
        print(f"🎯 DEBUG: Selected random prompt {self.current_prompt_index + 1}/{len(self.prompts)}: {self.prompts[self.current_prompt_index] if self.prompts else 'No prompts available'}")
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
        
        # Countdown timer using unified widget (if enabled)
        if self.countdown_enabled:
            # Create unified countdown widget
            self.countdown_widget = CountdownWidget(
                parent_screen=self,
                countdown_minutes=self.countdown_minutes,
                show_main_display=True,
                show_corner_display=True
            )
            # References for compatibility with existing countdown manager
            self.countdown_label = self.countdown_widget.countdown_label
            self.corner_countdown_label = self.countdown_widget.corner_countdown_label
        
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
        
        # Developer skip button (only show in developer mode)
        if self.developer_mode:
            self.setup_developer_skip_button(screen_width, screen_height)
        
        # Set initial focus to the start button
        self.descriptive_start_button.setFocus()
        
        # Log screen display
        self.log_action("DESCRIPTIVE_TASK_SCREEN_DISPLAYED", f"Descriptive task screen displayed with {len(self.prompts)} prompts available")
    
    def setup_response_textbox(self):
        """Setup the response textbox area with responsive sizing."""
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive sizes - increased for better visibility
        label_font_size = max(14, min(24, int(screen_width * 0.013)))
        text_font_size = max(12, min(20, int(screen_width * 0.011)))
        textbox_height = max(400, min(700, int(screen_height * 0.45)))  # Increased height
        word_count_font_size = max(12, min(18, int(screen_width * 0.010)))
        
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
        self.response_text.setMaximumHeight(int(screen_height * 0.5))  # Increased max height
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
    
    def setup_developer_skip_button(self, screen_width, screen_height):
        """Setup developer-only skip button for quick navigation."""
        # Calculate responsive button size
        button_width = max(120, min(200, int(screen_width * 0.12)))
        button_height = max(40, min(60, int(screen_height * 0.06)))
        button_font_size = max(12, min(18, int(screen_width * 0.012)))
        
        # Create skip button (initially hidden)
        self.developer_skip_button = self.create_button(
            "DEV: SKIP TO STROOP",
            command=self.on_developer_skip_pressed,
            font_size=button_font_size,
            width=button_width,
            height=button_height,
            bg_color='#FF4444',  # Red to indicate developer feature
            fg_color='white'
        )
        
        # Position button in top-left corner
        self.developer_skip_button.hide()  # Initially hidden
        self.add_widget(self.developer_skip_button)
        
        # Use absolute positioning for the button
        self.developer_skip_button.setParent(self)
        self.developer_skip_button.setGeometry(20, 20, button_width, button_height)
    
    def position_corner_countdown(self):
        """Position the corner countdown timer using unified widget."""
        if hasattr(self, 'countdown_widget') and self.countdown_widget:
            self.countdown_widget.position_corner_countdown()
        else:
            print(f"🎯 DEBUG: Descriptive unified countdown widget not available for positioning")
    
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
        
        # Start unified countdown if enabled
        if self.countdown_enabled:
            try:
                if hasattr(self, 'countdown_widget'):
                    # Use unified countdown widget to start countdown
                    self.countdown_widget.start_countdown(self.auto_transition_from_descriptive)
                    print(f"🎯 Descriptive task unified countdown started successfully")
            except Exception as e:
                print(f"⚠️ Error setting up descriptive task countdown: {e}")
                # Continue without countdown instead of crashing
                pass
        
        # Show developer skip button if in developer mode
        if self.developer_mode and hasattr(self, 'developer_skip_button') and self.developer_skip_button:
            self.developer_skip_button.show()
            self.developer_skip_button.raise_()  # Bring to front
            print("🔧 Developer skip button shown")
    
    def on_developer_skip_pressed(self):
        """Handle developer skip button press."""
        print("🔧 Developer skip button pressed - Skipping to Stroop task...")
        self.log_action("DESCRIPTIVE_DEVELOPER_SKIP", "Developer skip button pressed - jumping to Stroop task")
        
        # Stop the countdown timer if running
        if hasattr(self.app, 'countdown_manager'):
            self.app.countdown_manager.stop_countdown()
            print("⏰ Countdown stopped by developer skip button")
        
        # Save current response and transition
        self.save_current_response()
        self.transition_to_next_screen()
    
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
        """Transition to the next screen (Stroop transition)."""
        print("📝 Descriptive task transition: Moving to Stroop task transition")
        self.app.switch_to_stroop_transition()


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
        self.transition_triggered = False
        
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
        
        # Calculate responsive sizes - increased for better visibility
        video_min_width = max(800, int(screen_width * 0.8))  # Increased from 0.7 to 0.8
        video_min_height = max(500, int(screen_height * 0.65))  # Increased from 0.55 to 0.65
        
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
        
        # Countdown timer using unified widget (corner only for Stroop)
        if self.countdown_enabled:
            # Create unified countdown widget (corner display only for Stroop)
            self.countdown_widget = CountdownWidget(
                parent_screen=self,
                countdown_minutes=self.countdown_minutes,
                show_main_display=False,
                show_corner_display=True
            )
            # References for compatibility with existing countdown manager
            self.corner_countdown_label = self.countdown_widget.corner_countdown_label
        
        # Video display area - responsive sizing and emphasized
        self.video_widget = QLabel()
        self.video_widget.setStyleSheet(f"background-color: black; border: 3px solid #444444; border-radius: 8px;")
        self.video_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_widget.setMinimumSize(video_min_width, video_min_height)
        self.video_widget.setMaximumSize(int(screen_width * 0.95), int(screen_height * 0.8))  # Increased max size
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
        """Position the corner countdown timer using unified widget."""
        if hasattr(self, 'countdown_widget') and self.countdown_widget:
            self.countdown_widget.position_corner_countdown()
        else:
            print(f"🎦 DEBUG: Stroop unified countdown widget not available for positioning")
    
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
            # Set up video completion callback for auto-transition
            self.app.video_manager.set_video_end_callback(lambda: self.on_video_end())
            
            # Start video playback from 3-minute mark (180 seconds)
            fps = self.app.video_manager.cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(180 * fps)  # 180 seconds * fps
            self.app.video_manager.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.app.video_manager.start_pyqt_video_loop(self.video_widget, lambda: self.app.current_screen, "stroop")
            print("🎬 Stroop video started from 3-minute mark")
            self.log_action("STROOP_VIDEO_STARTED_3_MIN", "Stroop video started from 3:00 mark")
        
        # Start unified countdown if enabled
        if self.countdown_enabled:
            try:
                if hasattr(self, 'countdown_widget'):
                    # Use unified countdown widget to start countdown
                    self.countdown_widget.start_countdown(self.auto_transition_from_stroop)
                    print(f"🎦 Stroop task unified countdown started successfully")
            except Exception as e:
                print(f"⚠️ Error setting up stroop task countdown: {e}")
                # Continue without countdown instead of crashing
                pass
            
        # Set focus to main content
        self.setFocus()
    
    def on_video_end(self):
        """Handle when Stroop video reaches its natural end."""
        if self.app.current_screen == self.screen_name and not self.transition_triggered:
            self.transition_triggered = True
            print("🎬 Stroop video finished - Auto-transitioning to Math task")
            self.log_action("STROOP_VIDEO_END_TRANSITION", "Stroop video completed, automatically transitioning to Math task")
            self.transition_to_next_screen()
    
    def on_enter_pressed(self):
        """Handle Enter key in developer mode."""
        if self.developer_mode and not self.transition_triggered:
            self.transition_triggered = True
            print("🎯 Enter pressed in Stroop task - Skipping to Math task...")
            self.log_action("STROOP_ENTER_KEY_DEVELOPER", "Enter key pressed - developer mode skip")
            self.transition_to_next_screen()
    
    def auto_transition_from_stroop(self):
        """Auto-transition when countdown finishes."""
        if self.app.current_screen == self.screen_name and not self.transition_triggered:
            self.transition_triggered = True
            mode_text = "developer mode" if self.developer_mode else "production mode"
            print(f"⏰ Stroop task countdown finished - Auto-transitioning to Math task ({mode_text})")
            self.log_action("STROOP_COUNTDOWN_AUTO_TRANSITION", f"Stroop task countdown completed in {mode_text}, automatically transitioning to math")
            self.transition_to_next_screen()
    
    def transition_to_next_screen(self):
        """Transition to the next screen (Math task transition)."""
        print("🎬 Stroop transition: Moving to Math task transition")
        self.app.switch_to_math_transition()


class NativeStroopScreen(BaseScreen):
    """Screen for native Stroop task with generated word list."""
    
    def __init__(self, app_instance, logging_manager=None):
        print("🎨 DEBUG: Creating NativeStroopScreen instance")
        super().__init__(app_instance, logging_manager)
        print(f"🎨 DEBUG: NativeStroopScreen initialized with screen_name: {self.screen_name}")
        self.task_started = False
        self.corner_countdown_label = None
        self.stroop_start_button = None
        self.transition_triggered = False
        self.scroll_area = None
        self.word_container = None
        self.current_words = []
        
        # Stroop word and color lists
        self.words = ['red', 'green', 'blue', 'purple', 'brown']
        self.stroop_colors = ['red', 'green', 'blue', 'purple', 'brown']
        
        # Color mapping for CSS
        self.color_map = {
            'red': '#FF0000',
            'green': '#00FF00', 
            'blue': '#0000FF',
            'purple': '#800080',
            'brown': '#8B4513'
        }
        
        # Track last word and color to avoid consecutive duplicates
        self.last_word = None
        self.last_color = None
        
        # Track recent words and colors for better randomization
        self.recent_words = []
        self.recent_colors = []
        
        # Seed random number generator
        import time
        random.seed(int(time.time()))
        
        # Load configuration or use defaults
        try:
            from config import (BACKGROUND_COLOR, COLORS, COUNTDOWN_ENABLED, 
                              STROOP_COUNTDOWN_ENABLED, STROOP_COUNTDOWN_MINUTES,
                              DEVELOPER_MODE)
            self.background_color = BACKGROUND_COLOR
            self.colors = COLORS if isinstance(COLORS, dict) else {
                'title': 'white', 
                'text_primary': 'white',
                'countdown_normal': '#00FF00',
                'countdown_warning': '#FFFF00',
                'countdown_critical': '#FF0000'
            }
            self.countdown_enabled = COUNTDOWN_ENABLED and STROOP_COUNTDOWN_ENABLED
            self.countdown_minutes = STROOP_COUNTDOWN_MINUTES
            self.developer_mode = DEVELOPER_MODE
        except ImportError:
            # Fallback values
            self.background_color = '#8B0000'
            self.colors = {
                'title': 'white', 
                'text_primary': 'white',
                'countdown_normal': '#00FF00',
                'countdown_warning': '#FFFF00',
                'countdown_critical': '#FF0000'
            }
            self.countdown_enabled = True
            self.countdown_minutes = 1
            self.developer_mode = False
    
    def generate_stroop_word(self, position_in_batch=0):
        """Generate a Stroop word with improved randomization constraints."""
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # Get available words - avoid recent words
            recent_words_set = set(self.recent_words[-8:])
            available_words = [w for w in self.words if w not in recent_words_set]
            if not available_words:
                word_counts = {w: self.recent_words[-10:].count(w) for w in self.words}
                min_count = min(word_counts.values()) if word_counts else 0
                available_words = [w for w, count in word_counts.items() if count == min_count]
            
            word = random.choice(available_words)
            
            # Get available colors - avoid recent colors and word match
            recent_colors_set = set(self.recent_colors[-12:])
            available_colors = [c for c in self.stroop_colors 
                             if c != word and c not in recent_colors_set]
            
            if not available_colors:
                available_colors = [c for c in self.stroop_colors if c != word]
            
            if available_colors:
                color = random.choice(available_colors)
                
                # Update tracking lists
                self.recent_words.append(word)
                self.recent_colors.append(color)
                
                # Keep only last 30 items
                if len(self.recent_words) > 30:
                    self.recent_words = self.recent_words[-30:]
                if len(self.recent_colors) > 30:
                    self.recent_colors = self.recent_colors[-30:]
                
                self.last_word = word
                self.last_color = color
                
                return word, color
        
        # Fallback
        word = random.choice(self.words)
        available_colors = [c for c in self.stroop_colors if c != word]
        color = random.choice(available_colors) if available_colors else random.choice(self.stroop_colors)
        
        self.last_word = word
        self.last_color = color
        
        return word, color
    
    def generate_word_batch(self, count=20):
        """Generate a batch of Stroop words."""
        try:
            print(f"🎨 DEBUG: Generating word batch with count={count}")
            words = []
            
            for i in range(count):
                position_in_batch = len(self.current_words) + i
                word, color = self.generate_stroop_word(position_in_batch)
                words.append((word, color))
            
            print(f"🎨 DEBUG: Generated {len(words)} words")
            return words
            
        except Exception as e:
            print(f"🚨 ERROR in generate_word_batch: {e}")
            import traceback
            print(f"🚨 Full traceback: {traceback.format_exc()}")
            return []
    
    def reset_randomization_state(self):
        """Reset randomization state for a fresh start."""
        import time
        random.seed(int(time.time() * 1000000) % 2**32)
        
        self.recent_words = []
        self.recent_colors = []
        self.last_word = None
        self.last_color = None
        
        print(f"🎨 Randomization state reset with new seed")
    
    def setup_screen(self):
        """Setup the native Stroop task screen."""
        try:
            print(f"🎨 DEBUG: Setting up Native Stroop screen with name: {self.screen_name}")
            self.set_background_color(self.background_color)
            
            # Get screen dimensions for responsive scaling
            screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
            screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
            print(f"🎨 DEBUG: Screen dimensions: {screen_width}x{screen_height}")
            
            # Calculate responsive font sizes
            title_font_size = max(24, min(56, int(screen_width * 0.030)))
            instruction_font_size = max(14, min(24, int(screen_width * 0.013)))
            button_font_size = max(16, min(28, int(screen_width * 0.015)))
            
            # Title
            title = self.create_title(
                "Stroop Task",
                font_size=title_font_size,
                color=self.colors['title']
            )
            self.layout.addWidget(title)
            self.layout.addStretch(1)
            
            # Instructions
            instruction = self.create_instruction(
                "Say the COLOR of each word (not the word itself). Scroll to see more words.",
                font_size=instruction_font_size,
                color=self.colors['text_primary']
            )
            self.layout.addWidget(instruction)
            self.layout.addStretch(1)
            
            # Countdown timer using unified widget (corner only for Stroop)
            print(f"🎨 DEBUG: Countdown enabled: {self.countdown_enabled}")
            if self.countdown_enabled:
                print("🎨 DEBUG: Creating countdown widget")
                self.countdown_widget = CountdownWidget(
                    parent_screen=self,
                    countdown_minutes=self.countdown_minutes,
                    show_main_display=False,
                    show_corner_display=True
                )
                self.corner_countdown_label = self.countdown_widget.corner_countdown_label
                print("🎨 DEBUG: Countdown widget created successfully")
            
            # Start button
            button_width = max(150, min(300, int(screen_width * 0.15)))
            button_height = max(50, min(100, int(screen_height * 0.08)))
            
            self.stroop_start_button = self.create_button(
                "START TASK",
                command=self.start_stroop_task,
                font_size=button_font_size,
                width=button_width,
                height=button_height,
                bg_color='#4CAF50',
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
            
            # Setup scrollable word area (initially hidden)
            self.setup_word_area()
            
            # Bind keys for developer mode
            if self.developer_mode:
                print("🎨 DEBUG: Binding Enter key for developer mode")
                self.bind_key('<Return>', self.on_enter_pressed)
            
            # Set initial focus to start button
            self.stroop_start_button.setFocus()
            
            # Log screen display
            self.log_action("NATIVE_STROOP_SCREEN_DISPLAYED", "Native Stroop task screen displayed")
            
            print("🎨 DEBUG: Native Stroop screen setup completed successfully")
            
        except Exception as e:
            print(f"🚨 ERROR in setup_screen: {e}")
            import traceback
            print(f"🚨 Full traceback: {traceback.format_exc()}")
            try:
                self.log_action("NATIVE_STROOP_SETUP_ERROR", f"Error in setup_screen: {e}")
            except:
                print("🚨 Could not log setup error")
            raise
    
    def setup_word_area(self):
        """Setup the scrollable word display area."""
        try:
            print("🎨 DEBUG: Setting up word area")
            
            # Get screen dimensions
            screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
            screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
            
            # Calculate area dimensions - make it take more space
            area_height = max(600, int(screen_height * 0.75))
            
            # Create scroll area
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll_area.setMinimumHeight(area_height)
            self.scroll_area.setMaximumHeight(area_height)
            
            # Style the scroll area
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: 3px solid #444444;
                    border-radius: 8px;
                    background-color: black;
                }}
                QScrollBar:vertical {{
                    background-color: #444444;
                    width: 20px;
                    border-radius: 10px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #666666;
                    border-radius: 10px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: #888888;
                }}
            """)
            
            # Create container widget for words using QTextEdit for proper scrolling
            from PyQt6.QtWidgets import QTextEdit
            self.word_container = QTextEdit()
            self.word_container.setReadOnly(True)
            self.word_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.word_container.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.word_container.setStyleSheet("""
                QTextEdit {
                    background-color: black;
                    color: white;
                    padding: 20px;
                    border: none;
                    font-family: Arial;
                }
            """)
            
            # Set scroll area widget
            self.scroll_area.setWidget(self.word_container)
            
            # Enable proper focus and wheel events
            self.scroll_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.word_container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            # Initially hide the scroll area
            self.scroll_area.hide()
            
            # Add to layout
            self.layout.addWidget(self.scroll_area)
            self.add_widget(self.scroll_area)
            
            # Connect scroll event to generate more words
            self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
            
            print("🎨 DEBUG: Word area setup completed successfully")
            
        except Exception as e:
            print(f"🚨 ERROR in setup_word_area: {e}")
            import traceback
            print(f"🚨 Full traceback: {traceback.format_exc()}")
    
    def keyPressEvent(self, event):
        """Handle key press events, especially for Enter key in developer mode."""
        try:
            from PyQt6.QtCore import Qt
            
            # Handle Enter key in developer mode
            if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and self.developer_mode:
                print("🎯 DEBUG: Enter key detected via keyPressEvent")
                self.on_enter_pressed()
                event.accept()
                return
            
            # Pass to parent for other keys
            super().keyPressEvent(event)
            
        except Exception as e:
            print(f"⚠️ Error in keyPressEvent: {e}")
            super().keyPressEvent(event)
    
    def on_scroll(self, value):
        """Handle scroll events to generate more words when needed."""
        try:
            scroll_bar = self.scroll_area.verticalScrollBar()
            # When user scrolls near bottom, generate more words
            if value >= scroll_bar.maximum() - 100:
                self.add_more_words()
        except Exception as e:
            print(f"⚠️ Error in scroll handler: {e}")
    
    def add_more_words(self):
        """Add more words to the display."""
        try:
            new_words = self.generate_word_batch(50)  # Generate 50 more words
            self.current_words.extend(new_words)
            self.update_word_display()
        except Exception as e:
            print(f"⚠️ Error adding more words: {e}")
    
    def update_word_display(self):
        """Update the word display with current words in 10 columns."""
        try:
            print("🎨 DEBUG: Entering update_word_display")
            
            if not self.word_container:
                print("🎨 DEBUG: ERROR - word_container is None!")
                return
            
            print(f"🎨 DEBUG: Updating display with {len(self.current_words)} words")
            
            # Calculate responsive font size
            screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
            word_font_size = max(24, min(48, int(screen_width * 0.025)))
            
            # Create HTML content for words in a 10-column table layout
            html_content = """
            <div style='background-color: black; padding: 20px;'>
                <table style='width: 100%; border-collapse: separate; border-spacing: 15px;'>
            """
            
            # Arrange words in rows of 10 columns
            for i in range(0, len(self.current_words), 10):
                html_content += "<tr>"
                
                # Add up to 10 words per row
                for j in range(10):
                    if i + j < len(self.current_words):
                        word, color = self.current_words[i + j]
                        color_hex = self.color_map[color]
                        html_content += f"""
                        <td style='text-align: center; padding: 10px;'>
                            <span style='
                                color: {color_hex}; 
                                font-size: {word_font_size}px; 
                                font-weight: bold; 
                                font-family: Arial, sans-serif;
                                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                            '>{word}</span>
                        </td>
                        """
                    else:
                        html_content += "<td></td>"
                
                html_content += "</tr>"
            
            html_content += """
                </table>
            </div>
            """
            
            # Set the HTML content
            self.word_container.setHtml(html_content)
            print("🎨 DEBUG: Word display updated successfully")
            
        except Exception as e:
            print(f"🚨 ERROR in update_word_display: {e}")
            import traceback
            print(f"🚨 Full traceback: {traceback.format_exc()}")
    
    def position_corner_countdown(self):
        """Position the corner countdown timer using unified widget."""
        if hasattr(self, 'countdown_widget') and self.countdown_widget:
            self.countdown_widget.position_corner_countdown()
        else:
            print(f"🎨 DEBUG: Native Stroop unified countdown widget not available for positioning")
    
    def start_stroop_task(self):
        """Start the native Stroop task with countdown and word generation."""
        try:
            print("🚀 DEBUG: Entering start_stroop_task method")
            
            if self.task_started:
                print("🚀 DEBUG: Task already started, returning early")
                return
                
            print("🚀 Native Stroop task STARTED by user...")
            self.log_action("NATIVE_STROOP_TASK_STARTED", "Native Stroop task started by user button press")
            
            # Hide start button
            if hasattr(self, 'stroop_start_button') and self.stroop_start_button:
                self.stroop_start_button.hide()
                self.stroop_start_button.deleteLater()
                if hasattr(self, 'widgets') and self.stroop_start_button in self.widgets:
                    self.widgets.remove(self.stroop_start_button)
            
            # Mark as started
            self.task_started = True
            
            # Reset randomization state
            self.reset_randomization_state()
            
            # Generate initial words and show scroll area
            self.current_words = self.generate_word_batch(100)  # Start with 100 words
            print(f"🚀 DEBUG: Generated {len(self.current_words)} words")
            
            self.update_word_display()
            
            if hasattr(self, 'scroll_area') and self.scroll_area:
                self.scroll_area.show()
                print("🚀 DEBUG: Scroll area shown successfully")
            
            # Start countdown if enabled
            if self.countdown_enabled:
                try:
                    if hasattr(self, 'countdown_widget'):
                        self.countdown_widget.start_countdown(self.auto_transition_from_stroop)
                        print(f"🎨 Native Stroop countdown started")
                        
                        # Position corner countdown with delay
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(100, self.position_corner_countdown)
                except Exception as e:
                    print(f"⚠️ Error setting up countdown: {e}")
            
            # Set focus to scroll area for proper scrolling and Enter key handling
            if hasattr(self, 'scroll_area') and self.scroll_area:
                self.scroll_area.setFocus()
            else:
                self.setFocus()
            
            print("🚀 DEBUG: start_stroop_task completed successfully")
            
        except Exception as e:
            print(f"🚨 CRITICAL ERROR in start_stroop_task: {e}")
            import traceback
            print(f"🚨 Full traceback: {traceback.format_exc()}")
            try:
                self.log_action("NATIVE_STROOP_ERROR", f"Critical error in start_stroop_task: {e}")
            except:
                print("🚨 Could not log error action")
            raise
    
    def on_enter_pressed(self):
        """Handle Enter key in developer mode only."""
        try:
            print(f"🎯 DEBUG: on_enter_pressed called, developer_mode: {self.developer_mode}")
            
            # Only work in developer mode
            if not self.developer_mode:
                print("🎯 Enter key ignored - not in developer mode")
                return
                
            if not self.task_started:
                # If task hasn't started, start it
                print("🎯 Enter pressed - Starting Stroop task (developer mode)...")
                self.start_stroop_task()
                return
                
            if not self.transition_triggered and self.task_started:
                self.transition_triggered = True
                print("🎯 Enter pressed in Native Stroop task - Skipping to Math task (developer mode)...")
                self.log_action("NATIVE_STROOP_ENTER_KEY_DEVELOPER", "Enter key pressed - developer mode skip")
                
                # Stop any running countdown
                try:
                    if hasattr(self, 'countdown_widget') and self.countdown_widget:
                        self.countdown_widget.stop_countdown()
                        print("⏰ Countdown stopped by Enter key")
                except Exception as countdown_error:
                    print(f"⚠️ Error stopping countdown: {countdown_error}")
                
                # Transition with delay
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, self.safe_transition_to_next_screen)
                
        except Exception as e:
            print(f"⚠️ Error in Enter key handler: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
    
    def auto_transition_from_stroop(self):
        """Auto-transition when countdown finishes."""
        try:
            if self.app.current_screen == self.screen_name and not self.transition_triggered:
                self.transition_triggered = True
                mode_text = "developer mode" if self.developer_mode else "production mode"
                print(f"⏰ Native Stroop task countdown finished - Auto-transitioning to Math task ({mode_text})")
                self.log_action("NATIVE_STROOP_COUNTDOWN_AUTO_TRANSITION", f"Native Stroop task countdown completed in {mode_text}, automatically transitioning to math")
                self.safe_transition_to_next_screen()
        except Exception as e:
            print(f"⚠️ Error in auto transition: {e}")
    
    def safe_transition_to_next_screen(self):
        """Safe transition wrapper to prevent crashes."""
        try:
            self.transition_to_next_screen()
        except Exception as e:
            print(f"⚠️ Error in safe transition: {e}")
            
    def transition_to_next_screen(self):
        """Transition to the next screen (Math task transition)."""
        try:
            print("🎨 Native Stroop transition: Moving to Math task transition")
            
            # Ensure we're still on the current screen before transitioning
            if hasattr(self.app, 'current_screen') and self.app.current_screen != self.screen_name:
                print(f"⚠️ Warning: Already left {self.screen_name}, current screen is {self.app.current_screen}")
                return
            
            # Save any state if needed before transitioning
            if hasattr(self, 'current_words') and self.current_words:
                print(f"🎨 Generated {len(self.current_words)} words during session")
            
            # Check if the method exists before calling
            if hasattr(self.app, 'switch_to_math_transition'):
                self.app.switch_to_math_transition()
            else:
                print("⚠️ switch_to_math_transition method not found")
            
        except Exception as e:
            print(f"⚠️ Error in Native Stroop transition: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")


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
        
        # Countdown timer using unified widget (if enabled)
        if self.countdown_enabled:
            # Create unified countdown widget
            self.countdown_widget = CountdownWidget(
                parent_screen=self,
                countdown_minutes=self.countdown_minutes,
                show_main_display=True,
                show_corner_display=True
            )
            # References for compatibility with existing countdown manager
            self.countdown_label = self.countdown_widget.countdown_label
            self.corner_countdown_label = self.countdown_widget.corner_countdown_label
        
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
        """Position the corner countdown timer using unified widget."""
        if hasattr(self, 'countdown_widget') and self.countdown_widget:
            self.countdown_widget.position_corner_countdown()
        else:
            print(f"🎯 Math unified countdown widget not available for positioning")
    
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
        
        # Start unified countdown if enabled
        if self.countdown_enabled:
            try:
                if hasattr(self, 'countdown_widget'):
                    # Use unified countdown widget to start countdown with urgency callback
                    self.countdown_widget.start_countdown(
                        auto_transition_callback=self.auto_transition_from_math,
                        update_callback=self.update_countdown_urgency
                    )
                    print(f"🎯 Math task unified countdown started successfully")
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
        """Transition to the next screen (during-study survey 2)."""
        print("🧮 Math transition: Moving to during-study survey 2")
        self.app.switch_to_duringstudy2_survey()


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
        print("📱 Content performance transition: Moving to Post-study relaxation transition")
        self.log_action("CONTENT_PERFORMANCE_COMPLETED", 
                       f"Content performance task completed for: {self.assigned_task}")
        self.app.switch_to_relaxation_transition()


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