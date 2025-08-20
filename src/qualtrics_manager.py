#!/usr/bin/env python3

import subprocess
import platform
import webbrowser


class QualtricsManager:
    """
    Manages Qualtrics survey integration with MellowMind app.
    Handles pausing the app, opening surveys in external browser, and resuming.
    """
    
    def __init__(self, logging_manager=None):
        self.logging_manager = logging_manager
        self.app_instance = None
        self.survey_window = None
        self.original_focus_mode = False
        self.original_fullscreen = False
        self.original_topmost = False
        self.survey_complete = False
        
    def set_app_instance(self, app_instance):
        """Set reference to the main MolyApp instance."""
        self.app_instance = app_instance
        
    def open_survey(self, survey_url, survey_name="Qualtrics Survey", callback=None):
        """
        Open Qualtrics survey in external browser and pause the app.
        
        Args:
            survey_url (str): The Qualtrics survey URL
            survey_name (str): Name of the survey for logging
            callback (function): Function to call when survey is complete
        """
        if not self.app_instance:
            print("⚠️ No app instance set for QualtricsManager")
            return False
            
        try:
            print(f"📋 Opening Qualtrics survey: {survey_name}")
            if self.logging_manager:
                self.logging_manager.log_action("SURVEY_STARTED", f"Opening survey: {survey_name} - {survey_url}", "survey")
            
            # Pause the MellowMind app
            self.pause_app()
            
            # Open survey in browser
            success = self.open_browser_survey(survey_url)
            
            if success:
                # Show waiting screen
                self.show_survey_waiting_screen(survey_name, callback)
                return True
            else:
                # Resume app if browser opening failed
                self.resume_app()
                return False
                
        except Exception as e:
            print(f"⚠️ Error opening survey: {e}")
            if self.logging_manager:
                self.logging_manager.log_action("SURVEY_ERROR", f"Error opening survey: {e}", "survey")
            self.resume_app()
            return False
    
    def pause_app(self):
        """Pause the MellowMind app by disabling focus mode and fullscreen."""
        if not self.app_instance or not self.app_instance.root:
            return
            
        try:
            # Store original settings (import here to avoid circular import)
            from config import FOCUS_MODE
            self.original_focus_mode = FOCUS_MODE
            # Store original window attributes for PyQt6 compatibility
            self.original_fullscreen = getattr(self.app_instance, 'isFullScreen', lambda: False)()
            self.original_topmost = bool(getattr(self.app_instance, 'windowFlags', lambda: 0)() & 0x00000008)
            
            print("⏸️ Pausing MellowMind app for survey")
            if self.logging_manager:
                self.logging_manager.log_action("APP_PAUSED", "App paused for external survey", "survey")
            
            # Hide the application window for PyQt6/tkinter compatibility
            if hasattr(self.app_instance, 'hide'):
                # PyQt6 method
                if self.original_fullscreen and hasattr(self.app_instance, 'showNormal'):
                    self.app_instance.showNormal()
                self.app_instance.hide()
            elif hasattr(self.app_instance, 'root'):
                # tkinter compatibility
                self.app_instance.root.attributes('-fullscreen', False)
                self.app_instance.root.attributes('-topmost', False)
                self.app_instance.root.withdraw()
            
        except Exception as e:
            print(f"⚠️ Error pausing app: {e}")
    
    def resume_app(self):
        """Resume the MellowMind app by restoring focus mode and fullscreen."""
        if not self.app_instance:
            return
            
        try:
            print("▶️ Resuming MellowMind app after survey")
            if self.logging_manager:
                self.logging_manager.log_action("APP_RESUMED", "App resumed after external survey", "survey")
            
            # Show and restore window for PyQt6/tkinter compatibility
            if hasattr(self.app_instance, 'show'):
                # PyQt6 method
                self.app_instance.show()
                if self.original_fullscreen and hasattr(self.app_instance, 'showFullScreen'):
                    self.app_instance.showFullScreen()
                if hasattr(self.app_instance, 'activateWindow'):
                    self.app_instance.activateWindow()
                    self.app_instance.raise_()
            elif hasattr(self.app_instance, 'root'):
                # tkinter compatibility
                self.app_instance.root.deiconify()
                if self.original_fullscreen:
                    self.app_instance.root.attributes('-fullscreen', True)
                if self.original_topmost:
                    self.app_instance.root.attributes('-topmost', True)
                self.app_instance.root.focus_force()
                self.app_instance.root.lift()
            
        except Exception as e:
            print(f"⚠️ Error resuming app: {e}")
    
    def open_browser_survey(self, survey_url):
        """Open survey in external browser with platform-specific optimizations."""
        try:
            system = platform.system()
            
            # Try to open in Chrome/Chromium for better Qualtrics compatibility
            if system == "Darwin":  # macOS
                chrome_paths = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Chromium.app/Contents/MacOS/Chromium"
                ]
                for path in chrome_paths:
                    try:
                        subprocess.Popen([path, survey_url])
                        print(f"✅ Opened survey in Chrome: {path}")
                        return True
                    except (FileNotFoundError, OSError):
                        continue
                        
            elif system == "Windows":
                chrome_paths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                ]
                for path in chrome_paths:
                    try:
                        subprocess.Popen([path, survey_url])
                        print(f"✅ Opened survey in Chrome: {path}")
                        return True
                    except (FileNotFoundError, OSError):
                        continue
                        
            elif system == "Linux":
                chrome_commands = ["google-chrome", "chromium-browser", "chromium"]
                for cmd in chrome_commands:
                    try:
                        subprocess.Popen([cmd, survey_url])
                        print(f"✅ Opened survey in Chrome: {cmd}")
                        return True
                    except (FileNotFoundError, OSError):
                        continue
            
            # Fallback to default browser
            print("⚠️ Chrome not found, using default browser")
            webbrowser.open(survey_url)
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to open browser: {e}")
            return False
    
    def show_survey_waiting_screen(self, survey_name, callback=None):
        """Show a waiting screen while user completes the survey."""
        if not self.app_instance:
            return
            
        # Clear current screen
        self.app_instance.clear_screen()
        self.app_instance.current_screen = "survey_waiting"
        
        # For PyQt6 compatibility, we'll create a simple screen
        # This should be implemented as a proper PyQt6 widget in the future
        print("📋 Survey in Progress")
        print(f"Please complete the {survey_name} in your browser window.")
        print("The application will automatically continue when ready.")
        
        # For now, just show a simple completion option
        # This could be enhanced with a proper PyQt6 dialog in the future
        if callback:
            # Auto-continue after user indicates completion
            callback()
        
        print(f"✅ Survey waiting screen displayed for: {survey_name}")
    
    def complete_survey(self, callback=None):
        """Handle survey completion and resume normal app flow."""
        try:
            print("✅ User marked survey as complete")
            if self.logging_manager:
                self.logging_manager.log_action("SURVEY_COMPLETED", "User marked survey as complete", "survey")
            
            self.survey_complete = True
            
            # Resume the app
            self.resume_app()
            
            # Execute callback if provided
            if callback and callable(callback):
                callback()
            else:
                # Default: return to previous screen or continue flow
                print("📱 Survey complete, continuing with app flow...")
                
        except Exception as e:
            print(f"⚠️ Error completing survey: {e}")
            if self.logging_manager:
                self.logging_manager.log_action("SURVEY_COMPLETION_ERROR", f"Error completing survey: {e}", "survey")
    
    def is_survey_complete(self):
        """Check if current survey is complete."""
        return self.survey_complete
        
    def reset_survey_state(self):
        """Reset survey completion state for next survey."""
        self.survey_complete = False