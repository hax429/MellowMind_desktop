# MellowMind Desktop Application

🧘 **A comprehensive desktop application for psychological research studies involving stress response and relaxation tasks.**

## Overview

MellowMind is a specialized research tool designed for conducting psychological studies that examine stress responses, cognitive performance, and relaxation effectiveness. The application provides a structured environment for participants to complete various tasks while comprehensive data logging captures their interactions and responses.

## Features

### ✨ Core Functionality
- **Descriptive Writing Tasks** - Guided prompts for mindfulness and self-reflection
- **Stroop Test Integration** - Color-word interference testing with video content
- **Mental Arithmetic Tasks** - Counting backwards from configurable starting numbers
- **Relaxation Sessions** - Video-guided relaxation with automatic progression
- **Consent Management** - PDF-based consent forms with scroll-to-bottom verification

### 📊 Data Collection
- **Comprehensive Logging** - JSON-formatted logs with millisecond precision
- **Session Recovery** - Automatic crash detection and participant state restoration
- **Task Assignment** - Randomized or self-selection task distribution
- **Real-time Monitoring** - Live word counts, timing, and interaction tracking

### 🎨 User Experience
- **Fullscreen Interface** - Distraction-free research environment
- **Customizable Timers** - Flexible countdown durations for all tasks
- **Visual Feedback** - Color-coded progress indicators and status displays
- **Cross-platform** - Primary support for macOS, secondary for Windows/Linux

## Quick Start

### 1. Installation
```bash
# Clone or download the repository
cd MellowMind_desktop

# Install dependencies
pip install -r requirements.txt

# Make launcher executable (macOS/Linux)
chmod +x start_mellowmind.sh
```

### 2. Launch Application
```bash
# Option 1: Using launcher script
./start_mellowmind.sh

# Option 2: Direct Python execution  
python src/app.py

# Option 3: Using app bundle (macOS)
open MellowMind.app
```

### 3. First Run Setup
1. Enter participant ID
2. Complete consent form (scroll to bottom)
3. Follow on-screen instructions for each task
4. Data automatically saved to `logs/` directory

## Project Structure

```
MellowMind_desktop/
├── src/                    # Core application code
│   ├── app.py             # Main application entry point
│   ├── config.py          # Configuration settings
│   ├── video_manager.py   # Video playback management
│   ├── countdown_manager.py # Timer functionality
│   ├── logging_manager.py # Session data logging
│   ├── recovery_manager.py # Crash recovery system
│   └── task_manager.py    # Task assignment logic
├── res/                   # Resource files
│   ├── brief.pdf         # Consent form document
│   ├── screen.mkv        # Relaxation video
│   ├── stroop.mov        # Stroop test video
│   └── beep.m4a         # Audio notifications
├── docs/                  # Documentation
│   ├── SETUP.md          # Detailed setup instructions
│   ├── REQUIREMENTS.md   # Dependency documentation
│   └── UTILITIES.md      # Utility scripts guide
├── utils/                 # Utility scripts and tools
│   ├── analyze_logs.py   # Log analysis tools
│   ├── reset_task_assignments.py # Task management
│   └── debug_*.py        # Development/testing tools
├── logs/                  # Session data (auto-created)
├── MellowMind.app/       # macOS app bundle
└── task_assignments.json # Participant task tracking
```

## Configuration

### Key Settings (src/config.py)
```python
# Task Durations
DESCRIPTIVE_COUNTDOWN_MINUTES = 5
STROOP_COUNTDOWN_MINUTES = 3
MATH_COUNTDOWN_MINUTES = 2

# Task Assignment Mode
TASK_SELECTION_MODE = "random_assigned"  # or "self_selection"

# Interface Settings
DEVELOPER_MODE = False  # Hide debug information for participants
FOCUS_MODE = True      # Keep window always on top
```

### Video Files
- Place video files in `res/` directory
- Supported formats: .mkv, .mov, .mp4, .avi
- Ensure files are accessible and not corrupted

### Consent Forms
- PDF files placed in `res/brief.pdf`
- Automatically extracted and displayed
- Scroll-to-bottom requirement enforced

## Data Output

### Log Files (logs/{participant_id}/)
- **session_info.json** - Session metadata and configuration
- **actions.jsonl** - All user interactions and system events
- **descriptive_responses.jsonl** - Task response data with timing
- **tech_log.jsonl** - Technical events and debugging information

### Task Assignment Tracking
- **task_assignments.json** - Participant task distribution and rotation

## Research Applications

### Study Types
- **Stress Response Studies** - Pre/post relaxation measurement
- **Cognitive Performance** - Attention and interference testing
- **Mindfulness Research** - Descriptive writing effectiveness
- **Technology Acceptance** - Digital intervention usability

### Data Analysis
- Timing precision to millisecond level
- Complete interaction history
- Task completion rates and patterns
- Session recovery and continuation tracking

## Development

### Prerequisites
- Python 3.7+
- OpenCV (cv2) for video processing
- PyPDF2 for consent form handling
- Tkinter for GUI (usually included)

### Testing
```bash
# Run utility tests
python utils/test_recovery.py
python utils/debug_countdown.py

# Simulate scenarios
python utils/simulate_crash.py
```

### Customization
- Modify `src/config.py` for study-specific settings
- Update video content in `res/` directory
- Customize consent forms by replacing `res/brief.pdf`
- Adjust UI colors and fonts in configuration

## Deployment

### Research Computer Setup
1. Install Python 3.7+ and dependencies
2. Copy application files to target machine
3. Configure paths and settings in `config.py`
4. Test all functionality before participant sessions
5. Create desktop shortcuts for easy access

### Data Management
- Plan storage space for log files (grows over time)
- Implement regular backup procedures
- Ensure data privacy and security measures
- Consider automated data export workflows

## Troubleshooting

### Common Issues
- **Video not playing**: Check codecs and file formats
- **PDF not displaying**: Verify PyPDF2 installation and file path
- **Timing issues**: Ensure system performance adequate
- **Crash recovery**: Check log file permissions and paths

### Support Resources
- 📖 [Detailed Setup Guide](docs/SETUP.md)
- 🔧 [Requirements Documentation](docs/REQUIREMENTS.md)
- 🛠️ [Utilities Guide](docs/UTILITIES.md)
- 📊 [Log Analysis Tools](utils/analyze_logs.py)

## Contributing

### Development Guidelines
- Follow existing code structure and patterns
- Test thoroughly before committing changes
- Document new features and configuration options
- Maintain backwards compatibility with existing data

### Research Collaboration
- Share configuration templates for different study types
- Contribute video content appropriate for research use
- Report bugs and suggest improvements
- Document study protocols and methodologies

## License and Ethics

### Research Use
This application is designed for legitimate psychological and behavioral research. Users are responsible for:
- Obtaining appropriate ethical approval
- Ensuring participant consent and data privacy
- Following institutional data protection policies
- Maintaining participant confidentiality

### Data Responsibility
- All session data contains potentially sensitive information
- Implement appropriate security measures for data storage
- Regular cleanup of test and development data
- Secure data transmission for multi-site studies

## Version History

### Current Features
- ✅ Comprehensive task suite (descriptive, Stroop, arithmetic)
- ✅ Video-guided relaxation sessions
- ✅ PDF consent form integration
- ✅ Automatic crash recovery system
- ✅ Task assignment and randomization
- ✅ Detailed session logging
- ✅ Cross-platform compatibility

### Planned Enhancements
- 🔄 Web-based administration interface
- 🔄 Advanced statistical analysis tools
- 🔄 Multi-language support
- 🔄 Enhanced video content library
- 🔄 Cloud data synchronization

---

## Quick Reference

### Essential Commands
```bash
# Launch application
./utils/start_mellowmind.sh

# Analyze participant data
python utils/analyze_logs.py --participant ID

# Reset task assignments
python utils/reset_task_assignments.py --backup

# Create desktop shortcut
./utils/create_desktop_shortcut.sh
```

### Important Files
- `src/app.py` - Main application
- `src/config.py` - All settings
- `task_assignments.json` - Participant tracking
- `logs/` - Session data output

### Support
For technical issues or research collaboration inquiries, please refer to the documentation in the `docs/` directory or review the utility scripts in `utils/` for troubleshooting tools.

🧘 **Happy researching with MellowMind!**