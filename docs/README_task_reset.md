# Task Assignment Reset Script

This script allows you to reset the task assignment system for the Moly application.

## What it does

The script resets the task assignment system by:
- Clearing all participant assignments
- Resetting the rotation index to start from the beginning  
- Optionally creating a backup of current assignments before reset

## Usage

### Basic Usage
```bash
# Interactive reset with confirmation prompt
python reset_task_assignments.py

# Show current statistics only (no reset)
python reset_task_assignments.py --stats-only
```

### Advanced Usage
```bash
# Create backup before reset
python reset_task_assignments.py --backup

# Skip confirmation prompt (for automated use)
python reset_task_assignments.py --confirm

# Backup and auto-confirm
python reset_task_assignments.py --backup --confirm
```

## Command Line Options

- `--stats-only`: Only display current assignment statistics without performing reset
- `--backup`: Create a timestamped backup of current assignments before reset
- `--confirm`: Skip the confirmation prompt (useful for automated scripts)
- `--help`: Show detailed help message

## Safety Features

- **Confirmation prompt**: By default, asks for user confirmation before reset
- **Backup option**: Can create timestamped backups in `./backups/` directory
- **Statistics display**: Shows current assignments before reset
- **Error handling**: Graceful handling of missing files or permission errors

## File Structure

The script works with the `task_assignments.json` file which has this structure:

```json
{
  "task_rotation": ["mandala", "diary", "mindfulness"],
  "last_assigned_index": 0,
  "assignments": {
    "PARTICIPANT001": "mandala",
    "PARTICIPANT002": "diary"
  }
}
```

## Examples

### Check current status
```bash
python reset_task_assignments.py --stats-only
```

### Safe reset with backup
```bash
python reset_task_assignments.py --backup
```

### Quick reset for testing
```bash
python reset_task_assignments.py --confirm
```

## Output Example

```
🧘 Moly Task Assignment Reset Tool
========================================

📊 Current Assignment Status:
📊 Current Assignment Statistics:
   Total Participants: 4
   Mandala: 2 (50.0%)
   Diary: 1 (25.0%)  
   Mindfulness: 1 (25.0%)
🔄 Last assigned index: 0
🎯 Next assignment will be: diary (index 1)

👥 Recent Participants:
   TESTMA001: mandala
   TESTMA002: diary
   TESTMA003: mindfulness
   TESTMA004: mandala
```