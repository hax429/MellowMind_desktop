#!/usr/bin/env python3
"""
PDF Display Diagnostic Tool
Checks for PDF rendering dependencies and troubleshoots issues.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_packages():
    """Check if required Python packages are installed."""
    print("🔍 Checking Python packages...")
    
    # Check pdf2image
    try:
        import pdf2image
        try:
            version = pdf2image.__version__
        except AttributeError:
            version = "available (version unknown)"
        print(f"✅ pdf2image: {version}")
    except ImportError:
        print("❌ pdf2image: Not installed")
        print("   Install with: pip install pdf2image")
    
    # Check PyPDF2
    try:
        import PyPDF2
        try:
            version = PyPDF2.__version__
        except AttributeError:
            version = "available (version unknown)"
        print(f"✅ PyPDF2: {version}")
    except ImportError:
        print("❌ PyPDF2: Not installed")
        print("   Install with: pip install PyPDF2")
    
    # Check PyQt6 WebEngine
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt6.QtWebEngineWidgets: Available")
    except ImportError:
        print("❌ PyQt6.QtWebEngineWidgets: Not available")
        print("   Install with: pip install PyQt6-WebEngine")

def check_poppler():
    """Check if poppler-utils is installed and accessible."""
    print("\n🔍 Checking Poppler utilities...")
    
    # Common poppler paths to check
    poppler_commands = ['pdftoppm', 'pdfinfo', 'pdfimages']
    
    for cmd in poppler_commands:
        try:
            result = subprocess.run([cmd, '-v'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {cmd}: Available")
                # Try to get version info
                version_result = subprocess.run([cmd, '-v'], capture_output=True, text=True, timeout=5)
                if version_result.stderr:
                    version_info = version_result.stderr.split('\n')[0]
                    print(f"   Version: {version_info}")
            else:
                print(f"❌ {cmd}: Error - {result.stderr.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {cmd}: Not found in PATH")
    
    # Check common installation paths
    common_paths = [
        '/usr/bin',
        '/usr/local/bin',
        '/opt/homebrew/bin',
        '/opt/miniconda3/envs/moly/bin',
        '/opt/anaconda3/envs/moly/bin'
    ]
    
    print("\n🔍 Checking common installation paths...")
    for path in common_paths:
        pdftoppm_path = os.path.join(path, 'pdftoppm')
        if os.path.exists(pdftoppm_path):
            print(f"✅ Found pdftoppm at: {pdftoppm_path}")
        else:
            print(f"❌ Not found at: {pdftoppm_path}")

def check_conda_env():
    """Check conda environment and dependencies."""
    print("\n🔍 Checking Conda environment...")
    
    # Check if we're in a conda environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        print(f"✅ Conda environment: {conda_prefix}")
        
        # Check for poppler in conda env
        conda_poppler = os.path.join(conda_prefix, 'bin', 'pdftoppm')
        if os.path.exists(conda_poppler):
            print(f"✅ Conda poppler: {conda_poppler}")
        else:
            print(f"❌ Conda poppler not found at: {conda_poppler}")
            print("   Install with: conda install poppler")
    else:
        print("❌ Not in a conda environment")
        print("   Current Python:", sys.executable)

def check_pdf_file():
    """Check if the PDF file exists and is readable."""
    print("\n🔍 Checking PDF file...")
    
    # Check different possible PDF paths
    possible_paths = [
        'res/brief.pdf',
        '../res/brief.pdf',
        '../../res/brief.pdf',
        os.path.join(os.path.dirname(__file__), '..', 'res', 'brief.pdf')
    ]
    
    for pdf_path in possible_paths:
        abs_path = os.path.abspath(pdf_path)
        if os.path.exists(abs_path):
            print(f"✅ PDF found: {abs_path}")
            print(f"   Size: {os.path.getsize(abs_path)} bytes")
            print(f"   Readable: {os.access(abs_path, os.R_OK)}")
            return abs_path
        else:
            print(f"❌ PDF not found: {abs_path}")
    
    return None

def test_pdf_conversion(pdf_path):
    """Test PDF to image conversion."""
    if not pdf_path:
        print("\n❌ Cannot test PDF conversion - no PDF file found")
        return
    
    print(f"\n🔍 Testing PDF conversion with: {pdf_path}")
    
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image imported successfully")
        
        # Try conversion with different approaches
        try:
            print("🔄 Attempting PDF conversion...")
            images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)
            if images:
                print(f"✅ PDF conversion successful! Got {len(images)} page(s)")
                print(f"   Image size: {images[0].size}")
                print(f"   Image mode: {images[0].mode}")
            else:
                print("❌ PDF conversion returned no images")
        except Exception as e:
            print(f"❌ PDF conversion failed: {e}")
            print(f"   Exception type: {type(e).__name__}")
            
            # Try with explicit poppler path
            print("🔄 Trying with explicit poppler path...")
            try:
                # Try common poppler paths
                poppler_paths = [
                    '/opt/miniconda3/envs/moly/bin',
                    '/opt/homebrew/bin',
                    '/usr/local/bin',
                    '/usr/bin'
                ]
                
                for poppler_path in poppler_paths:
                    if os.path.exists(os.path.join(poppler_path, 'pdftoppm')):
                        print(f"🔄 Trying poppler path: {poppler_path}")
                        images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1, poppler_path=poppler_path)
                        if images:
                            print(f"✅ PDF conversion successful with poppler path: {poppler_path}")
                            break
                else:
                    print("❌ All poppler paths failed")
            except Exception as e2:
                print(f"❌ Explicit poppler path also failed: {e2}")
    
    except ImportError:
        print("❌ pdf2image not available for testing")

def provide_installation_instructions():
    """Provide platform-specific installation instructions."""
    print("\n📋 Installation Instructions")
    print("=" * 50)
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("For macOS:")
        print("1. Install poppler via Homebrew:")
        print("   brew install poppler")
        print("\n2. Install Python packages:")
        print("   pip install pdf2image PyPDF2 PyQt6-WebEngine")
        print("\n3. If using conda:")
        print("   conda install poppler")
        print("   pip install pdf2image")
    
    elif system == "Linux":
        print("For Linux (Ubuntu/Debian):")
        print("1. Install poppler-utils:")
        print("   sudo apt-get install poppler-utils")
        print("\n2. Install Python packages:")
        print("   pip install pdf2image PyPDF2 PyQt6-WebEngine")
        print("\n3. If using conda:")
        print("   conda install poppler")
        print("   pip install pdf2image")
    
    elif system == "Windows":
        print("For Windows:")
        print("1. Download poppler for Windows:")
        print("   https://github.com/oschwartz10612/poppler-windows/releases/")
        print("   Extract and add to PATH")
        print("\n2. Install Python packages:")
        print("   pip install pdf2image PyPDF2 PyQt6-WebEngine")
        print("\n3. If using conda:")
        print("   conda install poppler")
        print("   pip install pdf2image")

def main():
    """Run all diagnostic checks."""
    print("🔍 PDF Display Diagnostic Tool")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    check_python_packages()
    check_poppler()
    check_conda_env()
    pdf_path = check_pdf_file()
    test_pdf_conversion(pdf_path)
    provide_installation_instructions()
    
    print("\n✨ Diagnostic complete!")
    print("If images still don't show on the other computer, run this script there.")

if __name__ == "__main__":
    main()