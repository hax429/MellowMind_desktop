#!/usr/bin/env python3
"""
Script to simulate a crash for testing the Moly crash recovery system.
This script will start the app, let it run for a bit, then forcefully terminate it.
"""

import subprocess
import time
import signal
import os
import sys

def simulate_crash():
    """Simulate a crash by starting the app and then killing it."""
    
    print("🧪 Moly Crash Simulation Script")
    print("=" * 50)
     
    # Check if we're in the right directory
    # if not os.path.exists("moly_app.py"):
    #     print("❌ Error: moly_app.py not found in current directory")
    #     print("   Please run this script from the moly project directory")
    #     return
    
    # Start the Moly application
    print("🚀 Starting Moly application..k..")
    try:
        # Start the app in the background
        process = subprocess.Popen([
            "/opt/miniconda3/envs/moly/bin/python", 
            "/Users/hax429/Developer/Internship/MellowMind_desktop/src/app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"📱 App started with PID: {process.pid}")
        print("⏰ Letting app run for 20 seconds...")
        
        # Let it run for a bit
        time.sleep(20)
        
        # Check if process is still running
        if process.poll() is None:
            print("💥 Simulating crash by forcefully terminating the process...")
            
            # Forcefully terminate (simulate crash)
            process.terminate()
            time.sleep(2)
            
            # If it's still running, kill it harder
            if process.poll() is None:
                process.kill()
                time.sleep(1)
            
            print(f"💀 Process {process.pid} terminated (crash simulated)")
            
            # Check for incomplete sessions
            print("\n🔍 Checking for incomplete sessions...")
            check_incomplete_sessions()
            
            print("\n✅ Crash simulation complete!")
            print("💡 Now run 'python moly_app.py' to test the recovery system")
            
        else:
            print("❌ App exited before we could simulate a crash")
            stdout, stderr = process.communicate()
            if stdout:
                print("STDOUT:", stdout.decode())
            if stderr:
                print("STDERR:", stderr.decode())
    
    except Exception as e:
        print(f"❌ Error simulating crash: {e}")

def check_incomplete_sessions():
    """Check for incomplete sessions in the logs directory."""
    import json
    import glob
    
    if not os.path.exists("logs"):
        print("   No logs directory found")
        return
    
    incomplete_found = False
    
    for participant_dir in os.listdir("logs"):
        participant_path = os.path.join("logs", participant_dir)
        if not os.path.isdir(participant_path):
            continue
        
        # Check session files
        session_files = glob.glob(os.path.join(participant_path, "session_info_*.json"))
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_info = json.load(f)
                
                # Check if session is incomplete (no end time)
                if 'session_end_time' not in session_info:
                    print(f"   📋 Found incomplete session: {participant_dir}")
                    print(f"      Started: {session_info.get('session_start_time', {}).get('local', 'Unknown')}")
                    print(f"      File: {session_file}")
                    incomplete_found = True
                    
            except Exception as e:
                print(f"   ⚠️ Error reading {session_file}: {e}")
    
    if not incomplete_found:
        print("   No incomplete sessions found")

def interactive_crash_simulation():
    """Interactive crash simulation with options."""
    print("🧪 Interactive Crash Simulation")
    print("=" * 40)
    print()
    print("Options:")
    print("1. Quick crash (5 seconds)")
    print("2. Medium crash (15 seconds)")
    print("3. Long crash (30 seconds)")
    print("4. Custom timing")
    print("5. List current incomplete sessions")
    print("6. Clean up test sessions")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == '1':
        run_timed_crash(5)
    elif choice == '2':
        run_timed_crash(15)
    elif choice == '3':
        run_timed_crash(30)
    elif choice == '4':
        try:
            seconds = int(input("Enter seconds to run before crash: "))
            run_timed_crash(seconds)
        except ValueError:
            print("❌ Invalid number")
    elif choice == '5':
        check_incomplete_sessions()
    elif choice == '6':
        cleanup_test_sessions()
    else:
        print("❌ Invalid choice")

def run_timed_crash(seconds):
    """Run the app for specified seconds then crash it."""
    print(f"🚀 Starting app for {seconds} seconds before crash...")
    
    try:
        # Start the app
        process = subprocess.Popen([
            "/opt/miniconda3/envs/moly/bin/python", 
            "moly_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"📱 App started with PID: {process.pid}")
        print(f"⏰ Waiting {seconds} seconds...")
        
        # Wait for specified time
        time.sleep(seconds)
        
        # Crash it
        if process.poll() is None:
            print("💥 Crashing now...")
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
            print("💀 Process crashed successfully")
        else:
            print("❌ App already exited")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def cleanup_test_sessions():
    """Clean up test sessions."""
    import shutil
    
    test_participants = ['TEST001', 'TEST002', 'TEST003', 'CRASH001', 'CRASH002', 'RECOVERY_TEST']
    
    cleaned = 0
    for participant in test_participants:
        participant_dir = f"logs/{participant}"
        if os.path.exists(participant_dir):
            shutil.rmtree(participant_dir)
            print(f"🗑️ Removed: {participant}")
            cleaned += 1
    
    if cleaned == 0:
        print("✨ No test sessions found to clean")
    else:
        print(f"✅ Cleaned {cleaned} test sessions")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_crash_simulation()
        elif sys.argv[1] == '--quick':
            run_timed_crash(5)
        elif sys.argv[1] == '--check':
            check_incomplete_sessions()
        elif sys.argv[1] == '--cleanup':
            cleanup_test_sessions()
        else:
            print("Usage: python simulate_crash.py [--interactive|--quick|--check|--cleanup]")
    else:
        simulate_crash()

if __name__ == '__main__':
    main()
