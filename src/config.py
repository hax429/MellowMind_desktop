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
STROOP_COUNTDOWN_MINUTES = 3
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

# COLOR SCHEME - Optimized for dark backgrounds
COLORS = {
    'title': '#ff4444',           # Bright red for titles
    'warning': '#ff6666',         # Red for warnings
    'text_primary': 'white',      # Primary text color - white for dark background
    'text_secondary': '#e8e8e8',  # Light gray - much higher contrast than #aa6666
    'text_accent': '#ffaa44',     # Accent text color - yellow/orange for emphasis
    'text_dim': '#cccccc',        # Medium gray for slightly less important text
    'pdf_background': '#2a2a2a',  # Dark gray background for PDF content area
    'pdf_text': '#ffffff',        # Pure white text for PDF content for maximum contrast
    'button_bg': '#ff4444',       # Button background
    'button_active': '#aa0000',   # Button active state
    'notification_bg': '#440000', # Notification background
    'countdown_normal': '#00ff00', # Bright green for normal state (higher contrast)
    'countdown_warning': '#ffff00', # Bright yellow for warning state
    'countdown_critical': '#ff0000', # Bright red for critical state
    'consent_title': '#ffffff',    # Bright white for readability on black background
    'consent_instruction': '#ffaa44', # Orange/yellow for better visibility
    'consent_agreement': '#ff6666',  # Light red for important agreement text
    'consent_button_text': '#ffffff', # White text on red button
    'relaxation_text': '#ffffff'     # Pure white for relaxation overlay text
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

# SURVEY URLS AND WEBPAGE SCREEN SETTINGS
SURVEY_URLS = {
    'prestudy': 'https://mit.co1.qualtrics.com/jfe/form/SV_dnwU04eKIrvIclg',
    'poststudy': 'https://mit.co1.qualtrics.com/jfe/form/SV_0HVcg0Fzo8s7Kbs',
    # Legacy compatibility (can be removed in future versions)
    'google': 'https://mit.co1.qualtrics.com/jfe/form/SV_dnwU04eKIrvIclg',  # Mapped to prestudy
    'pre_study': 'https://mit.co1.qualtrics.com/jfe/form/SV_dnwU04eKIrvIclg',
    'mid_study': 'https://mit.co1.qualtrics.com/jfe/form/SV_midstudysurvey',
    'post_study': 'https://mit.co1.qualtrics.com/jfe/form/SV_0HVcg0Fzo8s7Kbs'
}

# Default survey configurations
DEFAULT_SURVEY_CONFIG = {
    'title': 'Web Survey',
    'button_text': 'CONTINUE',
    'callback': None,
    'height': 800
}

# Specific survey configurations
SURVEY_CONFIGS = {
    # Primary survey configurations
    'prestudy': {
        'title': 'Prestudy Survey',
        'button_text': 'CONTINUE TO CONSENT FORM',
        'callback': 'switch_to_consent',
        'height': 900
    },
    'poststudy': {
        'title': 'Poststudy Survey',
        'button_text': 'FINISH STUDY',
        'callback': 'quit_app',
        'height': 900
    },
    # Legacy configurations (can be removed in future versions)
    'google': {
        'title': 'Google Search - Real Website',
        'button_text': 'CONTINUE TO CONSENT FORM',
        'callback': 'switch_to_consent',
        'height': 800,
        'fallback_html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Search - Study Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: white; }
                .header { text-align: center; margin-bottom: 30px; }
                .logo { font-size: 48px; color: #4285F4; font-weight: bold; }
                .search-box { text-align: center; margin: 30px; }
                .search-input { width: 400px; height: 40px; font-size: 16px; border: 1px solid #ddd; border-radius: 20px; padding: 0 15px; }
                .note { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">Google</div>
            </div>
            <div class="search-box">
                <input type="text" class="search-input" placeholder="Search Google or type a URL">
            </div>
            <div class="note">
                <h3>🌐 Real Google Website Integration</h3>
                <p>This is the actual Google homepage embedded in the study application.</p>
                <p>You can interact with it as you normally would in a web browser.</p>
                <p>When ready, click the "CONTINUE TO CONSENT FORM" button below.</p>
            </div>
        </body>
        </html>
        '''
    },
    'pre_study': {
        'title': 'Pre-Study Survey',
        'button_text': 'CONTINUE TO CONSENT',
        'callback': 'switch_to_consent',
        'height': 900
    },
    'mid_study': {
        'title': 'Mid-Study Survey',
        'button_text': 'CONTINUE TO NEXT TASK',
        'callback': 'switch_to_stroop',
        'height': 900
    },
    'post_study': {
        'title': 'Post-Study Survey',
        'button_text': 'FINISH STUDY',
        'callback': 'switch_to_post_study_rest',
        'height': 900
    }
}

# Pre-study, mid-study, post-study survey URLs (legacy compatibility)
PRE_STUDY_SURVEY_URL = SURVEY_URLS['pre_study']
MID_STUDY_SURVEY_URL = SURVEY_URLS['mid_study']
POST_STUDY_SURVEY_URL = SURVEY_URLS['post_study']