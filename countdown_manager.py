#!/usr/bin/env python3

import time
import threading
import tkinter as tk


class CountdownManager:
    """Manages countdown timer functionality for the Moly app."""
    
    def __init__(self, logging_manager):
        self.logging_manager = logging_manager
        
        # Countdown state
        self.countdown_remaining = 0
        self.countdown_thread = None
        self.countdown_label = None
        self.corner_countdown_label = None  # Secondary countdown in top-right corner
        self.countdown_running = False
        self.countdown_enabled = True
        
        # Current screen reference (to be set by parent)
        self.get_current_screen = None
        
        # Callbacks
        self.countdown_finish_callback = None
    
    def set_current_screen_callback(self, callback):
        """Set callback to get current screen."""
        self.get_current_screen = callback
    
    def set_countdown_label(self, label):
        """Set the countdown label widget."""
        self.countdown_label = label
    
    def setup_countdown_label(self, label):
        """Set up the countdown label widget."""
        self.countdown_label = label
    
    def set_corner_countdown_label(self, label):
        """Set the corner countdown label widget."""
        self.corner_countdown_label = label
    
    def start_countdown(self, minutes, screen_name):
        """Start countdown timer for a screen with milliseconds precision."""
        if not self.countdown_enabled:
            print(f"⏰ Countdown disabled - not starting timer for {screen_name}")
            return
        
        print(f"⏰ Starting {minutes} minute countdown for {screen_name}")
        
        # Stop any existing countdown first
        self.stop_countdown()
        
        self.countdown_remaining = minutes * 60 * 1000  # Convert to milliseconds
        self.countdown_running = True
        
        print(f"⏰ Countdown initialized: {self.countdown_remaining}ms remaining")
        
        # Record start time for accurate timing
        start_time = time.time() * 1000  # Get current time in milliseconds
        initial_countdown = self.countdown_remaining
        
        def countdown_loop():
            while (self.countdown_remaining > 0 and 
                   self.countdown_running and 
                   (not self.get_current_screen or self.get_current_screen() == screen_name)):
                try:
                    if self.countdown_running:  # Double-check before updating
                        # Calculate actual elapsed time and update countdown
                        current_time = time.time() * 1000
                        elapsed = current_time - start_time
                        self.countdown_remaining = max(0, initial_countdown - int(elapsed))
                        
                        self.update_countdown_display()

                        # Log countdown state every 30 seconds for recovery
                        seconds_remaining = self.countdown_remaining // 1000
                        if seconds_remaining % 30 == 0 and self.countdown_remaining % 1000 < 100:
                            total_seconds = minutes * 60
                            self.logging_manager.log_countdown_state(seconds_remaining, total_seconds, screen_name)

                    time.sleep(0.01)  # Update every 10ms for smooth display
                except (tk.TclError, AttributeError) as e:
                    print(f"⚠️ Countdown loop error: {e}")
                    break
            
            # Time's up notification
            if (self.countdown_remaining <= 0 and 
                self.countdown_running and 
                (not self.get_current_screen or self.get_current_screen() == screen_name)):
                try:
                    # Call finish callback first (for enabling navigation)
                    if hasattr(self, 'countdown_finish_callback') and self.countdown_finish_callback:
                        self.countdown_finish_callback()
                    
                    # Then call timeout callback (for automatic transitions)
                    if hasattr(self, 'timeout_callback') and self.timeout_callback:
                        self.timeout_callback(screen_name)
                except (tk.TclError, AttributeError):
                    pass
        
        self.countdown_thread = threading.Thread(target=countdown_loop, daemon=True)
        self.countdown_thread.start()
    
    def update_countdown_display(self):
        """Update the countdown display with milliseconds precision."""
        if not self.countdown_enabled or not self.countdown_running:
            return
        
        # Convert milliseconds to minutes, seconds, and milliseconds
        total_seconds = int(self.countdown_remaining // 1000)
        milliseconds = int((self.countdown_remaining % 1000) // 10)  # Show centiseconds (0-99)
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        
        # Update main countdown label (detailed message)
        if self.countdown_label:
            # Create stressful message based on remaining time (in milliseconds)
            if self.countdown_remaining > 60000:  # More than 1 minute
                stress_msg = f"⏰ You only have {minutes:01d}:{seconds:02d}.{milliseconds:02d} left!"
            elif self.countdown_remaining > 30000:  # 30-60 seconds
                stress_msg = f"⚠️ HURRY! Only {seconds:02d}.{milliseconds:02d} seconds remaining!"
            elif self.countdown_remaining > 10000:  # 10-30 seconds
                stress_msg = f"🚨 CRITICAL! {seconds:02d}.{milliseconds:02d} seconds left!"
            else:  # Less than 10 seconds
                stress_msg = f"🚨 TIME RUNNING OUT! {seconds:02d}.{milliseconds:02d}s!"
            
            # Color based on urgency (using milliseconds)
            if self.countdown_remaining > 120000:  # More than 2 minutes
                color = '#ffaa44'
            elif self.countdown_remaining > 60000:  # 1-2 minutes
                color = '#ff6666'
            else:  # Less than 1 minute
                color = '#ff0000'
                
            try:
                self.countdown_label.config(text=stress_msg, fg=color)
            except (tk.TclError, AttributeError):
                pass
        
        # Update corner countdown label (simple minutes:seconds format)
        if self.corner_countdown_label:
            corner_text = f"{minutes:01d}:{seconds:02d}"
            
            # Color for corner countdown (more visible)
            if self.countdown_remaining > 60000:  # More than 1 minute
                corner_color = '#00FF00'  # Bright green
            elif self.countdown_remaining > 30000:  # 30-60 seconds
                corner_color = '#FFFF00'  # Bright yellow
            elif self.countdown_remaining > 10000:  # 10-30 seconds
                corner_color = '#FF8000'  # Bright orange
            else:  # Less than 10 seconds
                corner_color = '#FF0000'  # Bright red
            
            try:
                self.corner_countdown_label.config(text=corner_text, fg=corner_color)
            except (tk.TclError, AttributeError):
                pass
    
    def update_countdown_label(self, text, color):
        """Update countdown label safely in main thread."""
        if self.countdown_label and self.countdown_running:
            try:
                # Double-check the label still exists before updating
                if hasattr(self.countdown_label, 'config'):
                    self.countdown_label.config(text=text, fg=color)
            except (tk.TclError, AttributeError):
                # Label was destroyed, stop trying to update it
                self.countdown_label = None
    
    def stop_countdown(self):
        """Stop the current countdown safely."""
        # Signal countdown to stop
        self.countdown_running = False
        
        # Wait for thread to finish with timeout
        if self.countdown_thread and self.countdown_thread.is_alive():
            try:
                self.countdown_thread.join(timeout=0.5)
            except:
                pass
        
        # Clear the thread reference
        self.countdown_thread = None
        
        # Don't clear countdown label - let it be reused by next screen
        # self.countdown_label = None  # Commented out to fix display issue
        
        # Clear countdown finish callback to avoid conflicts
        self.countdown_finish_callback = None
    
    def set_timeout_callback(self, callback):
        """Set callback for when countdown expires."""
        self.timeout_callback = callback
    
    def set_countdown_finish_callback(self, callback):
        """Set callback for when countdown finishes (reaches 0)."""
        self.countdown_finish_callback = callback
    
    def set_root_after_callback(self, callback):
        """Set callback for root.after() calls."""
        self.root_after = callback
    
    def restore_countdown_from_seconds(self, seconds_remaining):
        """Restore countdown from a specific number of seconds remaining."""
        if seconds_remaining > 0:
            self.countdown_remaining = int(seconds_remaining * 1000)  # Convert to milliseconds
            self.countdown_running = True
            print(f"🔄 Restored countdown: {seconds_remaining} seconds remaining")
            
            # Start the countdown from where it left off
            self.start_restored_countdown()
    
    def start_restored_countdown(self):
        """Start countdown from restored state (for recovery)."""
        if not hasattr(self, 'countdown_remaining') or self.countdown_remaining <= 0:
            return

        print(f"⏱️ Starting restored countdown with {self.countdown_remaining // 1000} seconds remaining")

        # Record start time for accurate timing
        start_time = time.time() * 1000  # Get current time in milliseconds
        initial_countdown = self.countdown_remaining
        
        def restored_countdown_loop():
            while (self.countdown_remaining > 0 and
                   self.countdown_running and
                   self.countdown_label):
                try:
                    # Calculate actual elapsed time and update countdown
                    current_time = time.time() * 1000
                    elapsed = current_time - start_time
                    self.countdown_remaining = max(0, initial_countdown - int(elapsed))
                    
                    # Update display
                    seconds = self.countdown_remaining // 1000
                    minutes = seconds // 60
                    secs = seconds % 60
                    
                    if self.countdown_label:
                        try:
                            self.countdown_label.config(text=f"⏱️ Time remaining: {minutes:02d}:{secs:02d}")
                        except (tk.TclError, AttributeError):
                            break

                    # Log countdown state periodically (every 30 seconds)
                    if seconds % 30 == 0 and self.countdown_remaining % 1000 < 100:
                        from config import DESCRIPTIVE_COUNTDOWN_MINUTES
                        total_time = DESCRIPTIVE_COUNTDOWN_MINUTES * 60
                        self.logging_manager.log_countdown_state(seconds, total_time, "descriptive_task")

                    # Sleep for smooth display updates
                    time.sleep(0.1)  # Update every 100ms

                except Exception as e:
                    print(f"⚠️ Error in restored countdown: {e}")
                    break

            # Time's up notification
            if (self.countdown_remaining <= 0 and
                self.countdown_running and
                self.countdown_label):
                try:
                    self.countdown_label.config(text="⏰ Time's up!", fg='red')
                    self.countdown_running = False
                except:
                    pass

        # Start countdown in a separate thread
        countdown_thread = threading.Thread(target=restored_countdown_loop, daemon=True)
        countdown_thread.start()
    
    def set_enabled(self, enabled):
        """Enable or disable countdown functionality."""
        self.countdown_enabled = enabled
    
    def get_remaining_time(self):
        """Get remaining time in seconds."""
        return self.countdown_remaining // 1000 if self.countdown_remaining > 0 else 0