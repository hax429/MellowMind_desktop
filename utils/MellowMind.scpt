#!/usr/bin/osascript

tell application "Terminal"
    activate
    do script "cd '/Users/hax429/Developer/Internship/MellowMind_desktop' && export PYTHONPATH='/Users/hax429/Developer/Internship/MellowMind_desktop/src:${PYTHONPATH}' && /opt/miniconda3/envs/moly/bin/python3 src/app.py"
end tell