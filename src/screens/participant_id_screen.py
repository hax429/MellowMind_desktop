#!/usr/bin/env python3

from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QValidator
from .base_screen import BaseScreen


class ParticipantIDScreen(BaseScreen):
    """Screen for participant ID entry."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.participant_id_entry = None
        self.background_color = 'black'
    
    def setup_screen(self):
        """Setup the participant ID entry screen with responsive layout."""
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive font sizes
        title_font_size = max(24, min(48, int(screen_width * 0.025)))
        instruction_font_size = max(16, min(28, int(screen_width * 0.015)))
        entry_font_size = max(14, min(24, int(screen_width * 0.012)))
        
        # Title - made bigger and responsive
        title = self.create_title(
            "Moly - Performance Evaluation", 
            font_size=title_font_size, 
            color='white'
        )
        self.layout.addWidget(title)
        self.layout.addStretch(2)
        
        # Instructions - responsive font
        instruction = self.create_instruction(
            "Please enter your participant ID to begin:",
            font_size=instruction_font_size,
            color='white'
        )
        self.layout.addWidget(instruction)
        self.layout.addStretch(1)
        
        # Participant ID entry - responsive sizing
        self.participant_id_entry = QLineEdit()
        entry_width = max(200, min(500, int(screen_width * 0.25)))
        entry_height = max(40, min(80, int(screen_height * 0.06)))
        
        self.participant_id_entry.setMinimumSize(entry_width, entry_height)
        self.participant_id_entry.setMaximumSize(entry_width * 2, entry_height)
        self.participant_id_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.participant_id_entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                color: black;
                border: 3px solid gray;
                border-radius: 8px;
                font-size: {entry_font_size}px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        
        # Create custom validator for participant ID
        class ParticipantIDValidator(QValidator):
            def validate(self, text, pos):
                if all(c.isalnum() or c in ['_', '-'] for c in text):
                    return QValidator.State.Acceptable, text.upper(), pos
                return QValidator.State.Invalid, text, pos
        
        self.participant_id_entry.setValidator(ParticipantIDValidator())
        self.participant_id_entry.textChanged.connect(lambda text: self.participant_id_entry.setText(text.upper()))
        self.participant_id_entry.textChanged.connect(self.log_text_change)
        self.participant_id_entry.returnPressed.connect(self.submit_participant_id)
        
        # Center the entry widget
        entry_layout = QHBoxLayout()
        entry_layout.addStretch()
        entry_layout.addWidget(self.participant_id_entry)
        entry_layout.addStretch()
        self.layout.addLayout(entry_layout)
        self.layout.addStretch(1)
        
        # Add widget to tracking
        self.add_widget(self.participant_id_entry)
        
        # Submit button - responsive sizing and emphasized
        button_width = max(150, min(300, int(screen_width * 0.15)))
        button_height = max(50, min(100, int(screen_height * 0.08)))
        button_font_size = max(14, min(24, int(screen_width * 0.012)))
        
        submit_button = self.create_button(
            "START SESSION",
            command=self.submit_participant_id,
            font_size=button_font_size,
            width=button_width,
            height=button_height,
            bg_color='#4CAF50',  # More prominent green
            fg_color='white'
        )
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(submit_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.layout.addStretch(2)
        
        # Set focus to entry
        self.participant_id_entry.setFocus()
        
        # Log screen display
        self.log_action("PARTICIPANT_ID_SCREEN_DISPLAYED", "Participant ID entry screen shown")
    
    def log_text_change(self, text):
        """Log participant ID text changes."""
        if text.strip():  # Only log non-empty text
            self.log_action("PARTICIPANT_ID_TEXT_CHANGE", f"Text entered: {text}")
    
    def submit_participant_id(self):
        """Handle participant ID submission."""
        try:
            participant_id = self.participant_id_entry.text().strip()
            if participant_id:
                print(f"🔍 Processing participant ID: {participant_id}")
                print(f"🔍 Current app: {self.app}")
                print(f"🔍 App webpage_screen: {getattr(self.app, 'webpage_screen', 'NOT FOUND')}")
                
                # Set participant ID in app
                self.app.set_participant_id(participant_id)
                self.log_action("PARTICIPANT_ID_SUBMITTED", f"Participant ID: {participant_id}")
                
                # Navigate to next screen based on configuration
                try:
                    from config import CONSENT_ENABLED
                    print(f"🔍 CONSENT_ENABLED: {CONSENT_ENABLED}")
                    if CONSENT_ENABLED:
                        print("🔍 Navigating to webpage screen")
                        
                        # Debug print available screens
                        if hasattr(self.app, 'screens'):
                            print(f"🔍 Available screens: {list(self.app.screens.keys())}")
                        
                        # Use the MolyApp's proper navigation - switch to prestudy survey
                        if hasattr(self.app, 'prestudy_screen'):
                            print("🔍 Using app.prestudy_screen")
                            self.app.switch_to_screen(self.app.prestudy_screen)
                        elif hasattr(self.app, 'switch_to_prestudy_survey'):
                            print("🔍 Using switch_to_prestudy_survey method")
                            self.app.switch_to_prestudy_survey()
                        else:
                            print("⚠️ No prestudy survey available - this should not happen")
                            raise RuntimeError("Prestudy survey screen not available")
                    else:
                        print("🔍 Consent disabled, switching to relaxation")
                        if hasattr(self.app, 'relaxation_screen'):
                            self.app.switch_to_screen(self.app.relaxation_screen)
                        else:
                            # Fallback to direct method call
                            self.app.switch_to_relaxation()
                except ImportError as e:
                    print(f"🔍 ImportError: {e}")
                    # Config not available, use prestudy survey as default
                    if hasattr(self.app, 'switch_to_prestudy_survey'):
                        self.app.switch_to_prestudy_survey()
                    else:
                        raise RuntimeError("Prestudy survey not available and no fallback")
                except Exception as e:
                    print(f"⚠️ Error during screen transition: {e}")
                    import traceback
                    print(f"⚠️ Full traceback: {traceback.format_exc()}")
            else:
                self.show_error("⚠️ Please enter a valid participant ID")
        except Exception as e:
            print(f"⚠️ Critical error in submit_participant_id: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            self.show_error("⚠️ An error occurred. Please try again.")
    
    def show_error(self, message):
        """Show an error message temporarily."""
        try:
            from config import COLORS
            warning_color = COLORS.get('warning', '#ff6666')
        except (ImportError, AttributeError):
            warning_color = '#ff6666'
            
        error_label = self.create_instruction(
            message,
            font_size=16,
            color=warning_color
        )
        self.layout.addWidget(error_label)
        
        # Remove error message after 3 seconds
        timer = QTimer()
        timer.timeout.connect(lambda: self.layout.removeWidget(error_label) or error_label.deleteLater())
        timer.setSingleShot(True)
        timer.start(3000)