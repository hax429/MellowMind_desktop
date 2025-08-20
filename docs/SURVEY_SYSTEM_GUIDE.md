# Universal Survey System Guide

## Overview

The webpage screen has been made universal and can now handle multiple survey types including prestudy and poststudy surveys. The system is designed to be easily extensible for future survey types.

## Current Flow

1. **Participant ID Entry** → **Prestudy Survey** → **Consent** → **Study Tasks** → **Post-Study Rest** → **Poststudy Survey** → **App Exit**

## Survey Types Configured

### 1. Prestudy Survey (PRIMARY - Default First Screen)
- **Title**: "Prestudy Survey" 
- **URL**: `https://mit.co1.qualtrics.com/jfe/form/SV_dnwU04eKIrvIclg`
- **Button**: "CONTINUE TO CONSENT FORM"
- **Next**: Transitions to Consent Screen
- **Status**: 🟢 **This is now the default first screen after participant ID entry (replaces Google screen)**

### 2. Poststudy Survey (PRIMARY - Final Screen)
- **Title**: "Poststudy Survey"
- **URL**: `https://mit.co1.qualtrics.com/jfe/form/SV_0HVcg0Fzo8s7Kbs`
- **Button**: "FINISH STUDY" 
- **Next**: Exits the application
- **Status**: 🟢 **Shown after the post-study rest screen**

### 3. Legacy Surveys (for compatibility - deprecated)
- ❌ Google search demo screen (REMOVED from default flow)
- Pre-study, mid-study, post-study surveys (legacy naming)

## Configuration Location

All survey configurations are in `src/config.py`:

```python
SURVEY_URLS = {
    'prestudy': 'https://mit.co1.qualtrics.com/jfe/form/SV_dnwU04eKIrvIclg',
    'poststudy': 'https://mit.co1.qualtrics.com/jfe/form/SV_0HVcg0Fzo8s7Kbs',
    # ... other survey types
}

SURVEY_CONFIGS = {
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
    }
}
```

## Adding New Survey Types

To add a new survey type:

1. **Add URL to config.py**:
```python
SURVEY_URLS['new_survey'] = 'https://your-survey-url.com'
```

2. **Add configuration to config.py**:
```python
SURVEY_CONFIGS['new_survey'] = {
    'title': 'New Survey Title',
    'button_text': 'CONTINUE TO NEXT',
    'callback': 'method_to_call_next',
    'height': 900
}
```

3. **Create screen instance in app.py**:
```python
self.new_survey_screen = WebpageScreen(self, self.logging_manager, 'new_survey')
```

4. **Add to screens dictionary**:
```python
self.screens['new_survey'] = self.new_survey_screen
```

5. **Add switch method**:
```python
def switch_to_new_survey(self):
    print("📋 Switching to New Survey")
    self.switch_to_screen(self.new_survey_screen)
```

## Universal Methods Available

The WebpageScreen class provides these universal methods:

- `configure_for_prestudy()` - Reconfigure for prestudy survey
- `configure_for_poststudy()` - Reconfigure for poststudy survey  
- `configure_for_custom_survey(type, title, url, button_text, callback)` - Dynamic configuration
- `set_survey_type(survey_type)` - Change survey type and reload

## Example Usage

```python
# Create a new survey screen dynamically
survey_screen = WebpageScreen(app, logging_manager)
survey_screen.configure_for_custom_survey(
    'feedback', 
    'Feedback Survey', 
    'https://feedback-url.com',
    'SUBMIT FEEDBACK',
    'switch_to_next_screen'
)
```

## Current App Instance Variables

- `self.prestudy_screen` - 🟢 **Prestudy survey screen (PRIMARY - default first screen)**
- `self.poststudy_screen` - 🟢 **Poststudy survey screen (PRIMARY - final screen)**
- ~~`self.webpage_screen`~~ - ❌ **Removed - Google demo screen no longer in use**

## Switch Methods Available

- `self.app.switch_to_prestudy_survey()` - 🟢 **Primary method (default after participant ID)**
- `self.app.switch_to_poststudy_survey()` - 🟢 **Primary method (after post-study rest)**
- ~~`self.app.switch_to_webpage_screen()`~~ - ❌ **Removed method**

All screens are responsive and will automatically adjust to different screen sizes.