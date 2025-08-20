#!/usr/bin/env python3
"""
Test script to verify PyQt6 migration.
This will test basic functionality of the converted screens.
"""

import sys
import os
sys.path.insert(0, 'src')

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from config import *

# Test imports
try:
    from screens.base_screen import BaseScreen
    from screens.participant_id_screen import ParticipantIDScreen
    from screens.webpage_screen import WebpageScreen
    print("✅ All screen imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TestApp:
    """Minimal test app to verify screen functionality."""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.screen_width = 800
        self.screen_height = 600
        self.current_screen = "test"
        
        # Mock methods that screens expect
        self.logging_manager = None
        
    def clear_screen(self):
        pass
    
    def set_participant_id(self, pid):
        print(f"📝 Participant ID set: {pid}")
    
    def switch_to_webpage_screen(self):
        print("🔄 Would switch to webpage screen")

def test_basic_functionality():
    """Test basic screen creation and setup."""
    print("\n🧪 Testing PyQt6 Migration")
    print("=" * 40)
    
    # Create test app
    test_app = TestApp()
    
    try:
        # Test BaseScreen (abstract, so we'll test a concrete implementation)
        print("Testing ParticipantIDScreen...")
        participant_screen = ParticipantIDScreen(test_app)
        participant_screen.setup_screen()
        print("✅ ParticipantIDScreen created successfully")
        
        print("Testing WebpageScreen...")
        webpage_screen = WebpageScreen(test_app)
        webpage_screen.setup_screen()
        print("✅ WebpageScreen created successfully")
        
        print("\n🎉 All tests passed! PyQt6 migration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_functionality()
    if success:
        print("\n✅ Migration verification complete - all systems go!")
        sys.exit(0)
    else:
        print("\n❌ Migration verification failed - needs fixes")
        sys.exit(1)