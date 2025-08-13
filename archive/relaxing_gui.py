#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import math
import time
import threading
from datetime import datetime

class RelaxingGUI:
    def __init__(self):
        self.breathing_active = False
        self.wave_offset = 0
        self.timer_active = False
        self.timer_seconds = 0
        self.setup_gui()
        self.setup_breathing_circle()
        self.setup_animated_background()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Serenity")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Create main canvas for animations
        self.canvas = tk.Canvas(
            self.root, 
            width=900, 
            height=700,
            bg='#16213e',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create overlay frame for controls
        self.control_frame = tk.Frame(self.root, bg='#0f0f23', relief='flat')
        self.control_frame.place(x=50, y=50, width=200, height=120)
        
        # Breathing exercise button
        self.breathing_btn = tk.Button(
            self.control_frame,
            text="Start Breathing",
            font=('Inter', 12, 'normal'),
            bg='#4a5568',
            fg='#e2e8f0',
            activebackground='#2d3748',
            activeforeground='#ffffff',
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.toggle_breathing
        )
        self.breathing_btn.pack(pady=5)
        
        # Meditation timer button
        self.timer_btn = tk.Button(
            self.control_frame,
            text="5 Min Timer",
            font=('Inter', 10, 'normal'),
            bg='#38b2ac',
            fg='#ffffff',
            activebackground='#2c7a7b',
            activeforeground='#ffffff',
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.start_timer
        )
        self.timer_btn.pack(pady=2)
        
        # Time display
        self.time_label = tk.Label(
            self.control_frame,
            text="",
            font=('Inter', 14, 'normal'),
            fg='#a0aec0',
            bg='#0f0f23'
        )
        self.time_label.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(
            self.canvas,
            text="Welcome to Serenity",
            font=('Inter', 16, 'normal'),
            fg='#e2e8f0',
            bg='#16213e'
        )
        self.canvas.create_window(450, 600, window=self.status_label)
        
    def setup_breathing_circle(self):
        # Breathing circle parameters
        self.center_x = 450
        self.center_y = 350
        self.min_radius = 60
        self.max_radius = 120
        self.current_radius = self.min_radius
        self.breathing_phase = 0  # 0=inhale, 1=hold, 2=exhale, 3=hold
        self.phase_time = 0
        
        # Create circle
        self.breathing_circle = self.canvas.create_oval(
            self.center_x - self.current_radius,
            self.center_y - self.current_radius,
            self.center_x + self.current_radius,
            self.center_y + self.current_radius,
            fill='#4299e1',
            outline='#63b3ed',
            width=2
        )
        
        # Breathing text
        self.breathing_text = self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="Breathe",
            font=('Inter', 18, 'normal'),
            fill='#ffffff'
        )
        
    def setup_animated_background(self):
        # Create floating particles
        self.particles = []
        for i in range(20):
            x = (i * 45) % 900
            y = (i * 35) % 700
            particle = self.canvas.create_oval(
                x-2, y-2, x+2, y+2,
                fill='#4a5568',
                outline=''
            )
            self.particles.append({
                'id': particle,
                'x': x,
                'y': y,
                'dx': (i % 3 - 1) * 0.2,
                'dy': (i % 5 - 2) * 0.1,
                'opacity': 0.3 + (i % 4) * 0.1
            })
        
        # Start background animation
        self.animate_background()
        self.update_time()
        
    def animate_background(self):
        # Animate particles
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Wrap around edges
            if particle['x'] < 0:
                particle['x'] = 900
            elif particle['x'] > 900:
                particle['x'] = 0
                
            if particle['y'] < 0:
                particle['y'] = 700
            elif particle['y'] > 700:
                particle['y'] = 0
                
            # Update position
            self.canvas.coords(
                particle['id'],
                particle['x']-2,
                particle['y']-2,
                particle['x']+2,
                particle['y']+2
            )
        
        # Create subtle wave effect
        self.wave_offset += 0.02
        
        # Schedule next frame
        self.root.after(50, self.animate_background)
        
    def toggle_breathing(self):
        if not self.breathing_active:
            self.breathing_active = True
            self.breathing_btn.configure(text="Stop Breathing")
            self.status_label.configure(text="Breathe with the circle...")
            self.animate_breathing()
        else:
            self.breathing_active = False
            self.breathing_btn.configure(text="Start Breathing")
            self.status_label.configure(text="Breathing exercise stopped")
            
    def animate_breathing(self):
        if not self.breathing_active:
            return
            
        # Breathing cycle: 4s inhale, 1s hold, 6s exhale, 1s hold
        cycle_times = [4.0, 1.0, 6.0, 1.0]
        cycle_texts = ["Inhale...", "Hold...", "Exhale...", "Hold..."]
        
        self.phase_time += 0.1
        
        if self.phase_time >= cycle_times[self.breathing_phase]:
            self.phase_time = 0
            self.breathing_phase = (self.breathing_phase + 1) % 4
            
        # Update circle size based on phase
        progress = self.phase_time / cycle_times[self.breathing_phase]
        
        if self.breathing_phase == 0:  # Inhale
            size_progress = self.smooth_step(progress)
            self.current_radius = self.min_radius + (self.max_radius - self.min_radius) * size_progress
        elif self.breathing_phase == 2:  # Exhale
            size_progress = 1 - self.smooth_step(progress)
            self.current_radius = self.min_radius + (self.max_radius - self.min_radius) * size_progress
        
        # Update circle
        self.canvas.coords(
            self.breathing_circle,
            self.center_x - self.current_radius,
            self.center_y - self.current_radius,
            self.center_x + self.current_radius,
            self.center_y + self.current_radius
        )
        
        # Update text
        self.canvas.itemconfig(
            self.breathing_text,
            text=cycle_texts[self.breathing_phase]
        )
        
        # Change circle color based on phase
        colors = ['#4299e1', '#38b2ac', '#ed8936', '#9f7aea']
        self.canvas.itemconfig(
            self.breathing_circle,
            fill=colors[self.breathing_phase],
            outline=colors[self.breathing_phase]
        )
        
        # Schedule next frame
        self.root.after(100, self.animate_breathing)
        
    def smooth_step(self, t):
        return t * t * (3 - 2 * t)
        
    def start_timer(self):
        if not self.timer_active:
            self.timer_active = True
            self.timer_seconds = 300  # 5 minutes
            self.timer_btn.configure(text="Stop Timer", bg='#e53e3e')
            self.status_label.configure(text="Meditation timer started - 5:00")
            self.run_timer()
        else:
            self.timer_active = False
            self.timer_btn.configure(text="5 Min Timer", bg='#38b2ac')
            self.status_label.configure(text="Timer stopped")
            
    def run_timer(self):
        if not self.timer_active or self.timer_seconds <= 0:
            if self.timer_seconds <= 0:
                self.status_label.configure(text="🔔 Meditation complete! Well done.")
                self.timer_btn.configure(text="5 Min Timer", bg='#38b2ac')
                self.timer_active = False
            return
            
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        timer_text = f"Timer: {minutes}:{seconds:02d}"
        self.status_label.configure(text=timer_text)
        
        self.timer_seconds -= 1
        self.root.after(1000, self.run_timer)
        
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
        
    def run(self):
        print("Serenity GUI Started!")
        print("Click 'Start Breathing' to begin a relaxing breathing exercise")
        print("The gentle animations will help you feel calm and centered")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")

def main():
    try:
        app = RelaxingGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have tkinter installed")

if __name__ == "__main__":
    main()