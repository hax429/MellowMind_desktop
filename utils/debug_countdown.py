#!/usr/bin/env python3
"""
Debug script to check countdown values in logs.
"""

import json
import glob

def debug_countdown_values():
    """Debug countdown values in logs."""
    print("🔍 Debug: Countdown Values")
    print("=" * 40)
    
    # Find all action log files
    log_files = glob.glob("logs/*/actions_*.jsonl")
    
    for log_file in log_files:
        print(f"\n📄 Checking: {log_file}")
        
        countdown_values = []
        partial_text_entries = []
        
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                try:
                    entry = json.loads(line)
                    
                    if entry.get('action_type') == 'COUNTDOWN_STATE':
                        details = json.loads(entry.get('details', '{}'))
                        remaining = details.get('remaining_seconds', 0)
                        total = details.get('total_seconds', 0)
                        countdown_values.append({
                            'line': line_num,
                            'remaining': remaining,
                            'total': total,
                            'timestamp': entry['timestamp']['local']
                        })
                        
                    elif entry.get('action_type') == 'PARTIAL_TEXT_UPDATE':
                        details = entry.get('details', {})
                        remaining = details.get('countdown_remaining', 0)
                        partial_text_entries.append({
                            'line': line_num,
                            'remaining': remaining,
                            'text_length': details.get('text_length', 0),
                            'timestamp': entry['timestamp']['local']
                        })
                        
                except Exception as e:
                    print(f"   ❌ Error parsing line {line_num}: {e}")
        
        print(f"   📊 COUNTDOWN_STATE entries: {len(countdown_values)}")
        for cv in countdown_values[:3]:  # Show first 3
            print(f"      {cv['timestamp']}: {cv['remaining']}s remaining (total: {cv['total']}s)")
        
        print(f"   📝 PARTIAL_TEXT_UPDATE entries: {len(partial_text_entries)}")
        for pte in partial_text_entries[:3]:  # Show first 3
            print(f"      {pte['timestamp']}: {pte['remaining']}s remaining (text: {pte['text_length']} chars)")
        
        # Check for inconsistencies
        if countdown_values and partial_text_entries:
            expected_max = max([cv['total'] for cv in countdown_values])
            actual_max = max([pte['remaining'] for pte in partial_text_entries if pte['remaining']])
            
            if actual_max > expected_max * 10:  # If more than 10x expected
                print(f"   ⚠️ ISSUE: Partial text countdown values seem too high!")
                print(f"      Expected max: ~{expected_max}s")
                print(f"      Actual max: {actual_max}s")

if __name__ == '__main__':
    debug_countdown_values()
