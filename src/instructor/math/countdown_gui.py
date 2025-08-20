#!/usr/bin/env python3

import os
import subprocess
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QScrollArea, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

class CountdownGUI(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.setWindowTitle("Countdown Task")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title_label = QLabel("Countdown: 4000 - 7 sequence")
        self.title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white; background-color: black;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # Scrollable area for numbers
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("background-color: black; border: none;")
        self.scroll_area.setWidgetResizable(True)
        
        # Scrollable widget and layout
        self.scrollable_widget = QWidget()
        self.scrollable_widget.setStyleSheet("background-color: black;")
        self.scroll_layout = QGridLayout(self.scrollable_widget)
        
        self.scroll_area.setWidget(self.scrollable_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
    def setup_shortcuts(self):
        # Spacebar
        spacebar_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        spacebar_shortcut.activated.connect(self.on_spacebar)
        
        # Escape
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.close_app)
        
        # Arrow keys
        up_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up_shortcut.activated.connect(lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() - 50))
        
        down_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down_shortcut.activated.connect(lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() + 50))
        
        # Page Up/Down
        pageup_shortcut = QShortcut(QKeySequence(Qt.Key.Key_PageUp), self)
        pageup_shortcut.activated.connect(lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() - 200))
        
        pagedown_shortcut = QShortcut(QKeySequence(Qt.Key.Key_PageDown), self)
        pagedown_shortcut.activated.connect(lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() + 200))
        
        # Left/Right for highlight
        left_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        left_shortcut.activated.connect(self.move_highlight_backward)
        
        right_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        right_shortcut.activated.connect(self.move_highlight_forward)
    
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
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
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
                border_style = "border: 4px solid white;"
            else:
                bg_color = 'black'
                border_style = "border: 2px solid gray;"
            
            number_label = QLabel(str(number))
            number_label.setFont(QFont('Arial', 32, QFont.Weight.Bold))
            number_label.setStyleSheet(f"""
                color: {color};
                background-color: {bg_color};
                {border_style}
                padding: 10px;
                min-width: 120px;
                min-height: 60px;
            """)
            number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            number_label.setFixedSize(140, 80)
            
            self.scroll_layout.addWidget(number_label, row, col)
            self.number_labels.append(number_label)
    
    def move_highlight_forward(self):
        if self.highlighted_index < len(self.numbers) - 1:
            self.highlighted_index += 1
            self.update_highlight()
    
    def move_highlight_backward(self):
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
                bg_color = 'darkblue'
                border_style = "border: 4px solid white;"
            else:
                bg_color = 'black'
                border_style = "border: 2px solid gray;"
            
            label.setStyleSheet(f"""
                color: {color};
                background-color: {bg_color};
                {border_style}
                padding: 10px;
                min-width: 120px;
                min-height: 60px;
            """)
    
    def on_spacebar(self):
        if self.current_process and self.current_process.poll() is None:
            print("SPACEBAR PRESSED! Interrupting current audio and starting new one...")
        else:
            print("SPACEBAR PRESSED! Playing sound...")
        self.play_sound()
    
    def close_app(self):
        self.stop_current_audio()
        self.close()
    
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
    
    def closeEvent(self, event):
        self.stop_current_audio()
        event.accept()

def main():
    try:
        app = QApplication(sys.argv)
        window = CountdownGUI()
        window.show()
        
        print("Countdown GUI Started!")
        print("Use arrow keys, Page Up/Down to scroll")
        print("Use Left/Right arrows to move highlight")
        print("Press SPACEBAR to play sound")
        print("Press ESC to exit")
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have the required libraries installed:")
        print("pip install PyQt6")

if __name__ == "__main__":
    main()