#!/usr/bin/env python3

import time
from PyQt6.QtCore import QTimer


class CountdownManager:
    """Simple PyQt6-based countdown timer manager."""
    
    def __init__(self, logging_manager):
        self.logging_manager = logging_manager
        
        # Countdown state
        self.countdown_remaining = 0
        self.countdown_running = False
        self.countdown_enabled = True
        
        # Labels to update
        self.countdown_label = None
        self.corner_countdown_label = None
        
        # Timer
        self.timer = None
        
        # Callbacks
        self.get_current_screen = None
        self.timeout_callback = None
        self.countdown_finish_callback = None
        self.countdown_update_callback = None  # For custom countdown updates
        
        # Tracking
        self.start_time = 0
        self.initial_duration = 0
        self.screen_name = ""
    
    def set_current_screen_callback(self, callback):
        """Set callback to get current screen."""
        self.get_current_screen = callback
    
    def setup_countdown_label(self, label):
        """Set the main countdown label widget."""
        self.countdown_label = label
        print(f"🎯 DEBUG: Main countdown label set: {label is not None}, type: {type(label) if label else 'None'}")
    
    def set_corner_countdown_label(self, label):
        """Set the corner countdown label widget."""
        self.corner_countdown_label = label
        print(f"🎯 DEBUG: Corner countdown label set: {label is not None}, type: {type(label) if label else 'None'}")
    
    def set_timeout_callback(self, callback):
        """Set callback for when countdown expires."""
        self.timeout_callback = callback
    
    def set_countdown_finish_callback(self, callback):
        """Set callback for when countdown finishes."""
        self.countdown_finish_callback = callback
    
    def set_countdown_update_callback(self, callback):
        """Set callback for countdown updates (called with remaining seconds)."""
        self.countdown_update_callback = callback
    
    def set_root_after_callback(self, callback):
        """Legacy compatibility method."""
        pass
    
    def set_enabled(self, enabled):
        """Enable or disable countdown functionality."""
        self.countdown_enabled = enabled
    
    def start_countdown(self, minutes, screen_name):
        """Start countdown timer for a screen."""
        if not self.countdown_enabled:
            print(f"⏰ Countdown disabled - not starting timer for {screen_name}")
            return
        
        print(f"⏰ Starting {minutes} minute countdown for {screen_name}")
        
        # Stop any existing countdown
        self.stop_countdown()
        
        # Initialize countdown
        self.initial_duration = minutes * 60  # Convert to seconds
        self.countdown_remaining = self.initial_duration
        self.countdown_running = True
        self.screen_name = screen_name
        self.start_time = time.time()
        
        print(f"⏰ Countdown initialized: {self.countdown_remaining} seconds remaining")
        
        # Create and start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(100)  # Update every 100ms
        
        print(f"🎯 QTimer started for countdown updates")
    
    def update_countdown(self):
        """Update countdown display - called by QTimer."""
        try:
            # Check if we should continue
            if not self.countdown_running:
                return
            
            if self.get_current_screen and self.get_current_screen() != self.screen_name:
                return
            
            # Calculate remaining time
            elapsed = time.time() - self.start_time
            self.countdown_remaining = max(0, self.initial_duration - elapsed)
            
            # Convert to display format
            total_seconds = int(self.countdown_remaining)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            # Debug print occasionally (every 5 seconds)
            if total_seconds % 5 == 0 and self.countdown_remaining % 1 < 0.2:
                print(f"🎯 Countdown update: {minutes}:{seconds:02d} remaining")
            
            # Update main countdown label
            if self.countdown_label:
                if self.countdown_remaining > 60:
                    message = f"⏰ You only have {minutes}:{seconds:02d} left!"
                elif self.countdown_remaining > 30:
                    message = f"⚠️ HURRY! Only {seconds} seconds remaining!"
                elif self.countdown_remaining > 10:
                    message = f"🚨 CRITICAL! {seconds} seconds left!"
                else:
                    message = f"🚨 TIME RUNNING OUT! {seconds}s!"
                
                if hasattr(self.countdown_label, 'setText'):
                    self.countdown_label.setText(message)
                    # Force widget update
                    if hasattr(self.countdown_label, 'update'):
                        self.countdown_label.update()
            
            # Update corner countdown label
            if self.corner_countdown_label:
                corner_text = f"{minutes}:{seconds:02d}"
                if hasattr(self.corner_countdown_label, 'setText'):
                    self.corner_countdown_label.setText(corner_text)
                    # Force widget update
                    if hasattr(self.corner_countdown_label, 'update'):
                        self.corner_countdown_label.update()
            
            # Call custom update callback if set
            if self.countdown_update_callback:
                try:
                    self.countdown_update_callback(total_seconds)
                except Exception as e:
                    print(f"⚠️ Error in countdown update callback: {e}")
            
            # Check if time is up
            if self.countdown_remaining <= 0:
                print("⏰ Countdown finished!")
                self.stop_countdown()
                
                # Call callbacks
                if self.countdown_finish_callback:
                    self.countdown_finish_callback()
                
                if self.timeout_callback:
                    self.timeout_callback(self.screen_name)
        
        except Exception as e:
            print(f"⚠️ Error in countdown update: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
    
    def stop_countdown(self):
        """Stop the countdown timer."""
        self.countdown_running = False
        
        if self.timer:
            self.timer.stop()
            self.timer = None
        
        print("🎯 Countdown stopped")
    
    def get_remaining_time(self):
        """Get remaining time in seconds."""
        return max(0, int(self.countdown_remaining))
    
    # Legacy compatibility methods
    def update_countdown_display(self):
        """Legacy method - not used in new implementation."""
        pass
    
    def restore_countdown_from_seconds(self, seconds_remaining, screen_name="descriptivetask"):
        """Restore countdown from a specific number of seconds remaining."""
        print(f"🔄 Restoring countdown with {seconds_remaining} seconds remaining for screen: {screen_name}")
        # Convert to minutes and start
        minutes = seconds_remaining / 60
        self.start_countdown(minutes, screen_name)