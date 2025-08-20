#!/usr/bin/env python3

"""
Unified Countdown Widget for MellowMind Desktop Application
Provides consistent countdown functionality across all task screens.
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CountdownWidget:
    """
    A unified countdown widget that provides consistent countdown functionality
    across all task screens (Descriptive, Stroop, Math).
    """
    
    def __init__(self, parent_screen, countdown_minutes, show_main_display=True, show_corner_display=True):
        """
        Initialize the countdown widget.
        
        Args:
            parent_screen: The parent screen instance
            countdown_minutes: Duration in minutes
            show_main_display: Whether to show the main countdown display
            show_corner_display: Whether to show the corner countdown display
        """
        self.parent_screen = parent_screen
        self.countdown_minutes = countdown_minutes
        self.show_main_display = show_main_display
        self.show_corner_display = show_corner_display
        
        # Initialize countdown displays
        self.countdown_label = None
        self.corner_countdown_label = None
        self.hurry_label = None
        
        # Setup countdown displays
        if self.show_main_display:
            self.setup_main_countdown()
        elif self.show_corner_display:
            # If only showing corner display, still create HURRY label
            self.setup_hurry_label()
        if self.show_corner_display:
            self.setup_corner_countdown()
    
    def setup_main_countdown(self):
        """Setup the main countdown display."""
        # Get screen dimensions for responsive scaling
        screen_width = self.parent_screen.app.screen_width if hasattr(self.parent_screen.app, 'screen_width') else 1920
        countdown_font_size = max(20, min(36, int(screen_width * 0.018)))
        
        # Create main countdown display - emphasized
        self.countdown_label = QLabel(f"⏰ You have {self.countdown_minutes} minutes for this task")
        self.countdown_label.setFont(QFont('Arial', countdown_font_size, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet(f"""
            color: {self.parent_screen.colors['countdown_normal']}; 
            background-color: rgba(0, 0, 0, 150); 
            padding: 15px; 
            border-radius: 10px;
            font-size: {countdown_font_size}px;
            border: 2px solid {self.parent_screen.colors['countdown_normal']};
        """)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to parent layout and widget tracking
        self.parent_screen.layout.addWidget(self.countdown_label)
        self.parent_screen.layout.addStretch(1)
        self.parent_screen.add_widget(self.countdown_label)
        
        # Create HURRY label (initially hidden)
        self.hurry_label = QLabel()
        hurry_font_size = max(18, min(32, int(screen_width * 0.016)))
        self.hurry_label.setFont(QFont('Arial', hurry_font_size, QFont.Weight.Bold))
        self.hurry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hurry_label.hide()  # Initially hidden
        
        # Add to parent layout and widget tracking
        self.parent_screen.layout.addWidget(self.hurry_label)
        self.parent_screen.layout.addStretch(1)
        self.parent_screen.add_widget(self.hurry_label)
    
    def setup_hurry_label(self):
        """Setup the HURRY label for corner-only countdown displays."""
        # Get screen dimensions for responsive scaling
        screen_width = self.parent_screen.app.screen_width if hasattr(self.parent_screen.app, 'screen_width') else 1920
        hurry_font_size = max(18, min(32, int(screen_width * 0.016)))
        
        # Create HURRY label (initially hidden)
        self.hurry_label = QLabel()
        self.hurry_label.setFont(QFont('Arial', hurry_font_size, QFont.Weight.Bold))
        self.hurry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hurry_label.hide()  # Initially hidden
        
        # Add to parent layout and widget tracking
        self.parent_screen.layout.addWidget(self.hurry_label)
        self.parent_screen.layout.addStretch(1)
        self.parent_screen.add_widget(self.hurry_label)
    
    def setup_corner_countdown(self):
        """Setup the corner countdown display."""
        # Get screen dimensions for responsive scaling
        screen_width = self.parent_screen.app.screen_width if hasattr(self.parent_screen.app, 'screen_width') else 1920
        corner_countdown_font_size = max(60, min(120, int(screen_width * 0.06)))
        
        # Create corner countdown timer (top-right) - responsive and emphasized
        self.corner_countdown_label = QLabel(self.parent_screen)
        self.corner_countdown_label.setText("0:00")
        self.corner_countdown_label.setFont(QFont('Arial', corner_countdown_font_size, QFont.Weight.Bold))
        
        # Start with normal color (will be updated based on time remaining)
        try:
            from config import COLORS
            initial_color = COLORS.get('countdown_normal', '#00FF00')
        except ImportError:
            initial_color = self.parent_screen.colors.get('countdown_normal', '#00FF00')
        self.corner_countdown_label.setStyleSheet(f"""
            QLabel {{
                color: {initial_color};
                background-color: rgba(0, 0, 0, 200);
                border: 4px solid {initial_color};
                padding: 20px;
                border-radius: 15px;
                font-size: {corner_countdown_font_size}px;
            }}
        """)
        self.corner_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to parent widget tracking
        self.parent_screen.add_widget(self.corner_countdown_label)
    
    def position_corner_countdown(self):
        """Position the corner countdown timer after the screen is shown with improved auto-sizing."""
        if self.corner_countdown_label:
            # Get actual parent dimensions with fallback - use app window dimensions
            if hasattr(self.parent_screen, 'app') and hasattr(self.parent_screen.app, 'geometry'):
                app_geometry = self.parent_screen.app.geometry()
                parent_width = app_geometry.width()
                parent_height = app_geometry.height()
            else:
                parent_width = getattr(self.parent_screen.app, 'screen_width', 1920)
                parent_height = getattr(self.parent_screen.app, 'screen_height', 1080)
            
            print(f"🎯 DEBUG: Positioning corner countdown - parent_width:{parent_width}, parent_height:{parent_height}")
            
            # Calculate responsive dimensions based on screen size - increased for better visibility
            width = min(320, int(parent_width * 0.18))  # Increased max width and percentage
            height = min(140, int(parent_height * 0.10))  # Increased max height and percentage
            
            # Ensure minimum readable size for numbers
            width = max(width, 250)  # Increased minimum width
            height = max(height, 100)  # Increased minimum height
            
            # Position with margin from edges to ensure full visibility
            margin = 15
            x_pos = parent_width - width - margin
            y_pos = margin
            
            # Ensure the countdown doesn't go off-screen (safety check)
            if x_pos < 0:
                x_pos = parent_width - width - 5  # Minimal margin if space is very tight
            if x_pos + width > parent_width:
                x_pos = parent_width - width - 5
            
            print(f"🎯 DEBUG: Setting corner countdown geometry to: x:{x_pos}, y:{y_pos}, w:{width}, h:{height}")
            self.corner_countdown_label.setGeometry(x_pos, y_pos, width, height)
            self.corner_countdown_label.show()
            self.corner_countdown_label.raise_()
            
            # Force the label to be visible and on top
            self.corner_countdown_label.setVisible(True)
            self.corner_countdown_label.activateWindow()
            print(f"🎯 DEBUG: Corner countdown positioned and shown with improved auto-sizing")
    
    def start_countdown(self, auto_transition_callback, update_callback=None):
        """Start the countdown timer with the countdown manager."""
        if self.parent_screen.countdown_enabled:
            print(f"🎯 DEBUG: Setting up countdown labels for {self.parent_screen.screen_name}...")
            
            # Set up countdown manager with our labels
            if self.countdown_label:
                print(f"🎯 DEBUG: Main countdown label exists: {self.countdown_label is not None}")
                print(f"🎯 DEBUG: Main label text: {self.countdown_label.text() if self.countdown_label else 'None'}")
                self.parent_screen.app.countdown_manager.setup_countdown_label(self.countdown_label)
            
            if self.corner_countdown_label:
                print(f"🎯 DEBUG: Corner countdown label exists: {self.corner_countdown_label is not None}")
                print(f"🎯 DEBUG: Corner label text: {self.corner_countdown_label.text() if self.corner_countdown_label else 'None'}")
                self.parent_screen.app.countdown_manager.set_corner_countdown_label(self.corner_countdown_label)
                # Position corner countdown
                self.position_corner_countdown()
            
            # Set callbacks
            self.parent_screen.app.countdown_manager.set_countdown_finish_callback(auto_transition_callback)
            
            # Use unified countdown update callback that handles the HURRY label
            unified_callback = self.create_unified_update_callback(update_callback)
            self.parent_screen.app.countdown_manager.set_countdown_update_callback(unified_callback)
            
            # Start the countdown
            print(f"🎯 DEBUG: Starting countdown with {self.countdown_minutes} minutes...")
            print(f"🎯 DEBUG: Using screen name: {self.parent_screen.screen_name}")
            self.parent_screen.app.countdown_manager.start_countdown(self.countdown_minutes, self.parent_screen.screen_name)
    
    def create_unified_update_callback(self, additional_callback=None):
        """Create a unified countdown update callback that handles combined countdown display and colors."""
        def unified_callback(remaining_seconds):
            total_seconds = self.countdown_minutes * 60
            percentage_remaining = (remaining_seconds / total_seconds) * 100
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            # Update main countdown label with combined information (if exists)
            if hasattr(self, 'countdown_label') and self.countdown_label:
                if percentage_remaining > 50:
                    message = f"⏰ You have {minutes}:{seconds:02d} left!"
                    text_color = "white"
                    bg_color = "rgba(0, 0, 0, 150)"
                    border_color = self.parent_screen.colors.get('countdown_normal', '#00FF00')
                elif percentage_remaining > 25:
                    message = f"⚠️ HURRY! Only {minutes}:{seconds:02d} left!"
                    text_color = "black"  # Black text for better contrast on yellow/orange
                    bg_color = "rgba(255, 165, 0, 180)"
                    border_color = self.parent_screen.colors.get('countdown_warning', '#FFFF00')
                elif percentage_remaining > 10:
                    message = f"🚨 CRITICAL! Only {seconds} seconds left!"
                    text_color = "white"  # White text for contrast on red background
                    bg_color = "rgba(255, 0, 0, 180)"
                    border_color = self.parent_screen.colors.get('countdown_critical', '#FF0000')
                else:
                    message = f"⏰ TIME RUNNING OUT! {seconds}s!"
                    text_color = "white"  # White text for contrast on red background
                    bg_color = "rgba(255, 0, 0, 220)"
                    border_color = self.parent_screen.colors.get('countdown_critical', '#FF0000')
                
                self.countdown_label.setText(message)
                self.countdown_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        background-color: {bg_color};
                        padding: 15px;
                        border-radius: 10px;
                        border: 2px solid {border_color};
                        font-weight: bold;
                        margin: 5px;
                    }}
                """)
            
            # Update HURRY label for corner-only displays (when main display is not shown)
            if hasattr(self, 'hurry_label') and self.hurry_label and not self.show_main_display:
                if percentage_remaining <= 50:  # Show when 50% or less time remaining
                    if percentage_remaining > 25:  # 25-50% remaining
                        message = f"⚠️ HURRY! Only {minutes}:{seconds:02d} left!"
                        text_color = "black"  # Black text for better contrast
                        bg_color = "rgba(255, 165, 0, 180)"
                        border_color = self.parent_screen.colors.get('countdown_warning', '#FFFF00')
                    elif percentage_remaining > 10:  # 10-25% remaining
                        message = f"🚨 CRITICAL! Only {seconds} seconds left!"
                        text_color = "white"  # White text for contrast
                        bg_color = "rgba(255, 0, 0, 180)"
                        border_color = self.parent_screen.colors.get('countdown_critical', '#FF0000')
                    else:  # Less than 10% remaining
                        message = f"⏰ TIME RUNNING OUT! {seconds}s!"
                        text_color = "white"  # White text for contrast
                        bg_color = "rgba(255, 0, 0, 220)"
                        border_color = self.parent_screen.colors.get('countdown_critical', '#FF0000')
                    
                    self.hurry_label.setText(message)
                    self.hurry_label.setStyleSheet(f"""
                        QLabel {{
                            color: {text_color};
                            background-color: {bg_color};
                            padding: 12px 20px;
                            border-radius: 8px;
                            border: 2px solid {border_color};
                            font-weight: bold;
                            margin: 5px;
                        }}
                    """)
                    self.hurry_label.show()
                    
                    # Position HURRY label in center of screen for visibility
                    parent_width = self.parent_screen.width() if self.parent_screen.width() > 0 else self.parent_screen.app.screen_width
                    parent_height = self.parent_screen.height() if self.parent_screen.height() > 0 else self.parent_screen.app.screen_height
                    
                    # Center the label on screen
                    label_width = 600
                    label_height = 80
                    x_pos = (parent_width - label_width) // 2
                    y_pos = parent_height // 3  # Upper third of screen
                    
                    # Set geometry if the label supports it
                    try:
                        self.hurry_label.setGeometry(x_pos, y_pos, label_width, label_height)
                        self.hurry_label.raise_()
                    except:
                        pass  # Fallback to normal layout positioning
                else:
                    self.hurry_label.hide()
            
            # Update corner countdown colors and ensure proper contrast based on percentage
            if hasattr(self, 'corner_countdown_label') and self.corner_countdown_label:
                if percentage_remaining > 50:
                    border_color = self.parent_screen.colors.get('countdown_normal', '#00FF00')
                    text_color = "white"
                    bg_color = "rgba(0, 0, 0, 200)"
                elif percentage_remaining > 25:
                    border_color = self.parent_screen.colors.get('countdown_warning', '#FFFF00')
                    text_color = "black"  # Black text for better contrast on yellow
                    bg_color = "rgba(255, 255, 0, 100)"  # Light yellow background
                else:
                    border_color = self.parent_screen.colors.get('countdown_critical', '#FF0000')
                    text_color = "white"  # White text for contrast on red
                    bg_color = "rgba(255, 0, 0, 150)"  # Red background
                
                self.corner_countdown_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        background-color: {bg_color};
                        border: 4px solid {border_color};
                        padding: 20px;
                        border-radius: 15px;
                        font-weight: bold;
                    }}
                """)
            
            # Call additional callback if provided (for task-specific updates)
            if additional_callback:
                additional_callback(remaining_seconds)
        
        return unified_callback
    
    def stop_countdown(self):
        """Stop the countdown timer."""
        try:
            if hasattr(self.parent_screen, 'app') and hasattr(self.parent_screen.app, 'countdown_manager'):
                self.parent_screen.app.countdown_manager.stop_countdown()
                print(f"🎯 DEBUG: Countdown stopped via unified widget")
            else:
                print(f"🎯 DEBUG: No countdown manager available to stop")
        except Exception as e:
            print(f"⚠️ Error stopping countdown via unified widget: {e}")