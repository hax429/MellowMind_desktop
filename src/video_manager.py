#!/usr/bin/env python3

import cv2
import os
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk


class VideoManager:
    """Manages video playback functionality for the Moly app."""
    
    def __init__(self):
        self.cap = None
        self.video_frame = None
        self.running = True
        
        # Stroop-specific properties
        self.is_playing = False
        self.is_paused = False
        
        # Screen dimensions (to be set by parent)
        self.screen_width = None
        self.screen_height = None
        
        # Video completion callbacks
        self.video_end_callback = None
    
    def set_screen_dimensions(self, width, height):
        """Set screen dimensions for video scaling."""
        self.screen_width = width
        self.screen_height = height
    
    def set_video_end_callback(self, callback):
        """Set callback to be called when video reaches its natural end."""
        self.video_end_callback = callback
    
    def init_video(self, video_path):
        """Initialize video capture."""
        print(f"🎬 Initializing video: {video_path}")
        
        # Reset running flag when initializing new video
        self.running = True
        
        if os.path.exists(video_path):
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                print(f"❌ Warning: Could not open video file {video_path}")
                self.cap = None
            else:
                print(f"✅ Video initialized: {os.path.basename(video_path)}")
        else:
            print(f"❌ Warning: Video file not found at {video_path}")
            self.cap = None
    
    def get_video_frame(self):
        """Get current video frame for relaxation screen."""
        try:
            if self.cap is None:
                print("🎬 ERROR: Video capture is None")
                return None
                
            ret, frame = self.cap.read()
            if not ret:
                # Video has ended - check if we should call the end callback
                print("🎬 End of video reached")
                if self.video_end_callback:
                    print("🎬 Calling video end callback")
                    self.video_end_callback()
                    # Only call the callback once
                    self.video_end_callback = None
                
                # Loop video - restart from beginning
                print("🎬 Looping back to start")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    print("🎬 ERROR: Could not read frame even after restart")
                    return None
            
            # Get original video dimensions
            video_height, video_width = frame.shape[:2]
            
            # Calculate aspect ratios
            video_aspect = video_width / video_height
            screen_aspect = self.screen_width / self.screen_height
            
            # Scale to fit screen while maintaining aspect ratio
            if video_aspect > screen_aspect:
                # Video is wider - scale by height
                new_height = self.screen_height
                new_width = int(self.screen_height * video_aspect)
            else:
                # Video is taller - scale by width
                new_width = self.screen_width
                new_height = int(self.screen_width / video_aspect)
            
            # Resize frame
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            # Convert to PhotoImage
            try:
                return ImageTk.PhotoImage(pil_image)
            except Exception as photo_error:
                print(f"🎬 ERROR creating PhotoImage: {photo_error}")
                return None
        except Exception as e:
            print(f"Warning: Error reading video frame: {e}")
            return None
    
    def get_stroop_video_frame(self):
        """Get current video frame for stroop screen."""
        try:
            if self.cap is None:
                return None
                
            ret, frame = self.cap.read()
            if not ret:
                # Video has ended - check if we should call the end callback
                print("🎬 Stroop video ended")
                if self.video_end_callback:
                    print("🎬 Calling stroop video end callback")
                    self.video_end_callback()
                    # Only call the callback once
                    self.video_end_callback = None
                
                # Loop video - restart from beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return None
            
            # Resize frame to fit canvas (800x450)
            frame = cv2.resize(frame, (800, 450))
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image then PhotoImage
            pil_image = Image.fromarray(frame)
            try:
                return ImageTk.PhotoImage(pil_image)
            except Exception as photo_error:
                print(f"🎬 ERROR creating stroop PhotoImage: {photo_error}")
                return None
        except Exception as e:
            print(f"Warning: Error reading stroop video frame: {e}")
            return None
    
    def update_video_background(self, canvas, text_item=None):
        """Update video background for relaxation screen."""
        try:
            new_frame = self.get_video_frame()
            if new_frame and canvas:
                # Remove old frame
                if hasattr(self, 'video_bg_item'):
                    canvas.delete(self.video_bg_item)
                
                # Add new frame as background, centered
                self.video_bg_item = canvas.create_image(
                    self.screen_width // 2, self.screen_height // 2, 
                    anchor=tk.CENTER, image=new_frame
                )
                # Keep reference to prevent garbage collection
                self.video_frame = new_frame
                
                # Bring text to front if it exists
                if text_item:
                    canvas.tag_raise(text_item)
        except (tk.TclError, AttributeError):
            # Canvas or window was destroyed
            pass
    
    def update_stroop_video_display(self, canvas):
        """Update stroop video display on canvas."""
        try:
            new_frame = self.get_stroop_video_frame()
            if new_frame and canvas:
                # Remove old frame
                canvas.delete("video_frame")
                
                # Add new frame
                canvas.create_image(
                    400, 225,  # Center of 800x450 canvas
                    image=new_frame,
                    tags="video_frame"
                )
                
                # Keep reference to prevent garbage collection
                self.video_frame = new_frame
        except (tk.TclError, AttributeError):
            # Canvas or window was destroyed
            pass
    
    def start_video_loop(self, canvas, current_screen, text_item=None):
        """Start video loop for relaxation screen."""
        print(f"🎬 Starting video loop for relaxation screen")
        if not (hasattr(self, 'cap') and self.cap is not None):
            print("🎬 ERROR: No video capture available!")
            return
        
        def update_frame():
            """Update frame in main thread using after()."""
            try:
                if self.running and current_screen() == "relaxation" and hasattr(self, 'cap') and self.cap:
                    self.update_video_background(canvas, text_item)
                    # Schedule next frame
                    canvas.after(33, update_frame)  # ~30 FPS (33ms)
                else:
                    print(f"🎬 Video loop ended - running: {self.running}, screen: {current_screen()}")
            except (tk.TclError, AttributeError) as e:
                print(f"🎬 Video loop stopped: {e}")
        
        # Start the frame updates
        update_frame()
    
    def start_post_study_video_loop(self, canvas, current_screen, text_item=None):
        """Start video loop for post-study rest screen."""
        print(f"🎬 Starting post-study video loop")
        
        def update_frame():
            """Update frame in main thread using after()."""
            try:
                if self.running and current_screen() == "post_study_rest" and hasattr(self, 'cap') and self.cap:
                    self.update_video_background(canvas, text_item)
                    # Schedule next frame
                    canvas.after(33, update_frame)  # ~30 FPS (33ms)
                else:
                    print(f"🎬 Post-study video loop ended - running: {self.running}, screen: {current_screen()}")
            except (tk.TclError, AttributeError) as e:
                print(f"🎬 Post-study video loop stopped: {e}")
        
        # Start the frame updates
        update_frame()
    
    def start_stroop_video_loop(self, canvas, current_screen, update_callback=None):
        """Start stroop video playback loop."""
        def video_loop():
            while self.running and self.is_playing and current_screen() == "stroop":
                try:
                    if not self.is_paused and hasattr(self, 'cap') and self.cap:
                        new_frame = self.get_stroop_video_frame()
                        if new_frame and update_callback:
                            # Update canvas with new frame
                            update_callback(new_frame)
                    time.sleep(1/30)  # 30 FPS
                except (tk.TclError, AttributeError):
                    # Window closed or object destroyed
                    break
        
        thread = threading.Thread(target=video_loop, daemon=True)
        thread.start()
    
    def toggle_video_playback(self, status_callback=None):
        """Toggle video playback in stroop screen."""
        if self.cap is None:
            if status_callback:
                status_callback("❌ Video file not found", '#ff6666')
            return
        
        try:
            if not self.is_playing and not self.is_paused:
                # Start playing - set video to start at 3:00 (180 seconds)
                self.is_playing = True
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                frame_number = int(180 * fps)  # 180 seconds * fps
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                if status_callback:
                    status_callback("🎬 Playing...", '#66ff99')
                
            elif self.is_playing and not self.is_paused:
                # Pause
                self.is_paused = True
                if status_callback:
                    status_callback("⏸️ Paused", '#ffff66')
                
            elif self.is_paused:
                # Resume
                self.is_paused = False
                if status_callback:
                    status_callback("🎬 Playing...", '#66ff99')
                
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Video error: {str(e)}", '#ff6666')
    
    def restart_video(self, status_callback=None):
        """Restart video from beginning."""
        if self.cap and (self.is_playing or self.is_paused):
            self.is_playing = False
            self.is_paused = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if status_callback:
                status_callback("🔄 Restarted", '#66ccff')
    
    def stop_video(self):
        """Stop video playback and release resources."""
        self.running = False
        self.is_playing = False
        self.is_paused = False
        
        # Wait a moment for video threads to finish
        time.sleep(0.1)

        # Clean up video capture safely
        if hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except Exception as e:
                print(f"Warning: Error releasing video capture: {e}")
            finally:
                self.cap = None
        
        # Clear video frame reference
        if hasattr(self, 'video_frame'):
            self.video_frame = None
    
    def cleanup(self):
        """Clean up video resources."""
        self.stop_video()