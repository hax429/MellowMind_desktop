#!/usr/bin/env python3
"""
Task Assignment Reset Script for Moly Application

This script resets the task assignment system by:
1. Clearing all participant assignments
2. Resetting the rotation index to start from the beginning
3. Optionally backing up the current assignments before reset

Usage:
    python reset_task_assignments.py [--backup] [--confirm]
    
Options:
    --backup    Create a backup of current assignments before reset
    --confirm   Skip the confirmation prompt (for automated use)
"""

import json
import os
import argparse
import shutil
from datetime import datetime

# Configuration
ASSIGNMENTS_FILE = "/Users/hax429/Developer/Internship/moly/task_assignments.json"
BACKUP_DIR = "/Users/hax429/Developer/Internship/moly/backups"

def create_backup(assignments_file, backup_dir):
    """Create a timestamped backup of the current assignments file."""
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"task_assignments_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the assignments file to backup location
        shutil.copy2(assignments_file, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def reset_assignments(assignments_file):
    """Reset the task assignments to initial state."""
    try:
        # Load current assignments
        with open(assignments_file, 'r') as f:
            data = json.load(f)
        
        # Store current stats for reporting
        current_assignments = data.get("assignments", {})
        total_before = len(current_assignments)
        
        # Count task types before reset
        task_counts = {"mandala": 0, "diary": 0, "mindfulness": 0}
        for task in current_assignments.values():
            if task in task_counts:
                task_counts[task] += 1
        
        # Reset the assignments
        data["assignments"] = {}
        data["last_assigned_index"] = -1  # Will be incremented to 0 on first assignment
        
        # Ensure task_rotation exists with default values
        if "task_rotation" not in data:
            data["task_rotation"] = ["mandala", "diary", "mindfulness"]
        
        # Save the reset assignments
        with open(assignments_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Task assignments reset successfully!")
        print(f"📊 Cleared {total_before} participant assignments:")
        print(f"   - Mandala: {task_counts['mandala']}")
        print(f"   - Diary: {task_counts['diary']}")
        print(f"   - Mindfulness: {task_counts['mindfulness']}")
        print(f"🔄 Rotation index reset to -1 (next assignment will be index 0)")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Assignments file not found: {assignments_file}")
        print("Creating new assignments file with default structure...")
        
        # Create new file with default structure
        default_data = {
            "task_rotation": ["mandala", "diary", "mindfulness"],
            "last_assigned_index": -1,
            "assignments": {}
        }
        
        try:
            with open(assignments_file, 'w') as f:
                json.dump(default_data, f, indent=2)
            print("✅ New assignments file created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating new assignments file: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error resetting assignments: {e}")
        return False

def show_current_stats(assignments_file):
    """Display current assignment statistics."""
    try:
        with open(assignments_file, 'r') as f:
            data = json.load(f)
        
        assignments = data.get("assignments", {})
        total = len(assignments)
        last_index = data.get("last_assigned_index", -1)
        task_rotation = data.get("task_rotation", ["mandala", "diary", "mindfulness"])
        
        if total == 0:
            print("📊 Current Status: No participant assignments")
            print(f"🔄 Next assignment will be: {task_rotation[0]} (index 0)")
            return
        
        # Count task types
        task_counts = {"mandala": 0, "diary": 0, "mindfulness": 0}
        for task in assignments.values():
            if task in task_counts:
                task_counts[task] += 1
        
        print(f"📊 Current Assignment Statistics:")
        print(f"   Total Participants: {total}")
        print(f"   Mandala: {task_counts['mandala']} ({task_counts['mandala']/total*100:.1f}%)")
        print(f"   Diary: {task_counts['diary']} ({task_counts['diary']/total*100:.1f}%)")
        print(f"   Mindfulness: {task_counts['mindfulness']} ({task_counts['mindfulness']/total*100:.1f}%)")
        print(f"🔄 Last assigned index: {last_index}")
        
        if last_index >= 0 and last_index < len(task_rotation):
            next_index = (last_index + 1) % len(task_rotation)
            print(f"🎯 Next assignment will be: {task_rotation[next_index]} (index {next_index})")
        
        print(f"\n👥 Recent Participants:")
        recent_assignments = list(assignments.items())[-5:]  # Show last 5
        for participant_id, task in recent_assignments:
            print(f"   {participant_id}: {task}")
        
        if len(assignments) > 5:
            print(f"   ... and {len(assignments) - 5} more")
    
    except FileNotFoundError:
        print(f"📊 No assignments file found at {assignments_file}")
    except Exception as e:
        print(f"❌ Error reading current stats: {e}")

def main():
    """Main function to handle command line arguments and execute reset."""
    parser = argparse.ArgumentParser(
        description="Reset task assignments for Moly application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reset_task_assignments.py                 # Interactive reset with confirmation
  python reset_task_assignments.py --backup       # Create backup before reset
  python reset_task_assignments.py --confirm      # Skip confirmation prompt
  python reset_task_assignments.py --backup --confirm  # Backup and auto-confirm
        """
    )
    
    parser.add_argument('--backup', action='store_true',
                       help='Create a backup before resetting')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show current statistics without resetting')
    
    args = parser.parse_args()
    
    print("🧘 Moly Task Assignment Reset Tool")
    print("=" * 40)
    
    # Show current statistics
    print("\n📊 Current Assignment Status:")
    show_current_stats(ASSIGNMENTS_FILE)
    
    # If only showing stats, exit here
    if args.stats_only:
        return
    
    print("\n" + "=" * 40)
    
    # Get confirmation unless --confirm flag is used
    if not args.confirm:
        print("⚠️  WARNING: This will reset ALL task assignments!")
        print("   - All participant assignments will be cleared")
        print("   - Rotation index will be reset to start from beginning")
        
        if args.backup:
            print("   - A backup will be created before reset")
        
        confirm = input("\nAre you sure you want to proceed? (yes/no): ").lower().strip()
        if confirm not in ['yes', 'y']:
            print("❌ Reset cancelled by user")
            return
    
    # Create backup if requested
    backup_path = None
    if args.backup:
        print("\n📋 Creating backup...")
        backup_path = create_backup(ASSIGNMENTS_FILE, BACKUP_DIR)
        if not backup_path:
            print("❌ Backup failed. Aborting reset for safety.")
            return
    
    # Perform the reset
    print("\n🔄 Resetting task assignments...")
    success = reset_assignments(ASSIGNMENTS_FILE)
    
    if success:
        print("\n✅ Reset completed successfully!")
        if backup_path:
            print(f"💾 Backup available at: {backup_path}")
        print("\n🎯 Ready for new participant assignments")
    else:
        print("\n❌ Reset failed!")
        if backup_path:
            print(f"💾 Your data is safe in backup: {backup_path}")

if __name__ == "__main__":
    main()