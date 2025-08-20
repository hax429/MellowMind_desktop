#!/usr/bin/env python3

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QKeySequence, QShortcut
from abc import ABC, ABCMeta, abstractmethod


class CombinedMeta(type(QWidget), ABCMeta):
    """Combined metaclass for QWidget and ABC."""
    pass


class BaseScreen(QWidget, ABC, metaclass=CombinedMeta):
    """
    Base class for all MellowMind screen implementations.
    Provides common functionality and interface for all screens.
    """
    
    def __init__(self, app_instance, logging_manager=None):
        """
        Initialize base screen.
        
        Args:
            app_instance: Reference to the main MolyApp instance
            logging_manager: Optional logging manager for screen events
        """
        super().__init__()
        self.app = app_instance
        self.logging_manager = logging_manager
        self.screen_name = self.__class__.__name__.lower().replace('screen', '')
        
        # Common screen properties
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.widgets = []
        self.is_active = False
        
        # Set default styling
        self.setStyleSheet("background-color: black; color: white;")
        
    @abstractmethod
    def setup_screen(self):
        """Setup the screen UI. Must be implemented by subclasses."""
        pass
    
    def show(self):
        """Setup this screen if not already done. Note: Don't call QWidget.show()."""
        try:
            print(f"🖥️ Setting up {self.screen_name} screen")
            
            # Setup this screen if not already done
            print(f"🔍 Checking if setup is done: {hasattr(self, '_screen_setup_done')}")
            if not hasattr(self, '_screen_setup_done'):
                print(f"🔍 Setting up {self.screen_name} screen...")
                self.setup_screen()
                self._screen_setup_done = True
                print(f"🔍 Setup completed for {self.screen_name} screen")
            else:
                print(f"🔍 {self.screen_name} screen already set up")
            
            # Don't call super().show() - let main app handle visibility
            # The stacked widget will handle showing the widget
            
            # Log screen display
            if self.logging_manager:
                self.logging_manager.log_action("SCREEN_DISPLAYED", f"{self.screen_name} screen displayed", self.screen_name)
            
            self.is_active = True
            print(f"✅ {self.screen_name} screen setup completed (visibility handled by main app)")
            
        except Exception as e:
            print(f"⚠️ Error showing {self.screen_name} screen: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
            if self.logging_manager:
                self.logging_manager.log_action("SCREEN_ERROR", f"Error displaying {self.screen_name}: {e}", self.screen_name)
    
    def hide(self):
        """Hide this screen and clean up resources."""
        try:
            print(f"🔒 Hiding {self.screen_name} screen")
            self.is_active = False
            
            # Hide this widget
            super().hide()
            
            # Cleanup widgets
            for widget in self.widgets:
                try:
                    widget.deleteLater()
                except:
                    pass
            self.widgets.clear()
            
            # Cleanup shortcuts
            if hasattr(self, 'shortcuts'):
                for shortcut in self.shortcuts:
                    try:
                        shortcut.setEnabled(False)
                        shortcut.deleteLater()
                    except:
                        pass
                self.shortcuts.clear()
            
        except Exception as e:
            print(f"⚠️ Error hiding {self.screen_name} screen: {e}")
    
    def _apply_focus_mode(self):
        """Apply focus mode settings if enabled."""
        try:
            from config import FOCUS_MODE
            if FOCUS_MODE and self.app.main_window:
                self.app.main_window.activateWindow()
                self.app.main_window.raise_()
        except ImportError:
            pass  # Config not available
    
    def add_widget(self, widget):
        """Add a widget to be tracked for cleanup."""
        if widget:
            self.widgets.append(widget)
        return widget
    
    def create_title(self, text, font_size=32, color='white', bg_color=None):
        """Create a standard title label."""
        title = QLabel(text)
        font = QFont('Arial', font_size)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {color}; background-color: transparent;")
        return self.add_widget(title)
    
    def create_instruction(self, text, font_size=18, color='white', bg_color=None, wraplength=800):
        """Create a standard instruction label."""
        instruction = QLabel(text)
        font = QFont('Arial', font_size)
        instruction.setFont(font)
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setWordWrap(True)
        instruction.setStyleSheet(f"color: {color}; background-color: transparent;")
        return self.add_widget(instruction)
    
    def create_button(self, text, command, font_size=16, width=150, height=50, bg_color='lightgreen', fg_color='black'):
        """Create a standard button."""
        button = QPushButton(text)
        font = QFont('Arial', font_size)
        font.setBold(True)
        button.setFont(font)
        button.setFixedSize(width, height)
        button.setStyleSheet(f"background-color: {bg_color}; color: {fg_color}; border: 2px solid gray; border-radius: 5px;")
        button.clicked.connect(command)
        return self.add_widget(button)
    
    def bind_key(self, key_sequence, callback):
        """Bind a key sequence to a callback using QShortcut."""
        try:
            # Convert tkinter key format to PyQt6 QKeySequence
            if key_sequence == '<Return>':
                qt_key = QKeySequence(Qt.Key.Key_Return)
            elif key_sequence == '<KeyPress-q>':
                qt_key = QKeySequence(Qt.Key.Key_Q)
            else:
                # Try to parse other key sequences
                qt_key = QKeySequence(key_sequence.replace('<', '').replace('>', ''))
            
            # Create QShortcut for key binding
            shortcut = QShortcut(qt_key, self)
            shortcut.activated.connect(callback)
            
            # Store shortcut reference for cleanup
            if not hasattr(self, 'shortcuts'):
                self.shortcuts = []
            self.shortcuts.append(shortcut)
            
        except Exception as e:
            print(f"⚠️ Error binding key {key_sequence}: {e}")
            # Fallback - store in main app shortcuts if available
            if hasattr(self.app, 'shortcuts'):
                try:
                    shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self.app)
                    shortcut.activated.connect(callback)
                    self.app.shortcuts.append(shortcut)
                except:
                    pass
    
    def log_action(self, action_type, details):
        """Log an action for this screen."""
        if self.logging_manager:
            self.logging_manager.log_action(action_type, details, self.screen_name)
    
    def transition_to(self, target_screen_method, transition_message=None):
        """Transition to another screen with optional transition screen."""
        if transition_message and hasattr(self.app, 'show_transition_screen'):
            self.app.show_transition_screen(transition_message, target_screen_method)
        else:
            target_screen_method()
    
    def set_background_color(self, color):
        """Set the background color for this screen."""
        self.background_color = color
        self.setStyleSheet(f"background-color: {color}; color: white;")