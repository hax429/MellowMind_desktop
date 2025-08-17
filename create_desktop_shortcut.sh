#!/bin/bash

# Create Desktop Shortcut for MellowMind
# This script creates a shortcut on the desktop

DESKTOP_PATH="$HOME/Desktop"
APP_PATH="$(pwd)/MellowMind.app"
SHORTCUT_PATH="$DESKTOP_PATH/MellowMind.app"

echo "🖥️  Creating desktop shortcut for MellowMind..."

# Check if desktop exists
if [ ! -d "$DESKTOP_PATH" ]; then
    echo "❌ Desktop directory not found at $DESKTOP_PATH"
    exit 1
fi

# Check if app bundle exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ MellowMind.app not found at $APP_PATH"
    echo "Please run this script from the directory containing MellowMind.app"
    exit 1
fi

# Create symbolic link to desktop
if [ -L "$SHORTCUT_PATH" ]; then
    echo "🔄 Removing existing shortcut..."
    rm "$SHORTCUT_PATH"
fi

ln -s "$APP_PATH" "$SHORTCUT_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Desktop shortcut created successfully!"
    echo "📍 Shortcut location: $SHORTCUT_PATH"
    echo "🖱️  You can now double-click the MellowMind app on your desktop to launch it"
else
    echo "❌ Failed to create desktop shortcut"
    exit 1
fi

# Try to set the icon (this may require additional permissions)
echo "🎨 Attempting to set custom icon..."
if command -v SetFile &> /dev/null; then
    SetFile -a C "$SHORTCUT_PATH"
    echo "✅ Icon attributes set"
else
    echo "⚠️  SetFile command not available, using default icon"
fi

echo ""
echo "🧘 MellowMind Desktop Setup Complete!"
echo "   • App bundle: $APP_PATH"
echo "   • Desktop shortcut: $SHORTCUT_PATH"
echo "   • Shell script: ./start_mellowmind.sh"
echo ""
echo "You can launch MellowMind by:"
echo "  1. Double-clicking the app on your desktop"
echo "  2. Double-clicking MellowMind.app in this folder"
echo "  3. Running: ./start_mellowmind.sh"