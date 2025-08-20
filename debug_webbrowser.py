#!/usr/bin/env python3

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class DebugApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug WebBrowser")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Try to create web view
        try:
            web_view = QWebEngineView()
            web_view.setMinimumSize(400, 300)
            web_view.load(QUrl("https://www.google.com"))
            layout.addWidget(web_view)
            print("✅ WebEngineView created successfully")
        except Exception as e:
            error_label = QLabel(f"WebEngine Error: {e}")
            error_label.setStyleSheet("background-color: red; color: white; padding: 20px;")
            layout.addWidget(error_label)
            print(f"❌ WebEngine Error: {e}")
            
        # Add status label
        status_label = QLabel("Testing web browser functionality...")
        layout.addWidget(status_label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    debug_app = DebugApp()
    debug_app.show()
    
    sys.exit(app.exec())