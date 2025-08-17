#!/usr/bin/env python3

import json
import os
from config import TASK_ASSIGNMENTS_FILE


class TaskManager:
    """Manages task selection and assignment functionality."""
    
    def __init__(self, logging_manager):
        self.logging_manager = logging_manager
        self.selected_task = None
    
    def get_task_distribution_stats(self):
        """Get current task distribution statistics."""
        assignments_file = TASK_ASSIGNMENTS_FILE
        
        try:
            with open(assignments_file, 'r') as f:
                data = json.load(f)
            
            assignments = data.get("assignments", {})
            total_assignments = len(assignments)
            
            if total_assignments == 0:
                return {
                    "total_assignments": 0,
                    "mandala_count": 0,
                    "diary_count": 0,
                    "mindfulness_count": 0,
                    "mandala_percent": 0,
                    "diary_percent": 0,
                    "mindfulness_percent": 0
                }
            
            # Count each task type
            task_counts = {"mandala": 0, "diary": 0, "mindfulness": 0}
            for task in assignments.values():
                if task in task_counts:
                    task_counts[task] += 1
            
            # Calculate percentages
            stats = {
                "total_assignments": total_assignments,
                "mandala_count": task_counts["mandala"],
                "diary_count": task_counts["diary"],
                "mindfulness_count": task_counts["mindfulness"],
                "mandala_percent": round((task_counts["mandala"] / total_assignments) * 100, 1),
                "diary_percent": round((task_counts["diary"] / total_assignments) * 100, 1),
                "mindfulness_percent": round((task_counts["mindfulness"] / total_assignments) * 100, 1)
            }
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Error calculating task distribution: {e}")
            return {
                "total_assignments": 0,
                "mandala_count": 0,
                "diary_count": 0,
                "mindfulness_count": 0,
                "mandala_percent": 0,
                "diary_percent": 0,
                "mindfulness_percent": 0
            }
    
    def get_random_assigned_task(self, participant_id):
        """Get the next task in rotation for random assignment mode."""
        assignments_file = TASK_ASSIGNMENTS_FILE
        
        try:
            # Load current assignments
            with open(assignments_file, 'r') as f:
                data = json.load(f)
            
            # Get next task in rotation
            task_rotation = data["task_rotation"]
            last_index = data["last_assigned_index"]
            next_index = (last_index + 1) % len(task_rotation)
            assigned_task = task_rotation[next_index]
            
            # Update assignments
            data["last_assigned_index"] = next_index
            data["assignments"][participant_id] = assigned_task
            
            # Save updated assignments
            with open(assignments_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"🎯 System assigned task: {assigned_task} (rotation index: {next_index})")
            return assigned_task
            
        except Exception as e:
            print(f"⚠️ Error in task assignment: {e}")
            # Default to mandala if there's an error
            return "mandala"
    
    def save_user_task_selection(self, participant_id, task_name):
        """Save user's task selection to file."""
        assignments_file = TASK_ASSIGNMENTS_FILE
        
        try:
            # Load and update assignments file
            with open(assignments_file, 'r') as f:
                data = json.load(f)
            
            data["assignments"][participant_id] = task_name
            
            with open(assignments_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving task selection: {e}")
    
    def log_task_selection(self, task_name, participant_id, selection_mode):
        """Log detailed task selection information."""
        # Get updated stats
        updated_stats = self.get_task_distribution_stats()
        
        # Log detailed selection information
        self.logging_manager.log_action(
            "TASK_SELECTED", 
            f"User selected task: {task_name} | Participant: {participant_id} | Selection mode: {selection_mode}"
        )
        self.logging_manager.log_action(
            "TASK_DISTRIBUTION_AFTER_SELECTION", 
            f"After selection - Total: {updated_stats['total_assignments']}, "
            f"Mandala: {updated_stats['mandala_count']} ({updated_stats['mandala_percent']}%), "
            f"Diary: {updated_stats['diary_count']} ({updated_stats['diary_percent']}%), "
            f"Mindfulness: {updated_stats['mindfulness_count']} ({updated_stats['mindfulness_percent']}%)"
        )
    
    def log_task_assignment(self, task_name, participant_id, selection_mode):
        """Log task assignment for random assignment mode."""
        # Get current distribution stats and add to session info
        distribution_stats = self.get_task_distribution_stats()
        self.logging_manager.add_task_selection_to_session_info(task_name, selection_mode, distribution_stats)
        
        # Log the assignment
        self.logging_manager.log_action(
            "TASK_SELECTION_MODE", 
            f"Mode: {selection_mode} | Assigned task: {task_name}"
        )
        self.logging_manager.log_action(
            "TASK_ASSIGNED", 
            f"System assigned task: {task_name} | Participant: {participant_id}"
        )
    
    def log_task_to_perform(self, task_name, selection_mode):
        """Log the final task that will be performed."""
        task_descriptions = {
            "mandala": "drawing your figure",
            "diary": "journal down your mind", 
            "mindfulness": "watch a fun video"
        }
        
        description = task_descriptions.get(task_name, "unknown task")
        self.logging_manager.log_action(
            "TASK_TO_PERFORM", 
            f"Participant will perform: {task_name} ({description}) | Selection mode: {selection_mode}"
        )
    
    def set_selected_task(self, task_name):
        """Set the selected task."""
        self.selected_task = task_name
    
    def get_selected_task(self):
        """Get the selected task."""
        return self.selected_task