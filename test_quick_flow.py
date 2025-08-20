#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Simple test to verify the flow
from src.app import MolyApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    print("🚀 Starting Moly test application...")
    
    moly_app = MolyApp()
    
    # Set test participant ID
    moly_app.set_participant_id("TEST001")
    
    # Test direct navigation to webpage screen
    print("🌐 Testing webpage screen...")
    
    try:
        moly_app.switch_to_screen(moly_app.webpage_screen)
        print("✅ Webpage screen switch successful")
    except Exception as e:
        print(f"❌ Error switching to webpage: {e}")
        import traceback
        print(traceback.format_exc())
    
    moly_app.show()
    sys.exit(app.exec())