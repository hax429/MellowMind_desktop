#!/usr/bin/env python3

import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView  # Import early for proper initialization
import threading
import time
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
from qualtrics_manager import QualtricsManager

# Import modular screens
from screens import (
    ParticipantIDScreen, WebpageScreen, ConsentScreen, 
    RelaxationScreen, DescriptiveTaskScreen, StroopScreen, MathTaskScreen, 
    ContentPerformanceScreen, PostStudyRestScreen
)


class MolyApp(QMainWindow):
    """
    Unified Moly relaxation application with modular screen architecture.
    Handles transitions between relaxation, descriptive tasks, and video screens.
    """
    
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        
        self.main_window = self
        self.setWindowTitle(APP_TITLE)
        self.setStyleSheet("background-color: black;")
        
        # Apply focus mode settings
        if FOCUS_MODE:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
            self.showFullScreen()
            self.activateWindow()
        
        # Get screen dimensions
        screen = self.app.primaryScreen()
        screen_geometry = screen.geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        
        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stacked_widget = QStackedWidget()
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        # Common properties
        self.current_screen_widget = None
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
        self.qualtrics_manager = QualtricsManager(self.logging_manager)
        
        # Configure managers
        self.video_manager.set_screen_dimensions(self.screen_width, self.screen_height)
        self.countdown_manager.set_current_screen_callback(lambda: self.current_screen)
        self.countdown_manager.set_timeout_callback(self.show_timeout_notification)
        self.countdown_manager.set_root_after_callback(self.timer_callback)
        self.countdown_manager.set_enabled(COUNTDOWN_ENABLED)
        self.qualtrics_manager.set_app_instance(self)
        
        # Descriptive task properties (for compatibility)
        self.current_prompt_index = 0
        self.prompts = DESCRIPTIVE_PROMPTS.copy()
        
        # Math task properties (for compatibility)
        self.current_number = MATH_STARTING_NUMBER
        self.math_history = []

        # Task start flags (for compatibility)
        self.descriptive_task_started = False
        self.stroop_task_started = False
        self.math_task_started = False
        
        # Text tracking for sentence logging (for compatibility)
        self.last_sentence_position = 0
        self._last_text_length = 0
        self._last_logged_length = 0
        
        # Create main container
        self.setup_main_ui()

        # Set up crash detection
        self.setup_crash_detection()

        # Check for incomplete sessions before showing participant ID screen
        self.check_and_handle_recovery()

    def initialize_screens(self):
        """Initialize all modular screens."""
        self.participant_id_screen = ParticipantIDScreen(self, self.logging_manager)
        self.prestudy_screen = WebpageScreen(self, self.logging_manager, 'prestudy')  # Default survey screen
        self.poststudy_screen = WebpageScreen(self, self.logging_manager, 'poststudy')
        self.consent_screen = ConsentScreen(self, self.logging_manager)
        self.relaxation_screen = RelaxationScreen(self, self.logging_manager)
        self.descriptive_task_screen = DescriptiveTaskScreen(self, self.logging_manager)
        self.stroop_screen = StroopScreen(self, self.logging_manager)
        self.math_screen = MathTaskScreen(self, self.logging_manager)
        self.content_performance_screen = ContentPerformanceScreen(self, self.logging_manager)
        self.post_study_rest_screen = PostStudyRestScreen(self, self.logging_manager)
        
        # Store all screens for easy access
        self.screens = {
            'participant_id': self.participant_id_screen,
            'prestudy': self.prestudy_screen,
            'poststudy': self.poststudy_screen,
            'consent': self.consent_screen,
            'relaxation': self.relaxation_screen,
            'descriptive_task': self.descriptive_task_screen,
            'stroop': self.stroop_screen,
            'math_task': self.math_screen,
            'content_performance': self.content_performance_screen,
            'post_study_rest': self.post_study_rest_screen
        }

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
                # TODO: Implement PyQt recovery dialog
                print("⚠️ Recovery dialog needs PyQt conversion - skipping to participant ID screen")
                self.show_participant_id_screen()
            else:
                self.show_participant_id_screen()
        except Exception as e:
            print(f"⚠️ Error during recovery check: {e}")
            self.show_participant_id_screen()
        
    def setup_main_ui(self):
        """Setup the main UI container."""
        # Main frame is now handled by the stacked widget
        pass
    
    def timer_callback(self, delay, callback):
        """PyQt6 timer callback replacement for tkinter's after method."""
        QTimer.singleShot(delay, callback)
        
    def clear_screen(self):
        """Clear current screen content."""
        # Stop countdown timer first
        self.countdown_manager.stop_countdown()
        
        # Stop video if running
        self.video_manager.stop_video()
        
        # Clean up corner countdown if it exists
        if hasattr(self, 'corner_countdown_label'):
            try:
                self.corner_countdown_label.deleteLater()
                del self.corner_countdown_label
            except AttributeError:
                pass
            # Clear the reference in countdown manager
            self.countdown_manager.set_corner_countdown_label(None)
        
        # Hide current screen widget if it exists
        if self.current_screen_widget:
            try:
                self.current_screen_widget.hide()
                self.stacked_widget.removeWidget(self.current_screen_widget)
            except:
                pass
        
        # Clear all key shortcuts (PyQt6 equivalent)
        if hasattr(self, 'shortcuts'):
            for shortcut in self.shortcuts:
                shortcut.setEnabled(False)
            self.shortcuts.clear()
        else:
            self.shortcuts = []
    
    # =================== SCREEN NAVIGATION METHODS ===================
    
    def show_participant_id_screen(self):
        """Show participant ID entry screen using modular screen."""
        print("🆔 Showing Participant ID Entry Screen")
        # Initialize screens if not already done
        if not hasattr(self, 'participant_id_screen'):
            self.initialize_screens()
        self.switch_to_screen(self.participant_id_screen)
    
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
    
    def switch_to_prestudy_survey(self):
        """Show prestudy survey screen - this is now the default initial survey."""
        print("📋 Switching to Prestudy Survey Screen")
        self.switch_to_screen(self.prestudy_screen)
    
    def switch_to_poststudy_survey(self):
        """Show poststudy survey screen."""
        print("📊 Switching to Poststudy Survey Screen")
        self.switch_to_screen(self.poststudy_screen)
    
    def switch_to_consent(self):
        """Show consent screen using modular screen."""
        print("📋 Switching to Consent Screen")
        self.switch_to_screen(self.consent_screen)
    
    def switch_to_relaxation(self):
        """Show relaxation screen using modular screen."""
        print("🧘 Switching to Relaxation Screen")
        self.switch_to_screen(self.relaxation_screen)
    
    def switch_to_descriptive_task(self):
        """Show descriptive task screen using modular screen."""
        print("🎯 Switching to Descriptive Task Screen")
        self.switch_to_screen(self.descriptive_task_screen)
    
    # =================== SURVEY INTEGRATION METHODS ===================
    
    def open_pre_study_survey(self):
        """Open pre-study Qualtrics survey."""
        self.qualtrics_manager.open_survey(
            PRE_STUDY_SURVEY_URL, 
            "Pre-Study Survey", 
            callback=self.switch_to_consent
        )
    
    def open_mid_study_survey(self):
        """Open mid-study Qualtrics survey (e.g., after descriptive task)."""
        self.qualtrics_manager.open_survey(
            MID_STUDY_SURVEY_URL, 
            "Mid-Study Survey", 
            callback=self.switch_to_stroop
        )
    
    def open_post_study_survey(self):
        """Open post-study Qualtrics survey (e.g., after all tasks)."""
        self.qualtrics_manager.open_survey(
            POST_STUDY_SURVEY_URL, 
            "Post-Study Survey", 
            callback=self.switch_to_post_study_rest
        )
    
    # =================== LEGACY COMPATIBILITY METHODS ===================
    
    # These methods provide compatibility with existing functionality that 
    # hasn't been fully modularized yet
    
    def show_recovery_dialog(self, recovery_data):
        """Show recovery dialog using PyQt6 modular screens."""
        print("🔄 Recovery handling now uses PyQt6 modular screens")
        # Recovery is handled by RecoveryManager and PyQt screens
        self.show_participant_id_screen()

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
        
        # Update the modular screen's state
        if hasattr(self.descriptive_task_screen, 'current_prompt_index'):
            self.descriptive_task_screen.current_prompt_index = self.current_prompt_index
        
        # Go directly to descriptive task
        self.switch_to_descriptive_task()

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
        self.switch_to_descriptive_task()

    def show_recovery_notification(self, message):
        """Recovery notifications now handled by recovery manager and logging."""
        print(f"🔄 Notification: {message}")
        self.logging_manager.log_action("RECOVERY_NOTIFICATION", message, self.current_screen)

    def start_new_session(self):
        """Start a new session (normal flow)."""
        print("🆕 Starting new session")
        self.show_participant_id_screen()
    
    # Placeholder methods for screens not yet modularized
    def switch_to_stroop(self):
        """Switch to stroop screen."""
        print("🎬 Switching to Stroop Screen")
        self.switch_to_screen(self.stroop_screen)
    
    def switch_to_math_task(self):
        """Switch to math task screen."""
        print("🧮 Switching to Math Task Screen")
        self.switch_to_screen(self.math_screen)
    
    def switch_to_content_performance(self):
        """Switch to content performance screen."""
        print("📱 Switching to Content Performance Screen")
        self.switch_to_screen(self.content_performance_screen)
    
    def switch_to_post_study_rest(self):
        """Switch to post-study rest screen."""
        print("🧘 Switching to Post-Study Rest Screen")
        self.switch_to_screen(self.post_study_rest_screen)
    
    def show_timeout_notification(self, screen_name):
        """Show timeout notification and handle automatic transitions."""
        print(f"⏰ TIME'S UP for {screen_name} screen!")
        # TODO: Implement timeout handling
    
    def show_transition_screen(self, message, callback, bg_color=None):
        """Show transition screen using PyQt6 (simplified - direct transition for now)."""
        print(f"🚨 TRANSITION: {message}")
        self.logging_manager.log_action("TRANSITION_SCREEN_DISPLAYED", f"Transition: {message[:50]}...", self.current_screen)
        callback()
    
    # =================== APPLICATION LIFECYCLE ===================
    
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
            self.app.quit()
        except Exception as e:
            print(f"Warning: Error quitting application: {e}")
    
    def run(self):
        """Run the application."""
        try:
            print("🚀 Starting Moly Relaxation Application")
            print("📖 Current screen: Participant ID")
            
            # Initialize screens after QApplication is ready
            self.initialize_screens()
            
            # Show participant ID screen initially
            if hasattr(self, 'participant_id_screen'):
                self.switch_to_screen(self.participant_id_screen)
            
            # Start PyQt application
            self.show()
            self.raise_()  # Bring window to front
            self.activateWindow()  # Make sure it's the active window
            sys.exit(self.app.exec())
        except KeyboardInterrupt:
            print("\n🔌 Keyboard interrupt - Shutting down...")
            self.quit_app()
        finally:
            self.cleanup_resources()
    
    def switch_to_screen(self, screen_widget):
        """Switch to a specific screen widget."""        
        try:
            print(f"🔍 switch_to_screen called with: {screen_widget}")
            self.current_screen = getattr(screen_widget, 'screen_name', 'unknown')
            print(f"🔍 Current screen set to: {self.current_screen}")
            
            # Log screen transition
            self.logging_manager.log_action("SCREEN_TRANSITION", f"Switching to {self.current_screen} screen", self.current_screen)
            
            self.current_screen_widget = screen_widget
            
            # Important: Don't call screen_widget.show() directly!
            # We'll only use the QStackedWidget for display
            
            # Add widget to stack if not already there
            if self.stacked_widget.indexOf(screen_widget) == -1:
                print("🔍 Adding screen widget to stack")
                self.stacked_widget.addWidget(screen_widget)
            else:
                print("🔍 Screen widget already in stack")
            
            # Ensure screen is set up (calls setup_screen if needed)
            if not hasattr(screen_widget, '_screen_setup_done'):
                print(f"🔍 Setting up {self.current_screen} screen...")
                screen_widget.show()  # This will trigger setup if needed
                
            # Switch to the screen
            print("🔍 Setting current widget")
            self.stacked_widget.setCurrentWidget(screen_widget)
            print(f"🔍 Current widget index: {self.stacked_widget.currentIndex()}")
            print(f"🔍 Widget count in stack: {self.stacked_widget.count()}")
            
            # Ensure widget is shown and focused
            screen_widget.setEnabled(True)
            if hasattr(screen_widget, 'setFocus'):
                screen_widget.setFocus()
            
            print(f"🔍 Screen switch completed successfully to: {self.current_screen}")
            
            # Force window update
            self.update()
            self.repaint()
        except Exception as e:
            print(f"⚠️ Error in switch_to_screen: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            raise


def main():
    """Main entry point."""
    # Set attribute before any Qt objects are created (required for QWebEngineView)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    # Create QApplication first
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("🧘 Moly - Relaxation Experience (Modular Version)")
    print("=" * 50)
    
    moly_app = MolyApp()
    moly_app.run()
    
    print("👋 Thanks for using Moly!")


if __name__ == '__main__':
    main()