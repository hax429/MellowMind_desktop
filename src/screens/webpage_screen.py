#!/usr/bin/env python3

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer
from .base_screen import BaseScreen


class WebpageScreen(BaseScreen):
    """General-purpose screen for displaying web content and surveys."""
    
    def __init__(self, app_instance, logging_manager=None, survey_type='google'):
        super().__init__(app_instance, logging_manager)
        self.web_view = None
        self.background_color = 'black'
        self.survey_type = survey_type
        
        # Load configuration
        self.load_survey_config()
    
    def load_survey_config(self):
        """Load survey configuration from config.py."""
        try:
            from config import SURVEY_URLS, SURVEY_CONFIGS, DEFAULT_SURVEY_CONFIG, DEVELOPER_MODE
            
            # Get URL for this survey type
            self.survey_url = SURVEY_URLS.get(self.survey_type, 'https://www.google.com')
            
            # Get configuration for this survey type
            self.config = SURVEY_CONFIGS.get(self.survey_type, DEFAULT_SURVEY_CONFIG.copy())
            
            # Apply default values for missing config keys
            for key, default_value in DEFAULT_SURVEY_CONFIG.items():
                if key not in self.config:
                    self.config[key] = default_value
            
            self.developer_mode = DEVELOPER_MODE
            
        except ImportError:
            # Fallback configuration if config.py not available
            self.survey_url = 'https://www.google.com'
            self.config = {
                'title': 'Web Survey',
                'button_text': 'CONTINUE',
                'callback': None,
                'height': 800
            }
            self.developer_mode = False
    
    def setup_screen(self):
        """Setup the webpage screen with configurable content and responsive layout."""
        try:
            print(f"🔍 Setting up webpage screen for survey type: {self.survey_type}")
            self.set_background_color(self.background_color)
            
            # Get screen dimensions for responsive scaling
            screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
            screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
            
            # Calculate responsive font sizes and dimensions
            title_font_size = max(20, min(36, int(screen_width * 0.020)))
            button_font_size = max(14, min(22, int(screen_width * 0.012)))
            web_frame_height = max(400, min(800, int(screen_height * 0.65)))
            
            # Add debug label only in developer mode
            if self.developer_mode:
                debug_label = self.create_instruction(
                    f"Debug: Setting up {self.survey_type} survey screen...",
                    font_size=14,
                    color='yellow'
                )
                self.layout.addWidget(debug_label)
            
            # Title (configurable) - emphasized and responsive
            title = self.create_title(
                self.config['title'],
                font_size=title_font_size,
                color=self.config.get('title_color', '#4285F4')
            )
            self.layout.addWidget(title)
            self.layout.addStretch(1)
            
            # Create web view frame - responsive sizing
            print(f"🔍 Creating web frame for {self.survey_type}...")
            web_frame = QFrame()
            web_frame.setFrameStyle(QFrame.Shape.Box)
            web_frame.setLineWidth(3)
            try:
                from config import COLORS, UI_SETTINGS
                accent_color = COLORS['webpage_accent']
                bg_color = COLORS['webpage_bg']
                border_radius = UI_SETTINGS['border_radius_medium']
            except ImportError:
                accent_color = '#4285F4'
                bg_color = 'white'
                border_radius = '8px'
            web_frame.setStyleSheet(f"QFrame {{ border: 3px solid {accent_color}; background-color: {bg_color}; border-radius: {border_radius}; }}")
            web_frame.setMinimumHeight(web_frame_height)
            web_frame.setMaximumHeight(int(screen_height * 0.75))
            
            # Create web view with error handling - responsive sizing
            print(f"🔍 Creating QWebEngineView for {self.survey_type}...")
            try:
                from PyQt6.QtWebEngineWidgets import QWebEngineView
                self.web_view = QWebEngineView()
                self.web_view.setStyleSheet("border: none;")
                min_width = max(300, int(screen_width * 0.5))
                min_height = max(250, int(screen_height * 0.4))
                self.web_view.setMinimumSize(min_width, min_height)
                print(f"🔍 QWebEngineView created successfully for {self.survey_type}")
                
                # Test if view is actually working
                self.web_view.show()
                
            except ImportError as e:
                print(f"⚠️ Import error for QWebEngineView: {e}")
                # Create fallback label instead
                from PyQt6.QtWidgets import QLabel
                self.web_view = QLabel(f"PyQt6 WebEngine not found: {e}")
                self.web_view.setStyleSheet("background-color: white; padding: 20px; border: none; color: black;")
                min_width = max(300, int(screen_width * 0.5))
                min_height = max(250, int(screen_height * 0.4))
                self.web_view.setMinimumSize(min_width, min_height)
            except Exception as e:
                print(f"⚠️ Error creating QWebEngineView: {e}")
                # Create fallback label instead
                from PyQt6.QtWidgets import QLabel
                self.web_view = QLabel(f"Error creating web view: {e}")
                self.web_view.setStyleSheet("background-color: white; padding: 20px; border: none; color: black;")
                min_width = max(300, int(screen_width * 0.5))
                min_height = max(250, int(screen_height * 0.4))
                self.web_view.setMinimumSize(min_width, min_height)
            
            # Layout for web frame
            web_layout = QVBoxLayout(web_frame)
            web_layout.setContentsMargins(8, 8, 8, 8)
            web_layout.addWidget(self.web_view)
            
            self.layout.addWidget(web_frame)
            self.layout.addStretch(1)
            
            # Add to widget tracking
            self.add_widget(self.web_view)
            self.add_widget(web_frame)
            
            # Continue button (configurable) - emphasized and responsive
            print(f"🔍 Creating continue button for {self.survey_type}...")
            button_width = max(200, min(400, int(screen_width * 0.18)))
            button_height = max(50, min(90, int(screen_height * 0.07)))
            
            continue_button = self.create_button(
                self.config['button_text'],
                command=self.continue_to_next,
                font_size=button_font_size,
                width=button_width,
                height=button_height,
                # Colors now come from config via base_screen.py
                fg_color='white'
            )
            
            # Center the button
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(continue_button)
            button_layout.addStretch()
            self.layout.addLayout(button_layout)
            self.layout.addStretch(1)
            
            # Load website
            print(f"🔍 Loading website for {self.survey_type}...")
            self.load_website()
            print(f"🔍 Webpage screen setup completed for {self.survey_type}")
            
            # Log screen display
            self.log_action(f"{self.survey_type.upper()}_SCREEN_DISPLAYED", f"{self.survey_type} survey screen displayed with URL: {self.survey_url}")
            
        except Exception as e:
            print(f"⚠️ Error in webpage screen setup: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            # Add error display to screen
            error_label = self.create_instruction(
                f"Error: {str(e)}",
                font_size=16,
                color='red'
            )
            self.layout.addWidget(error_label)
            raise
    
    def load_website(self):
        """Load the configured website."""
        try:
            print(f"🔍 Loading {self.survey_type} website: {self.survey_url}")
            
            # Check if web_view is QWebEngineView or fallback label
            if hasattr(self.web_view, 'load'):
                # Load actual website
                print(f"🔍 Loading actual website: {self.survey_url}")
                website_url = QUrl(self.survey_url)
                self.web_view.load(website_url)
                print(f"✅ Loading website: {self.survey_url}")
                
                # Handle load finished
                self.web_view.loadFinished.connect(self.on_page_loaded)
            else:
                print(f"🔍 Using fallback web view (QLabel) for {self.survey_type}")
                # Load fallback content if available
                if 'fallback_html' in self.config:
                    self.load_fallback_content()
                
        except Exception as e:
            print(f"⚠️ Error loading website: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            self.load_fallback_content()
    
    def load_fallback_content(self):
        """Load fallback HTML content if website fails to load."""
        if 'fallback_html' in self.config:
            print(f"🔍 Loading fallback content for {self.survey_type}")
            if hasattr(self.web_view, 'setHtml'):
                self.web_view.setHtml(self.config['fallback_html'])
            else:
                # If web_view is a QLabel, show simple message
                from PyQt6.QtWidgets import QLabel
                if isinstance(self.web_view, QLabel):
                    self.web_view.setText(f"Fallback content for {self.config['title']}")
        else:
            print(f"⚠️ No fallback content available for {self.survey_type}")
            # Create generic fallback
            fallback_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>{self.config['title']}</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px; background: white;">
                <h1>{self.config['title']}</h1>
                <p>Unable to load content. Please try again later.</p>
                <p>Survey URL: {self.survey_url}</p>
            </body>
            </html>
            """
            if hasattr(self.web_view, 'setHtml'):
                self.web_view.setHtml(fallback_html)
    
    def on_page_loaded(self, success):
        """Handle when the webpage finishes loading."""
        if success:
            print(f"✅ {self.survey_type} website loaded successfully")
            self.log_action(f"{self.survey_type.upper()}_PAGE_LOADED", f"{self.survey_type} website loaded successfully")
        else:
            print(f"⚠️ Failed to load {self.survey_type} website, using fallback")
            self.log_action(f"{self.survey_type.upper()}_PAGE_LOAD_FAILED", f"{self.survey_type} website failed to load, using fallback content")
            self.load_fallback_content()
    
    def continue_to_next(self):
        """Continue to the next screen based on configuration."""
        self.log_action(f"{self.survey_type.upper()}_CONTINUE", f"User clicked continue from {self.survey_type} survey")
        
        # Get callback from configuration
        callback_name = self.config.get('callback')
        if callback_name and hasattr(self.app, callback_name):
            callback_method = getattr(self.app, callback_name)
            callback_method()
        else:
            print(f"⚠️ No valid callback found for {self.survey_type}, using default transition")
            # Fallback to consent screen
            if hasattr(self.app, 'switch_to_consent'):
                self.app.switch_to_consent()
            else:
                print("⚠️ No fallback transition available")
    
    def set_survey_type(self, survey_type):
        """Change the survey type and reload configuration."""
        self.survey_type = survey_type
        self.load_survey_config()
        
        # If screen is already set up, reload it
        if hasattr(self, '_screen_setup_done'):
            delattr(self, '_screen_setup_done')
            # Clear existing widgets
            for widget in self.widgets:
                try:
                    widget.deleteLater()
                except:
                    pass
            self.widgets.clear()
            
            # Clear layout
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Setup screen again
            self.setup_screen()
    
    def configure_for_prestudy(self):
        """Configure this screen for prestudy survey."""
        self.set_survey_type('prestudy')
    
    def configure_for_poststudy(self):
        """Configure this screen for poststudy survey."""
        self.set_survey_type('poststudy')
    
    def configure_for_custom_survey(self, survey_type, title, url, button_text, callback=None):
        """Configure this screen for a custom survey type."""
        # Add custom configuration to the config temporarily
        try:
            from config import SURVEY_URLS, SURVEY_CONFIGS
            SURVEY_URLS[survey_type] = url
            SURVEY_CONFIGS[survey_type] = {
                'title': title,
                'button_text': button_text,
                'callback': callback,
                'height': 900
            }
        except ImportError:
            pass
        
        self.set_survey_type(survey_type)


# Factory function to create survey screens
def create_survey_screen(app_instance, logging_manager, survey_type):
    """Factory function to create a survey screen of a specific type."""
    return WebpageScreen(app_instance, logging_manager, survey_type)