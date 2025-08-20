#!/usr/bin/env python3

import os

# ========================================
# MOLY APP CONFIGURATION
# ========================================

# APPLICATION SETTINGS
APP_TITLE = "Moly"

# Background colors are now defined in COLORS dictionary below
BACKGROUND_COLOR = '#220000'  # Dark red background for stress (legacy - use COLORS['background_primary'])
MAIN_FRAME_COLOR = '#220000'  # Main container color (legacy - use COLORS['background_primary'])

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
    "Please write continuously for the next few minutes about a recent situation where you felt stressed while having to perform under time pressure (e.g., exam, interview, or work task). Describe what happened, how you felt, and what thoughts went through your mind. Do not stop writing until the time is up.",
    "Look at the picture on the screen. Describe in as much detail as possible what you see, what you think is happening, and what the people might be thinking or feeling. Keep writing continuously for the entire duration, without pausing."
]

# STROOP SCREEN SETTINGS
STROOP_VIDEO_PATH = os.path.join("res", "stroop.mov")
GENERATE_STROOP_NATIVE = False  # When True, generates native word list instead of video

# MATH TASK SETTINGS
MATH_STARTING_NUMBER = 4000
MATH_SUBTRACTION_VALUE = 7
MATH_INSTRUCTION_TEXT = "Please subtract 7s from 4000, and say it aloud"

# CONTENT PERFORMANCE TASK SETTINGS
CONTENT_PERFORMANCE_TEXT = "Follow the instructions by the instructor and finish your task on Samsung phone"
# Background color moved to COLORS['content_performance_bg']

# ========================================
# UI THEME AND COLOR SETTINGS
# ========================================

# COLOR SCHEME - Optimized for dark backgrounds
COLORS = {
    # Core Text Colors
    'title': '#ff4444',           # Bright red for titles
    'warning': '#ff6666',         # Red for warnings
    'text_primary': 'white',      # Primary text color - white for dark background
    'text_secondary': '#e8e8e8',  # Light gray - much higher contrast than #aa6666
    'text_accent': '#ffaa44',     # Accent text color - yellow/orange for emphasis
    'text_dim': '#cccccc',        # Medium gray for slightly less important text
    
    # Background Colors
    'background_primary': '#220000',    # Main background color (dark red)
    'background_secondary': 'black',    # Secondary background (pure black)
    'background_frame': '#2a2a2a',      # Frame background (dark gray)
    'background_overlay': 'rgba(0, 0, 0, 150)',  # Semi-transparent overlay
    'background_overlay_light': 'rgba(0, 0, 0, 100)',  # Lighter overlay
    'background_overlay_heavy': 'rgba(0, 0, 0, 200)',  # Heavier overlay
    
    # Button Colors
    'button_bg': '#4CAF50',       # Primary button background (green)
    'button_bg_secondary': '#ff4444',  # Secondary button background (red)
    'button_text': 'white',       # Button text color
    'button_text_dark': 'black',  # Dark button text
    'button_active': '#45a049',   # Button active/hover state
    'button_disabled': '#CCCCCC', # Disabled button background
    'button_disabled_text': '#666666',  # Disabled button text
    'button_border': 'gray',      # Button border color
    
    # Specific UI Element Colors
    'pdf_background': '#2a2a2a',  # Dark gray background for PDF content area
    'pdf_text': '#ffffff',        # Pure white text for PDF content for maximum contrast
    'notification_bg': '#440000', # Notification background
    'border_default': '#444444',  # Default border color
    'border_accent': '#555555',   # Accent border color
    'border_warning': '#ff6666',  # Warning border color
    
    # Countdown Widget Colors
    'countdown_normal': '#00ff00',     # Bright green for normal state (higher contrast)
    'countdown_warning': '#ffff00',    # Bright yellow for warning state
    'countdown_critical': '#ff0000',   # Bright red for critical state
    'countdown_bg_normal': 'rgba(0, 0, 0, 200)',      # Normal countdown background
    'countdown_bg_warning': 'rgba(255, 165, 0, 180)', # Warning countdown background
    'countdown_bg_critical': 'rgba(255, 0, 0, 180)',  # Critical countdown background
    'countdown_bg_overtime': 'rgba(255, 0, 0, 220)',  # Overtime countdown background
    
    # Consent Screen Colors
    'consent_title': '#ffffff',        # Bright white for readability on black background
    'consent_instruction': '#ffaa44',  # Orange/yellow for better visibility
    'consent_agreement': '#ff6666',    # Light red for important agreement text
    'consent_button_bg': '#DC143C',    # Consent button background
    'consent_button_text': '#ffffff',  # White text on consent button
    'consent_button_disabled': '#CCCCCC',  # Disabled consent button
    
    # Task-Specific Colors
    'relaxation_text': '#ffffff',      # Pure white for relaxation overlay text
    'descriptive_bg': '#8B0000',       # Descriptive task background
    'stroop_bg': '#8B0000',           # Stroop task background
    'math_bg': '#8B0000',             # Math task background
    'content_performance_bg': '#2E5A87',  # Content performance background
    'post_study_bg': '#220000',       # Post-study rest background
    
    # Webpage/Survey Colors
    'webpage_accent': '#4285F4',      # Webpage accent color (Google blue)
    'webpage_bg': 'white',            # Webpage background
    
    # Special Effect Colors
    'text_shadow': 'rgba(0, 0, 0, 0.8)',     # Text shadow
    'border_glow': 'rgba(255, 255, 255, 0.3)', # Border glow effect
}

# UI ELEMENT STYLING
UI_SETTINGS = {
    # Font Settings
    'font_family': 'Arial',
    'font_weight_normal': 'normal',
    'font_weight_bold': 'bold',
    
    # Border Radius Settings
    'border_radius_small': '5px',
    'border_radius_medium': '8px',
    'border_radius_large': '15px',
    'border_radius_round': '20px',
    
    # Border Width Settings
    'border_width_thin': '2px',
    'border_width_medium': '3px',
    'border_width_thick': '4px',
    
    # Spacing Settings
    'padding_small': '10px',
    'padding_medium': '20px',
    'padding_large': '25px',
    
    # Button Default Settings
    'button_default_width': 150,
    'button_default_height': 50,
    'button_large_width': 400,
    'button_large_height': 120,
    
    # Text Line Height
    'line_height_normal': '1.4',
    'line_height_compact': '1.2',
    'line_height_loose': '1.6',
}

# TRANSITION SCREEN SETTINGS
TRANSITION_INSTRUCTION_TEXT = "Please listen carefully for the instructor on how to proceed to the next part."

# TRANSITION MESSAGES (content shown on transition screens)
TRANSITION_MESSAGES = {
    'descriptive': "You will be asked to write continuously for a few minutes about a specific prompt (for example, a personal experience or reaction to an image). Please keep writing without stopping until the time is up. There are no right or wrong answers; the goal is simply to express your thoughts. Performance is being monitored.",
    'stroop': "You will see words that name colors, but the ink color may not match the word (for example, the word RED shown in blue ink). Your task is to say the color of the ink as quickly and accurately as you can, ignoring the word itself. Your attention and responses are being monitored closely.",
    'math': "You will start from the number 4000 and count backwards in steps of 7 (for example: 4000, 3993, 3986, …). Continue out loud, as quickly and accurately as possible, until the researcher asks you to stop.",
    'content_performance': "Evaluation complete. You are now entering the content performance task. Please follow the instructions provided by the instructor and complete your task on the Samsung phone.",
    'relaxation': "You will now enter a relaxation task. Please remain still and minimize movements. Focus on your breathing and let go of any tension."
}

# TRANSITION SCREEN IMAGE PATHS
TRANSITION_IMAGES = {
    'stroop': os.path.join("res", "stroop.png")
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
    'duringstudy1': 'https://placeholder.url.for.duringstudy1',  # To be updated with actual URL
    'duringstudy2': 'https://placeholder.url.for.duringstudy2',  # To be updated with actual URL
    'poststudy': 'https://mit.co1.qualtrics.com/jfe/form/SV_0HVcg0Fzo8s7Kbs'
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
    'duringstudy1': {
        'title': 'During Study Survey 1',
        'button_text': 'CONTINUE TO DESCRIPTIVE TASK',
        'callback': 'switch_to_descriptive_transition',
        'height': 900
    },
    'duringstudy2': {
        'title': 'During Study Survey 2',
        'button_text': 'CONTINUE TO CONTENT PERFORMANCE TASK',
        'callback': 'switch_to_content_performance_transition',
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

