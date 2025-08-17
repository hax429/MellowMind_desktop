# MellowMind Utilities Documentation

## Overview
This document describes the utility scripts and tools available in the MellowMind desktop application.

## Utility Scripts Location
All utility scripts are located in the `utils/` directory:

```
utils/
├── analyze_logs.py           # Log analysis and reporting
├── create_partial_session.py # Session state simulation
├── debug_countdown.py        # Countdown timer debugging
├── debug_recovery.py         # Crash recovery testing
├── reset_task_assignments.py # Task assignment reset tool
├── simulate_crash.py         # Crash simulation for testing
├── test_recovery.py          # Recovery system testing
├── create_icon.py           # App icon generation
├── create_desktop_shortcut.sh # Desktop shortcut creation
└── start_mellowmind.sh      # Application launcher
```

## Log Analysis Tools

### analyze_logs.py
Comprehensive log analysis tool for research data processing.

**Usage:**
```bash
python utils/analyze_logs.py --participant MA001
python utils/analyze_logs.py --stats-only
python utils/analyze_logs.py --export-csv
```

**Features:**
- Session overview and statistics
- Action frequency analysis
- Response time calculations
- Screen transition tracking
- Export to CSV/Excel formats

**Command line options:**
- `--participant ID` - Analyze specific participant
- `--stats-only` - Show statistics without detailed data
- `--export-csv` - Export results to CSV
- `--date-range` - Filter by date range
- `--output-dir` - Specify output directory

## Development and Testing Tools

### debug_countdown.py
Debug countdown timer functionality and timing accuracy.

**Usage:**
```bash
python utils/debug_countdown.py
```

**Features:**
- Timer accuracy testing
- Countdown callback verification
- Performance monitoring
- Memory usage tracking

### debug_recovery.py
Test and debug the crash recovery system.

**Usage:**
```bash
python utils/debug_recovery.py --test-recovery
python utils/debug_recovery.py --create-incomplete
```

**Features:**
- Simulate incomplete sessions
- Test recovery logic
- Validate state restoration
- Check data integrity

### simulate_crash.py
Simulate application crashes for testing recovery functionality.

**Usage:**
```bash
python utils/simulate_crash.py --stage descriptive
python utils/simulate_crash.py --random
```

**Features:**
- Controlled crash simulation
- Different crash scenarios
- Recovery testing automation
- Log file validation

### test_recovery.py
Automated testing suite for crash recovery system.

**Usage:**
```bash
python utils/test_recovery.py --run-all
python utils/test_recovery.py --test-descriptive
```

**Features:**
- Automated recovery testing
- Multiple scenario validation
- Performance benchmarking
- Report generation

## Data Management Tools

### reset_task_assignments.py
Reset and manage task assignment system.

**Usage:**
```bash
python utils/reset_task_assignments.py
python utils/reset_task_assignments.py --backup
python utils/reset_task_assignments.py --stats-only
```

**Features:**
- Clear all task assignments
- Create backup before reset
- Display current statistics
- Task distribution analysis

**Command line options:**
- `--backup` - Create timestamped backup
- `--confirm` - Skip confirmation prompt
- `--stats-only` - Show stats without reset

### create_partial_session.py
Create partial session data for testing purposes.

**Usage:**
```bash
python utils/create_partial_session.py --participant TEST001
python utils/create_partial_session.py --stage stroop
```

**Features:**
- Generate test session data
- Simulate different completion stages
- Create realistic log entries
- Test data validation

## Installation and Deployment Tools

### create_icon.py
Generate application icons for different platforms.

**Usage:**
```bash
python utils/create_icon.py
```

**Features:**
- PNG icon generation
- macOS ICNS format support
- Multiple resolution creation
- Custom design elements

**Requirements:**
- PIL/Pillow for image generation
- Optional: ImageMagick for advanced formats

### create_desktop_shortcut.sh (macOS)
Create desktop shortcuts for easy application access.

**Usage:**
```bash
./utils/create_desktop_shortcut.sh
```

**Features:**
- Symbolic link creation
- Icon assignment
- Permission setting
- Validation checks

### start_mellowmind.sh
Application launcher script with environment detection.

**Usage:**
```bash
./utils/start_mellowmind.sh
```

**Features:**
- Python environment detection
- Conda environment support
- Dependency checking
- Error reporting
- Automatic path resolution

## Configuration and Maintenance

### Log File Management
```bash
# Archive old logs
mkdir -p archive/logs_$(date +%Y%m%d)
mv logs/* archive/logs_$(date +%Y%m%d)/

# Clean up temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete
```

### Backup Scripts
```bash
# Backup configuration and data
tar -czf backup_$(date +%Y%m%d).tar.gz \
    src/ res/ task_assignments.json logs/

# Backup task assignments only
cp task_assignments.json backups/task_assignments_$(date +%Y%m%d).json
```

## Performance Monitoring

### System Resource Usage
```python
# Monitor memory usage during sessions
import psutil
import time

def monitor_resources():
    process = psutil.Process()
    while True:
        memory = process.memory_info().rss / 1024 / 1024  # MB
        cpu = process.cpu_percent()
        print(f"Memory: {memory:.1f}MB, CPU: {cpu:.1f}%")
        time.sleep(5)
```

### Log File Size Monitoring
```bash
# Check log file sizes
du -sh logs/*/
du -h logs/*/*.jsonl | sort -rh | head -10
```

## Troubleshooting Tools

### Dependency Checker
```python
# Check all required dependencies
import importlib
import sys

dependencies = ['tkinter', 'cv2', 'PyPDF2', 'PIL', 'numpy']
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep} - Missing")
```

### Video File Validator
```python
# Validate video files
import cv2
import os

video_files = ['res/screen.mkv', 'res/stroop.mov']
for video in video_files:
    if os.path.exists(video):
        cap = cv2.VideoCapture(video)
        if cap.isOpened():
            print(f"✅ {video}")
            cap.release()
        else:
            print(f"❌ {video} - Cannot open")
    else:
        print(f"❌ {video} - File not found")
```

## Best Practices

### Utility Script Usage
1. Always run utilities from the project root directory
2. Use virtual environments for testing
3. Backup data before running destructive operations
4. Check script permissions before execution
5. Review output logs for errors or warnings

### Development Workflow
1. Use debug tools during development
2. Test recovery scenarios regularly
3. Monitor performance with analysis tools
4. Validate data integrity frequently
5. Keep utility scripts updated

### Data Management
1. Regular log analysis for insights
2. Periodic task assignment cleanup
3. Automated backup procedures
4. Performance monitoring
5. Storage space management

## Security Considerations

### Script Permissions
```bash
# Set appropriate permissions
chmod 755 utils/*.sh
chmod 644 utils/*.py
```

### Data Privacy
- Ensure log analysis tools anonymize data
- Use participant IDs, never real names
- Secure backup storage locations
- Regular cleanup of temporary files

### Access Control
- Limit utility script access to authorized users
- Use version control for script changes
- Document all utility modifications
- Test scripts in isolated environments