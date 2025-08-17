# MellowMind Desktop Setup Guide

## Overview
MellowMind is a desktop application for conducting psychological research studies involving stress response and relaxation tasks. The application includes descriptive writing tasks, Stroop tests, mental arithmetic, and relaxation periods with video content.

## System Requirements

### Operating System
- macOS 10.10 or later
- Windows 10/11 (with some modifications)
- Linux (Ubuntu 18.04+ recommended)

### Python Requirements
- Python 3.7 or later
- Conda environment recommended (specifically `moly` environment)

### Hardware Requirements
- Minimum 4GB RAM
- 1GB free disk space
- Audio output capability
- Display resolution: 1024x768 minimum (1920x1080 recommended)
- Webcam/microphone (optional, for some research configurations)

## Installation

### 1. Environment Setup

#### Option A: Using Conda (Recommended)
```bash
# Create the moly environment
conda create -n moly python=3.9

# Activate the environment
conda activate moly

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using System Python
```bash
# Install dependencies directly
pip3 install -r requirements.txt
```

### 2. Dependencies Installation

The application requires the following Python packages:
- `tkinter` (usually included with Python)
- `opencv-python` (cv2) - for video processing
- `PyPDF2` - for PDF content display in consent screen
- `Pillow` (PIL) - for image processing
- `numpy` - for data processing

Install all dependencies:
```bash
pip install opencv-python PyPDF2 Pillow numpy
```

### 3. Application Files Setup

Ensure the following directory structure:
```
MellowMind_desktop/
├── src/
│   ├── app.py              # Main application
│   ├── config.py           # Configuration settings
│   ├── video_manager.py    # Video playback management
│   ├── countdown_manager.py # Timer functionality
│   ├── logging_manager.py  # Session logging
│   ├── recovery_manager.py # Crash recovery
│   └── task_manager.py     # Task assignment
├── res/
│   ├── brief.pdf          # Consent form PDF
│   ├── screen.mkv         # Relaxation video
│   ├── stroop.mov         # Stroop test video
│   └── beep.m4a          # Audio notification
├── logs/                  # Session logs (auto-created)
├── docs/                  # Documentation
└── utils/                 # Utility scripts
```

### 4. Configuration

Edit `src/config.py` to customize:
- Task durations
- Video file paths
- Logging settings
- UI colors and fonts
- Consent screen settings

Key settings to verify:
```python
# Paths (should use relative paths)
RELAXATION_VIDEO_PATH = os.path.join("res", "screen.mkv")
STROOP_VIDEO_PATH = os.path.join("res", "stroop.mov")
CONSENT_PDF_PATH = os.path.join("res", "brief.pdf")

# Task durations (in minutes)
DESCRIPTIVE_COUNTDOWN_MINUTES = 5
STROOP_COUNTDOWN_MINUTES = 3
MATH_COUNTDOWN_MINUTES = 2
```

## Running the Application

### Method 1: Using App Bundle (macOS)
1. Double-click `MellowMind.app` on desktop or in Finder
2. The application will launch automatically

### Method 2: Using Shell Script
```bash
./start_mellowmind.sh
```

### Method 3: Direct Python Execution
```bash
# From project root
python3 src/app.py

# Or with conda
conda activate moly
python src/app.py
```

## First Time Setup

### 1. Create Desktop Shortcut (macOS)
```bash
./create_desktop_shortcut.sh
```

### 2. Test Video Files
Ensure all video files play correctly:
- `res/screen.mkv` - Relaxation video
- `res/stroop.mov` - Stroop test video

### 3. Verify PDF Display
Check that `res/brief.pdf` displays properly in the consent screen.

### 4. Test Task Assignment
The application uses `task_assignments.json` to track participant task assignments. This file is auto-created on first run.

## Troubleshooting

### Video Not Playing
- Install additional codecs: `pip install opencv-contrib-python`
- Check video file formats are supported by OpenCV
- Verify file paths in `config.py`

### PDF Not Displaying
- Ensure PyPDF2 is installed: `pip install PyPDF2`
- Check PDF file is not corrupted
- Verify PDF path in `config.py`

### Permission Issues (macOS)
```bash
# Make scripts executable
chmod +x start_mellowmind.sh
chmod +x create_desktop_shortcut.sh
chmod +x MellowMind.app/Contents/MacOS/MellowMind
```

### Python Environment Issues
```bash
# Check Python version
python3 --version

# Check installed packages
pip list

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Audio Issues
- Check system audio settings
- Verify `res/beep.m4a` file exists
- Test with different audio files if needed

## Research Configuration

### Task Selection Mode
Set in `config.py`:
```python
# Options: "self_selection" or "random_assigned"
TASK_SELECTION_MODE = "random_assigned"
```

### Logging Configuration
```python
DESCRIPTIVE_LINE_LOGGING = True  # Log sentences on period
COUNTDOWN_ENABLED = True         # Enable countdown timers
```

### Developer Mode
```python
DEVELOPER_MODE = True   # Show debug information
FOCUS_MODE = True      # Keep window always on top
```

## Data Collection

### Log Files Location
Session data is automatically saved to:
```
logs/{participant_id}/
├── session_info_{timestamp}.json          # Session metadata
├── actions_{timestamp}.jsonl              # User actions
├── descriptive_responses_{timestamp}.jsonl # Task responses
└── tech_log_{timestamp}.jsonl             # Technical events
```

### Task Assignment Tracking
Participant task assignments are stored in:
```
task_assignments.json
```

## Security Considerations

- Ensure participant data confidentiality
- Regularly backup log files
- Use participant IDs, not real names
- Store sensitive data on encrypted drives
- Follow institutional data protection policies

## Support

For technical issues:
1. Check log files in `logs/` directory for error messages
2. Verify all dependencies are installed
3. Test with a clean Python environment
4. Check file permissions and paths
5. Review configuration settings in `config.py`