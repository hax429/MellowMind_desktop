#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QStackedWidget
from src.screens.webpage_screen import WebpageScreen
from src.logging_manager import LoggingManager
from src.app import MolyApp

class TestApp:
    def __init__(self):
        self.logging_manager = LoggingManager()
        self.main_window = None
        
    def test_webpage_screen(self):
        """Test webpage screen directly"""
        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        
        # Create test window
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        test_window = QWidget()
        test_window.setWindowTitle("Test Webpage Screen")
        test_window.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(test_window)
        
        # Create and test webpage screen
        webpage_screen = WebpageScreen(self, self.logging_manager)
        layout.addWidget(webpage_screen)
        
        test_window.show()
        
        # Show the webpage screen
        webpage_screen.show()
        
        sys.exit(app.exec())

if __name__ == '__main__':
    test_app = TestApp()
    test_app.test_webpage_screen()