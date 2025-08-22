#!/usr/bin/env python3
"""
Compilation script for MellowMind deployment.
Compiles all Python files to bytecode (.pyc) except config.py to hide source code.
"""

import os
import py_compile
import shutil
import sys
import subprocess
from pathlib import Path

def compile_project():
    """Compile all Python files except config.py for deployment."""
    
    # Project root directory
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    # Create deployment directory
    deploy_dir = project_root / "deploy"
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Files/directories to exclude from compilation
    exclude_files = {"config.py"}
    exclude_dirs = {"__pycache__", ".git", "logs", "archive", "docs", "utils"}
    
    print("🔨 Starting compilation for deployment...")
    print(f"📁 Source directory: {src_dir}")
    print(f"📦 Deploy directory: {deploy_dir}")
    print(f"🚫 Excluding from compilation: {exclude_files}")
    
    compiled_count = 0
    copied_count = 0
    
    # Copy non-Python files and directories first
    for item in project_root.iterdir():
        if item.name in exclude_dirs or item.name == "deploy":
            continue
            
        if item.is_file() and not item.name.endswith('.py'):
            shutil.copy2(item, deploy_dir / item.name)
            copied_count += 1
        elif item.is_dir() and item.name not in exclude_dirs:
            if item.name == "src":
                continue  # Handle src separately
            shutil.copytree(item, deploy_dir / item.name)
            copied_count += 1
    
    # Create src directory in deployment
    deploy_src = deploy_dir / "src"
    deploy_src.mkdir()
    
    # Process src directory
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        
        # Get relative path for deployment structure
        rel_path = Path(root).relative_to(src_dir)
        deploy_root = deploy_src / rel_path
        deploy_root.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                if file in exclude_files:
                    # Copy config.py as-is (editable)
                    shutil.copy2(file_path, deploy_root / file)
                    print(f"📄 Copied (editable): {file_path.relative_to(project_root)}")
                    copied_count += 1
                else:
                    # Compile Python file to bytecode
                    try:
                        # Compile to .pyc in deployment directory
                        compiled_path = deploy_root / f"{file_path.stem}.pyc"
                        py_compile.compile(file_path, compiled_path, doraise=True)
                        print(f"🔧 Compiled: {file_path.relative_to(project_root)} -> {compiled_path.relative_to(project_root)}")
                        compiled_count += 1
                    except py_compile.PyCompileError as e:
                        print(f"❌ Failed to compile {file_path}: {e}")
                        return False
            else:
                # Copy non-Python files as-is
                shutil.copy2(Path(root) / file, deploy_root / file)
                copied_count += 1
    
    # Create a deployment runner script
    runner_script = deploy_dir / "run_mellowmind_compiled.py"
    runner_content = '''#!/usr/bin/env python3
"""
Deployment runner for compiled MellowMind.
This script runs the compiled bytecode version.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the compiled app
try:
    # Import from compiled bytecode
    import app
    app.main() if hasattr(app, 'main') else print("No main function found in app module")
except ImportError as e:
    print(f"Error importing app module: {e}")
    print("Make sure all dependencies are installed and the compilation was successful.")
    sys.exit(1)
except Exception as e:
    print(f"Error running application: {e}")
    sys.exit(1)
'''
    
    with open(runner_script, 'w') as f:
        f.write(runner_content)
    
    # Make runner script executable
    os.chmod(runner_script, 0o755)
    
    # Create Apple Script application
    create_apple_script_app(project_root, deploy_dir)
    
    print(f"\n✅ Compilation completed successfully!")
    print(f"📊 Statistics:")
    print(f"   - Compiled files: {compiled_count}")
    print(f"   - Copied files: {copied_count}")
    print(f"📁 Deployment ready in: {deploy_dir}")
    print(f"🚀 Run with: python3 {runner_script.relative_to(project_root)}")
    print(f"⚙️  Config file remains editable at: {deploy_dir}/src/config.py")
    
    return True


def create_apple_script_app(project_root, deploy_dir):
    """Create an Apple Script application for easy launching."""
    
    # Detect current user and determine paths
    current_user = os.getenv('USER')
    if current_user == 'hax429':
        base_path = '/Users/hax429/Developer/Internship/MellowMind_desktop'
    elif current_user == 'brluser':
        base_path = '/Users/brluser/MellowMind'
    else:
        # Fallback to current project root
        base_path = str(project_root)
    
    deploy_path = f"{base_path}/deploy"
    conda_env = "moly"
    
    # Create AppleScript content
    applescript_content = f'''on run
    tell application "Terminal"
        activate
        do script "cd '{deploy_path}' && source /opt/miniconda3/etc/profile.d/conda.sh && conda activate {conda_env} && python3 run_mellowmind_compiled.py"
    end tell
end run'''
    
    # Create AppleScript file in deploy directory
    applescript_file = deploy_dir / "MellowMind.scpt"
    with open(applescript_file, 'w') as f:
        f.write(applescript_content)
    
    print(f"📝 Created AppleScript: {applescript_file}")
    
    # Determine desktop path
    desktop_path = f"/Users/{current_user}/Desktop"
    app_name = "MellowMind.app"
    app_path = f"{desktop_path}/{app_name}"
    
    try:
        # Create .app bundle using osacompile
        cmd = [
            'osacompile',
            '-o', app_path,
            str(applescript_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"🍎 Created macOS application: {app_path}")
            
            # Try to set a custom icon if available
            icon_path = project_root / "res" / "mellowmind.png"
            if icon_path.exists():
                try:
                    # Convert PNG to ICNS and set as app icon
                    icns_path = deploy_dir / "icon.icns"
                    
                    # Create ICNS from PNG using sips
                    sips_cmd = [
                        'sips', '-s', 'format', 'icns',
                        str(icon_path), '--out', str(icns_path)
                    ]
                    
                    sips_result = subprocess.run(sips_cmd, capture_output=True, text=True)
                    
                    if sips_result.returncode == 0:
                        # Copy icon to app bundle
                        app_icon_path = f"{app_path}/Contents/Resources/applet.icns"
                        shutil.copy2(icns_path, app_icon_path)
                        print(f"🎨 Set custom icon for application")
                    else:
                        print(f"⚠️  Could not create icon: {sips_result.stderr}")
                        
                except Exception as e:
                    print(f"⚠️  Could not set custom icon: {e}")
            
            return True
            
        else:
            print(f"❌ Failed to create application: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ osacompile not found. Please install Xcode Command Line Tools.")
        return False
    except Exception as e:
        print(f"❌ Error creating application: {e}")
        return False

if __name__ == "__main__":
    try:
        success = compile_project()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Compilation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        sys.exit(1)