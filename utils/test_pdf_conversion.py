#!/usr/bin/env python3
"""
Simple PDF to Image Conversion Test
Tests PDF conversion in isolation to debug issues.
"""

import os
import sys
import traceback

def test_pdf_conversion():
    """Test PDF to image conversion with detailed debugging."""
    
    print("🧪 PDF Conversion Test")
    print("=" * 50)
    
    # Find PDF file
    pdf_paths = [
        'res/brief.pdf',
        '../res/brief.pdf',
        '../../res/brief.pdf',
        os.path.join(os.path.dirname(__file__), '..', 'res', 'brief.pdf')
    ]
    
    pdf_path = None
    for path in pdf_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            pdf_path = abs_path
            break
    
    if not pdf_path:
        print("❌ PDF file not found")
        return False
    
    print(f"📄 PDF file: {pdf_path}")
    print(f"📊 PDF size: {os.path.getsize(pdf_path)} bytes")
    print(f"🔐 PDF permissions: {oct(os.stat(pdf_path).st_mode)[-3:]}")
    
    # Test import
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image imported successfully")
    except ImportError as e:
        print(f"❌ Cannot import pdf2image: {e}")
        return False
    
    # Test basic conversion
    print("\n🔄 Testing basic conversion...")
    try:
        images = convert_from_path(pdf_path, dpi=150)
        if images:
            print(f"✅ Basic conversion successful: {len(images)} pages")
            for i, img in enumerate(images):
                print(f"   Page {i+1}: {img.size} ({img.mode})")
        else:
            print("❌ Basic conversion returned no images")
            return False
    except Exception as e:
        print(f"❌ Basic conversion failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"🔍 Full traceback:")
        traceback.print_exc()
        
        # Try with different settings
        print("\n🔄 Trying with different settings...")
        
        # Try lower DPI
        try:
            print("🔄 Trying DPI=75...")
            images = convert_from_path(pdf_path, dpi=75)
            print(f"✅ Lower DPI worked: {len(images)} pages")
        except Exception as e2:
            print(f"❌ Lower DPI failed: {e2}")
        
        # Try single page
        try:
            print("🔄 Trying first page only...")
            images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)
            print(f"✅ Single page worked: {len(images)} pages")
        except Exception as e3:
            print(f"❌ Single page failed: {e3}")
        
        return False
    
    # Test with explicit poppler path
    print("\n🔄 Testing with explicit poppler path...")
    
    # Get poppler paths to test
    poppler_paths = [
        '/opt/miniconda3/envs/moly/bin',
        '/opt/anaconda3/envs/moly/bin',
        '/opt/homebrew/bin',
        '/usr/local/bin',
        '/usr/bin'
    ]
    
    for poppler_path in poppler_paths:
        if os.path.exists(os.path.join(poppler_path, 'pdftoppm')):
            print(f"🔄 Testing with poppler path: {poppler_path}")
            try:
                images = convert_from_path(pdf_path, dpi=150, poppler_path=poppler_path)
                if images:
                    print(f"✅ Explicit poppler path worked: {len(images)} pages")
                else:
                    print(f"⚠️ Explicit poppler path returned no images")
            except Exception as e:
                print(f"❌ Explicit poppler path failed: {e}")
    
    # Test PyQt6 image conversion
    print("\n🔄 Testing PyQt6 image conversion...")
    try:
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QApplication
        import io
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        if images:
            # Convert first image to QPixmap
            img = images[0]
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            success = pixmap.loadFromData(buffer.getvalue())
            if success:
                print(f"✅ PyQt6 conversion successful: {pixmap.size()}")
            else:
                print("❌ PyQt6 conversion failed")
        else:
            print("⚠️ No images to test PyQt6 conversion")
            
    except Exception as e:
        print(f"❌ PyQt6 test failed: {e}")
    
    return True

if __name__ == "__main__":
    test_pdf_conversion()