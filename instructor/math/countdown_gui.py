#!/usr/bin/env python3

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

class CountdownGUI:
    def __init__(self):
        self.setup_sound_path()
        self.current_process = None
        self.generate_countdown_numbers()
        self.highlighted_index = 1  # Start with 3993 (index 1)
        self.number_labels = []
        self.setup_gui()
        self.setup_display()
        
    def setup_sound_path(self):
        self.beep_path = os.path.join(os.path.dirname(__file__), 'res', 'beep.m4a')
        if not os.path.exists(self.beep_path):
            print(f"Warning: Could not find beep.m4a at {self.beep_path}")
            self.beep_path = None
        else:
            print(f"Sound file found: {self.beep_path}")
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Countdown Task")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        
        # Bind spacebar globally
        self.root.bind('<KeyPress-space>', self.on_spacebar)
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = tk.Label(
            self.main_frame, 
            text="Countdown: 4000 - 7 sequence",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='black'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Scrollable frame for numbers
        self.canvas = tk.Canvas(self.main_frame, bg='black', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='black')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.root.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.root.bind("<Page_Up>", lambda e: self.canvas.yview_scroll(-10, "units"))
        self.root.bind("<Page_Down>", lambda e: self.canvas.yview_scroll(10, "units"))
        self.root.bind("<Right>", self.move_highlight_forward)
        self.root.bind("<Left>", self.move_highlight_backward)
    
    def generate_countdown_numbers(self):
        self.numbers = []
        current = 4000
        while current > 0:
            self.numbers.append(current)
            current -= 7
        # Add a few more to show it goes negative
        for i in range(5):
            self.numbers.append(current)
            current -= 7
    
    def setup_display(self):
        # Clear existing numbers
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.number_labels = []
        
        # Display all numbers in a grid
        cols = 4
        for i, number in enumerate(self.numbers):
            row = i // cols
            col = i % cols
            
            # Color coding
            if number > 0:
                color = 'lightgreen'
            elif number == 0:
                color = 'yellow'
            else:
                color = 'lightcoral'
            
            # Highlight style for selected number
            if i == self.highlighted_index:
                bg_color = 'darkblue'
                border_color = 'white'
                border_width = 4
            else:
                bg_color = 'black'
                border_color = 'gray'
                border_width = 2
            
            number_label = tk.Label(
                self.scrollable_frame,
                text=str(number),
                font=('Arial', 32, 'bold'),
                fg=color,
                bg=bg_color,
                width=8,
                relief='ridge',
                borderwidth=border_width,
                highlightbackground=border_color,
                highlightthickness=2 if i == self.highlighted_index else 0
            )
            number_label.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.number_labels.append(number_label)
        
        # Configure grid weights for responsiveness
        for i in range(cols):
            self.scrollable_frame.columnconfigure(i, weight=1)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def move_highlight_forward(self, event):
        if self.highlighted_index < len(self.numbers) - 1:
            self.highlighted_index += 1
            self.update_highlight()
    
    def move_highlight_backward(self, event):
        if self.highlighted_index > 0:
            self.highlighted_index -= 1
            self.update_highlight()
    
    def update_highlight(self):
        # Update all labels to reflect new highlight position
        for i, label in enumerate(self.number_labels):
            number = self.numbers[i]
            
            # Color coding
            if number > 0:
                color = 'lightgreen'
            elif number == 0:
                color = 'yellow'
            else:
                color = 'lightcoral'
            
            # Highlight style for selected number
            if i == self.highlighted_index:
                label.configure(bg='darkblue', borderwidth=4, highlightthickness=2)
            else:
                label.configure(bg='black', borderwidth=2, highlightthickness=0)
            
            label.configure(fg=color)
    
    def on_key_press(self, event):
        if event.keysym == 'Escape':
            self.stop_current_audio()
            self.root.quit()
    
    def on_spacebar(self, event):
        if self.current_process and self.current_process.poll() is None:
            print("SPACEBAR PRESSED! Interrupting current audio and starting new one...")
        else:
            print("SPACEBAR PRESSED! Playing sound...")
        self.play_sound()
    
    def stop_current_audio(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
            self.current_process = None
    
    def play_sound(self):
        if not self.beep_path:
            print("No sound file available")
            return
            
        try:
            # Stop any currently playing audio
            self.stop_current_audio()
            
            # Start new audio playback
            self.current_process = subprocess.Popen(['afplay', self.beep_path])
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def run(self):
        print("Countdown GUI Started!")
        print("Use arrow keys, Page Up/Down, or mouse wheel to scroll")
        print("Press SPACEBAR to play sound")
        print("Press ESC to exit")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
        finally:
            self.stop_current_audio()

def main():
    try:
        app = CountdownGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have the required libraries installed:")
        print("pip install tkinter")

if __name__ == "__main__":
    main()