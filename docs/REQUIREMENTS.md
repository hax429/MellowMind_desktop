# MellowMind Requirements Documentation

## Python Dependencies

### Core Requirements
The MellowMind application requires the following Python packages:

```
opencv-python>=4.5.0
PyPDF2>=3.0.0
Pillow>=8.0.0
numpy>=1.20.0
```

### Detailed Package Information

#### opencv-python (cv2)
- **Purpose**: Video file processing and playback
- **Version**: >= 4.5.0
- **Usage**: Handles .mkv and .mov video files for relaxation and Stroop tasks
- **Install**: `pip install opencv-python`

#### PyPDF2
- **Purpose**: PDF content extraction for consent forms
- **Version**: >= 3.0.0
- **Usage**: Reads and displays consent documents
- **Install**: `pip install PyPDF2`

#### Pillow (PIL)
- **Purpose**: Image processing and icon generation
- **Version**: >= 8.0.0
- **Usage**: App icon creation and image manipulation
- **Install**: `pip install Pillow`

#### numpy
- **Purpose**: Numerical operations and data handling
- **Version**: >= 1.20.0
- **Usage**: Data processing for logging and statistics
- **Install**: `pip install numpy`

### Built-in Python Modules
The following modules are part of Python's standard library:
- `tkinter` - GUI framework
- `json` - Data serialization
- `os` - Operating system interface
- `datetime` - Date and time handling
- `threading` - Concurrent execution
- `logging` - Application logging

## Installation Methods

### Method 1: Using requirements.txt
```bash
pip install -r requirements.txt
```

### Method 2: Manual Installation
```bash
pip install opencv-python PyPDF2 Pillow numpy
```

### Method 3: Conda Environment
```bash
conda create -n moly python=3.9
conda activate moly
pip install opencv-python PyPDF2 Pillow numpy
```

## Platform-Specific Requirements

### macOS
- **System**: macOS 10.10 or later
- **Python**: 3.7+ (Homebrew or official installer)
- **Additional**: Xcode Command Line Tools may be required
```bash
xcode-select --install
```

### Windows
- **System**: Windows 10/11
- **Python**: 3.7+ from python.org
- **Additional**: Microsoft Visual C++ Redistributable
- **Note**: Some video codecs may require additional setup

### Linux (Ubuntu/Debian)
- **System**: Ubuntu 18.04+ or equivalent
- **Python**: 3.7+ (`python3-dev` package recommended)
- **Additional packages**:
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-tk
sudo apt-get install libgtk-3-dev  # For GUI support
```

## Optional Dependencies

### For Enhanced Video Support
```bash
pip install opencv-contrib-python  # Additional codecs
```

### For Development
```bash
pip install pylint black pytest  # Code quality tools
```

### For Advanced Logging
```bash
pip install psutil  # System monitoring
```

## Version Compatibility

### Python Version Support
- **Minimum**: Python 3.7
- **Recommended**: Python 3.9 or 3.10
- **Maximum tested**: Python 3.11

### Operating System Compatibility
- **Primary**: macOS (developed and tested)
- **Secondary**: Windows 10/11 (basic testing)
- **Experimental**: Linux distributions

## Troubleshooting Dependencies

### Common Issues

#### OpenCV Installation Problems
```bash
# If opencv-python fails to install
pip uninstall opencv-python
pip install --no-cache-dir opencv-python

# Alternative: use conda
conda install -c conda-forge opencv
```

#### PyPDF2 Version Conflicts
```bash
# If PyPDF2 has issues
pip uninstall PyPDF2
pip install PyPDF2==3.0.1
```

#### Tkinter Missing (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

### Verification Commands
Test that all dependencies are working:

```python
# Test script to verify dependencies
import tkinter as tk
import cv2
import PyPDF2
import PIL
import numpy as np

print("✅ All dependencies imported successfully!")
print(f"OpenCV version: {cv2.__version__}")
print(f"PyPDF2 version: {PyPDF2.__version__}")
print(f"Pillow version: {PIL.__version__}")
print(f"NumPy version: {np.__version__}")
```

## Security Considerations

### Package Sources
- Install packages from trusted sources (PyPI)
- Use virtual environments to isolate dependencies
- Regularly update packages for security patches

### Known Vulnerabilities
Check for known vulnerabilities:
```bash
pip audit  # Check for known security issues
```

## Development Environment

### Recommended Setup
```bash
# Create virtual environment
python3 -m venv mellowmind_env
source mellowmind_env/bin/activate  # On Windows: mellowmind_env\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pylint black pytest

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### IDE Configuration
- **Recommended**: VS Code with Python extension
- **Alternative**: PyCharm Community Edition
- **Minimal**: Any text editor with Python syntax highlighting

## Performance Considerations

### Memory Usage
- Base application: ~50-100MB RAM
- With video playback: +200-500MB RAM
- Log files grow over time (plan for storage)

### CPU Requirements
- Minimal for basic operation
- Video decoding requires moderate CPU
- Multiple concurrent sessions may need more resources

## Deployment Checklist

Before deploying to research computers:

- [ ] Test all dependencies install correctly
- [ ] Verify video files play without issues
- [ ] Confirm PDF consent forms display properly
- [ ] Test task assignment functionality
- [ ] Validate logging works correctly
- [ ] Check file permissions are correct
- [ ] Ensure data storage paths are accessible
- [ ] Test crash recovery functionality
- [ ] Verify all GUI elements display properly
- [ ] Confirm audio notifications work