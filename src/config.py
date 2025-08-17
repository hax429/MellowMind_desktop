#!/usr/bin/env python3

import os

# ========================================
# MOLY APP CONFIGURATION
# ========================================

# APPLICATION SETTINGS
APP_TITLE = "Moly"

BACKGROUND_COLOR = '#220000'  # Dark red background for stress
MAIN_FRAME_COLOR = '#220000'  # Main container color

# MODE SETTINGS
DEVELOPER_MODE = True   # Show instructions (Press N for next prompt, etc.)
FOCUS_MODE = True      # Keep window always on top and maintain focus

# TASK SELECTION MODE
# Options: "self_selection" or "random_assigned"
TASK_SELECTION_MODE = "random_assigned"  # Choose between self selection and random assignment

# LOGGING SETTINGS
DESCRIPTIVE_LINE_LOGGING = True  # Log sentences when user types "." in descriptive task

# RELAXATION SCREEN SETTINGS
SHOW_RELAXATION_TEXT = True  # Whether to show text overlay on relaxation screen
RELAXATION_TEXT = "Please Relax"  # Text to display on relaxation screen
RELAXATION_VIDEO_PATH = os.path.join("res", "screen.mkv")

# COUNTDOWN TIMER SETTINGS
# Global countdown toggle (master switch)
COUNTDOWN_ENABLED = True

# Individual screen countdown toggles
DESCRIPTIVE_COUNTDOWN_ENABLED = True
STROOP_COUNTDOWN_ENABLED = True
MATH_COUNTDOWN_ENABLED = True

# Countdown durations (in minutes)
DESCRIPTIVE_COUNTDOWN_MINUTES = 1
STROOP_COUNTDOWN_MINUTES = 1
MATH_COUNTDOWN_MINUTES = 1
RELAXATION_COUNTDOWN_MINUTES = 1  # Hidden countdown for automatic transition

# DESCRIPTIVE TASK SETTINGS
DESCRIPTIVE_PROMPTS = [
    "Describe the colors you see around you in detail",
    "Notice five things you can hear right now",
    "Describe the texture of three objects within reach",
    "Name three scents you can detect in this moment",
    "Describe the temperature and feeling of the air on your skin",
    "List five things you are grateful for today",
    "Describe your breathing pattern in detail",
    "Notice the position of your body and how it feels",
    "Describe the lighting in your environment",
    "Think of a peaceful place and describe it in detail"
]

# STROOP SCREEN SETTINGS
STROOP_VIDEO_PATH = os.path.join("res", "stroop.mov")

# MATH TASK SETTINGS
MATH_STARTING_NUMBER = 4000
MATH_SUBTRACTION_VALUE = 7
MATH_INSTRUCTION_TEXT = "Please subtract 7s from 4000, and say it aloud"

# CONTENT PERFORMANCE TASK SETTINGS
CONTENT_PERFORMANCE_TEXT = "Follow the instructions by the instructor and finish your task on Samsung phone"
CONTENT_PERFORMANCE_BG_COLOR = '#2E5A87'  # Darker blue for content performance screen

# COLOR SCHEME
COLORS = {
    'title': '#ff4444',           # Bright red for titles
    'warning': '#ff6666',         # Red for warnings
    'text_primary': 'white',      # Primary text color
    'text_secondary': '#aa6666',  # Secondary text color
    'text_accent': '#ffaa44',     # Accent text color
    'button_bg': '#ff4444',       # Button background
    'button_active': '#aa0000',   # Button active state
    'notification_bg': '#440000', # Notification background
    'countdown_normal': '#ffaa44', # Countdown normal state
    'countdown_warning': '#ff6666', # Countdown warning state
    'countdown_critical': '#ff0000' # Countdown critical state
}

# TRANSITION SCREEN SETTINGS
TRANSITION_INSTRUCTION_TEXT = "Please listen carefully for the instructor on how to proceed to the next part."

# TRANSITION MESSAGES (content shown on transition screens)
TRANSITION_MESSAGES = {
    'descriptive': "You are entering the DESCRIPTIVE TASK evaluation phase. Your responses will be evaluated for accuracy and detail. Performance is being monitored.",
    'stroop': "You are now entering the stroop VIDEO evaluation phase. Your attention and responses are being monitored closely.",
    'math': "You are now in the MATH TASK evaluation phase. Your mathematical performance is being assessed. Say your answers aloud.",
    'post_study_rest': "Evaluation complete. You are now entering the POST-STUDY REST phase. Please relax and allow yourself to decompress from the evaluation tasks."
}

# TASK ASSIGNMENT FILE PATH
TASK_ASSIGNMENTS_FILE = "task_assignments.json"

# CONSENT SCREEN SETTINGS
CONSENT_ENABLED = True  # Whether to show consent screen
CONSENT_PDF_PATH = os.path.join("res", "brief.pdf")
CONSENT_TITLE = "Study Information and Consent"
CONSENT_INSTRUCTION = "Please read the study information below carefully. You must scroll to the bottom to continue."
CONSENT_BUTTON_TEXT = "I CONSENT TO PARTICIPATE"
CONSENT_AGREEMENT_TEXT = "By clicking this button, you voluntarily agree to participate in our study."
CONSENT_SCROLL_REQUIRED = True  # Whether user must scroll to bottom to enable button