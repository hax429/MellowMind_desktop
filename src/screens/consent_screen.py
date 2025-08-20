#!/usr/bin/env python3

from PyQt6.QtWidgets import QTextEdit, QScrollArea, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os
import tempfile
import shutil
from .base_screen import BaseScreen


class ConsentScreen(BaseScreen):
    """Screen for displaying consent form with PDF content."""
    
    def __init__(self, app_instance, logging_manager=None):
        super().__init__(app_instance, logging_manager)
        self.pdf_viewer = None
        self.consent_button = None
        self.consent_enabled = False
        self.background_color = 'black'
        self.preloaded_images = None  # Cache for preloaded PDF images
    
    def setup_screen(self):
        """Setup the consent screen with PDF display and responsive layout."""
        self.set_background_color(self.background_color)
        
        # Get screen dimensions for responsive scaling
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive font sizes
        title_font_size = max(20, min(36, int(screen_width * 0.020)))
        instruction_font_size = max(14, min(22, int(screen_width * 0.012)))
        agreement_font_size = max(12, min(18, int(screen_width * 0.010)))
        button_font_size = max(14, min(20, int(screen_width * 0.011)))
        
        try:
            from config import (CONSENT_TITLE, CONSENT_INSTRUCTION, CONSENT_AGREEMENT_TEXT, 
                              CONSENT_BUTTON_TEXT, CONSENT_SCROLL_REQUIRED, 
                              CONSENT_BODY_TEXT_SIZE, CONSENT_SUBTITLE_SIZE)
        except ImportError:
            # Fallback values if config not available
            CONSENT_TITLE = "Research Consent Form"
            CONSENT_INSTRUCTION = "Please read the following consent form carefully."
            CONSENT_AGREEMENT_TEXT = "By clicking the button below, you agree to participate in this research study."
            CONSENT_BUTTON_TEXT = "I AGREE TO PARTICIPATE"
            CONSENT_SCROLL_REQUIRED = False
            CONSENT_BODY_TEXT_SIZE = 16
            CONSENT_SUBTITLE_SIZE = 20
        
        try:
            from config import COLORS
        except ImportError:
            # Fallback colors
            COLORS = {
                'consent_title': '#ffffff',
                'consent_instruction': '#ffaa44',
                'consent_agreement': '#ff6666'
            }
        
        # Title with better contrast colors - emphasized and responsive
        title = self.create_title(
            CONSENT_TITLE,
            font_size=title_font_size,
            color=COLORS['consent_title']
        )
        self.layout.addWidget(title)
        self.layout.addStretch(1)
        
        # Instructions with brighter, more visible color - responsive font
        instruction = self.create_instruction(
            CONSENT_INSTRUCTION,
            font_size=instruction_font_size,
            color=COLORS['consent_instruction']
        )
        self.layout.addWidget(instruction)
        self.layout.addStretch(1)
        
        # Create scrollable frame for PDF and image content - responsive
        self.setup_content_display()
        
        # Agreement text with bright visible color - responsive font
        agreement_text = self.create_instruction(
            CONSENT_AGREEMENT_TEXT,
            font_size=agreement_font_size,
            color=COLORS['consent_agreement']
        )
        self.layout.addWidget(agreement_text)
        self.layout.addStretch(1)
        
        # Consent button - emphasized and responsive
        try:
            from config import COLORS
            initial_bg = COLORS['consent_button_bg'] if not CONSENT_SCROLL_REQUIRED else COLORS['button_disabled']
        except ImportError:
            initial_bg = '#DC143C' if not CONSENT_SCROLL_REQUIRED else '#CCCCCC'
        initial_enabled = not CONSENT_SCROLL_REQUIRED
        
        button_width = max(200, min(400, int(screen_width * 0.20)))
        button_height = max(50, min(90, int(screen_height * 0.07)))
        
        self.consent_button = self.create_button(
            CONSENT_BUTTON_TEXT,
            command=self.on_consent_given,
            font_size=button_font_size,
            width=button_width,
            height=button_height,
            bg_color=initial_bg,
            fg_color='white'
        )
        
        if not initial_enabled:
            self.consent_button.setEnabled(False)
            try:
                from config import COLORS, UI_SETTINGS
                disabled_bg = COLORS['button_disabled']
                disabled_text = COLORS['button_disabled_text']
                border_color = COLORS['button_border']
                border_radius = UI_SETTINGS['border_radius_medium']
            except ImportError:
                disabled_bg = '#CCCCCC'
                disabled_text = '#666666'
                border_color = 'gray'
                border_radius = '8px'
            self.consent_button.setStyleSheet(f"background-color: {disabled_bg}; color: {disabled_text}; border: 3px solid {border_color}; border-radius: {border_radius}; font-size: {button_font_size}px;")
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.consent_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.layout.addStretch(1)
        
        # Set up scroll detection if required
        if CONSENT_SCROLL_REQUIRED:
            self.setup_scroll_detection()
        
        # Preload PDF images for faster display next time
        self.preload_pdf_images()
        
        # Log screen display
        self.log_action("CONSENT_SCREEN_DISPLAYED", "Consent form displayed to user")
    
    def setup_content_display(self):
        """Set up content display area with PDF and images."""
        try:
            from config import COLORS
        except ImportError:
            COLORS = {'pdf_background': '#2a2a2a', 'pdf_text': '#ffffff'}
        
        # Get screen dimensions for responsive sizing
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive frame height
        content_frame_height = max(400, min(700, int(screen_height * 0.6)))
        
        # Create frame for all content - responsive sizing
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.Box)
        content_frame.setLineWidth(3)
        content_frame.setStyleSheet(f"QFrame {{ border: 3px solid #444444; background-color: {COLORS['pdf_background']}; border-radius: 8px; }}")
        content_frame.setMinimumHeight(content_frame_height)
        content_frame.setMaximumHeight(int(screen_height * 0.65))
        
        # Layout for content frame
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create scrollable area for all content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: none;
                border-radius: 5px;
            }
        """)
        
        # Create widget to hold all content
        content_widget = QFrame()
        content_widget.setStyleSheet("QFrame { background-color: white; border: none; }")
        content_widget_layout = QVBoxLayout(content_widget)
        content_widget_layout.setSpacing(20)
        content_widget_layout.setContentsMargins(20, 20, 20, 20)
        content_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add structured content with images interspersed
        self.add_structured_content_to_layout(content_widget_layout, screen_width)
        
        # Set up scroll area
        scroll_area.setWidget(content_widget)
        content_layout.addWidget(scroll_area)
        
        self.layout.addWidget(content_frame)
        self.add_widget(content_frame)
        
        # Store reference for scroll detection
        self.pdf_viewer = scroll_area
    
    def add_images_to_layout(self, layout, screen_width):
        """Add image1.jpg and image2.jpg to the layout."""
        try:
            # Image paths
            image_paths = [
                'res/image1.jpg',
                'res/image2.jpg'
            ]
            
            for i, image_path in enumerate(image_paths):
                abs_image_path = os.path.abspath(image_path)
                if os.path.exists(abs_image_path):
                    print(f"📷 Loading image {i+1}: {abs_image_path}")
                    
                    # Create title for image
                    image_title = QLabel(f"Figure {i+1}")
                    image_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin: 10px;")
                    layout.addWidget(image_title)
                    
                    # Load and display image
                    pixmap = QPixmap(abs_image_path)
                    if not pixmap.isNull():
                        # Scale image to fit width while maintaining aspect ratio
                        max_width = min(600, int(screen_width * 0.6))
                        if pixmap.width() > max_width:
                            scaled_pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
                        else:
                            scaled_pixmap = pixmap
                        
                        # Create label for image
                        image_label = QLabel()
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        image_label.setPixmap(scaled_pixmap)
                        image_label.setFixedSize(scaled_pixmap.size())
                        layout.addWidget(image_label)
                        
                        print(f"✅ Added image {i+1}: {scaled_pixmap.size()}")
                    else:
                        print(f"⚠️ Failed to load image {i+1}: {abs_image_path}")
                        # Add error message
                        error_label = QLabel(f"⚠️ Could not load image {i+1}")
                        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        error_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
                        layout.addWidget(error_label)
                else:
                    print(f"⚠️ Image {i+1} not found: {abs_image_path}")
                    # Add missing file message
                    missing_label = QLabel(f"⚠️ Image {i+1} not found: {os.path.basename(image_path)}")
                    missing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    missing_label.setStyleSheet("color: orange; font-size: 14px; margin: 10px;")
                    layout.addWidget(missing_label)
        
        except Exception as e:
            print(f"⚠️ Error loading images: {e}")
            error_label = QLabel(f"⚠️ Error loading images: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
            layout.addWidget(error_label)
    
    def add_pdf_to_layout(self, layout):
        """Add consent text content to the layout."""
        try:
            from config import COLORS
        except ImportError:
            COLORS = {'pdf_background': '#2a2a2a', 'pdf_text': '#ffffff'}
        
        # Create text widget for consent content
        consent_text_widget = QTextEdit()
        consent_text_widget.setFont(QFont('Arial', 12, QFont.Weight.Normal))
        consent_text_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                color: black;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 20px;
                line-height: 1.6;
                font-size: 12px;
                max-height: 600px;
            }}
        """)
        
        # Set the new consent text content
        consent_content = """Thank you for participating in our study. This document provides an overview of the session you will take part in, including the tests, cognitive tasks, and questionnaires you will complete. Please read through carefully so you know what to expect.

Study Overview
This study investigates emotional and physiological responses during different activities, including stress tasks and relaxation activities, using wearable devices and smartphone-based interventions. Each session lasts approximately 90 minutes and will be conducted on weekdays only.

Devices and Setup
During the session, you will wear two EmbracePlus devices (on your dominant and non-dominant wrists) and one Galaxy Watch (on your non-dominant wrist). We will confirm your handedness using the Edinburgh Handedness Inventory. These devices will measure physiological signals throughout the session.

Session Outline
●    0–5 min – Welcome, consent reconfirmation, and fitting of wearable devices.

●    5–12 min – Pre-study survey (including SAM, VAS, GAD-7, PHQ-8, and handedness inventory).

●    12–15 min – During study survey (Pre-stress block only: STAI-Y1)

●    15-19 min – Relaxation activity and baseline physiological recording.

●    19–39 min – Stress tasks: 

1. Descriptive Writing (~5 min)

You will be asked to write continuously for a few minutes about a specific prompt (for example, a personal experience or reaction to an image). Please keep writing without stopping until the time is up. There are no right or wrong answers; the goal is simply to express your thoughts.

2. Stroop test (~7-8 min)

You will see words that name colors, but the ink color may not match the word (for example, the word RED shown in blue ink). Your task is to say the color of the ink as quickly and accurately as you can, ignoring the word itself.

3. Mental Arithmetic (~7-8 min)

You will start from the number 4000 and count backwards in steps of 7 (for example: 4000, 3993, 3986, …). Continue out loud, as quickly and accurately as possible, until the researcher asks you to stop.

●    39–59 min – Smartphone activity (randomly assigned)

●    59–64 min – Rest period and recovery recording.      

●    64–72 min – During Study questionnaires: Post-cognitive task block (STAI-Y1, VAS).

●    72–85 min – Post-session survey (BFNE, SAM, WEMWBS, feedback).

●    85–90 min – Debriefing and compensation.

Questionnaires
You will complete several questionnaires at different points in the session. These ask about your feelings, mood, and experiences.
★    SAM (Self-Assessment Manikin): A quick picture-based scale to show how you feel right now.

★    VAS (Visual Analogue Scale): A simple line scale where you mark how strongly you feel something.

★    GAD-7 (Generalized Anxiety Disorder Scale): A short set of questions about common anxiety symptoms.

★    PHQ-8 (Patient Health Questionnaire): Questions about your mood and well-being over the past two weeks.

★    STAI-Y1 (State-Trait Anxiety Inventory): A questionnaire that measures your current level of anxiety.

★    BFNE (Brief Fear of Negative Evaluation): Questions about concerns of how others view you.

★    WEMWBS (Warwick-Edinburgh Mental Well-being Scale): A short survey about your overall mental well-being.

★    Rosenberg Self-Esteem Scale (exploratory): Questions about how you see and value yourself.

★    Feedback questions: At the end, you will be asked for feedback about your experience in the study."""
        
        consent_text_widget.setPlainText(consent_content)
        consent_text_widget.setReadOnly(True)
        
        layout.addWidget(consent_text_widget)
        
        print("📄 Added consent text content")
    
    def add_structured_content_to_layout(self, layout, screen_width):
        """Add structured content with text and images in the correct order."""
        try:
            from config import COLORS
        except ImportError:
            COLORS = {'pdf_background': '#2a2a2a', 'pdf_text': '#ffffff'}
        
        # First section text
        first_section = self.create_text_section("""Thank you for participating in our study. This document provides an overview of the session you will take part in, including the tests, cognitive tasks, and questionnaires you will complete. Please read through carefully so you know what to expect.

Study Overview
This study investigates emotional and physiological responses during different activities, including stress tasks and relaxation activities, using wearable devices and smartphone-based interventions. Each session lasts approximately 90 minutes and will be conducted on weekdays only.

Devices and Setup
During the session, you will wear two EmbracePlus devices (on your dominant and non-dominant wrists) and one Galaxy Watch (on your non-dominant wrist). We will confirm your handedness using the Edinburgh Handedness Inventory. These devices will measure physiological signals throughout the session.""")
        layout.addWidget(first_section)

        # Add image1.jpg without figure label
        self.add_single_image(layout, 'res/image1.jpg', screen_width, "")

        # Session outline section
        session_section = self.create_text_section("""Session Outline
●    0–5 min – Welcome, consent reconfirmation, and fitting of wearable devices.

●    5–12 min – Pre-study survey (including SAM, VAS, GAD-7, PHQ-8, and handedness inventory).

●    12–15 min – During study survey (Pre-stress block only: STAI-Y1)

●    15-19 min – Relaxation activity and baseline physiological recording.

●    19–39 min – Stress tasks: 

1. Descriptive Writing (~5 min)

You will be asked to write continuously for a few minutes about a specific prompt (for example, a personal experience or reaction to an image). Please keep writing without stopping until the time is up. There are no right or wrong answers; the goal is simply to express your thoughts.

2. Stroop test (~7-8 min)

You will see words that name colors, but the ink color may not match the word (for example, the word RED shown in blue ink). Your task is to say the color of the ink as quickly and accurately as you can, ignoring the word itself.""")
        layout.addWidget(session_section)
        
        # Add image2.jpg without figure label
        self.add_single_image(layout, 'res/image2.jpg', screen_width, "")
        
        # Final section
        final_section = self.create_text_section("""3. Mental Arithmetic (~7-8 min)

You will start from the number 4000 and count backwards in steps of 7 (for example: 4000, 3993, 3986, …). Continue out loud, as quickly and accurately as possible, until the researcher asks you to stop.

●    39–59 min – Smartphone activity (randomly assigned)

●    59–64 min – Rest period and recovery recording.      

●    64–72 min – During Study questionnaires: Post-cognitive task block (STAI-Y1, VAS).

●    72–85 min – Post-session survey (BFNE, SAM, WEMWBS, feedback).

●    85–90 min – Debriefing and compensation.

Questionnaires
You will complete several questionnaires at different points in the session. These ask about your feelings, mood, and experiences.
★    SAM (Self-Assessment Manikin): A quick picture-based scale to show how you feel right now.

★    VAS (Visual Analogue Scale): A simple line scale where you mark how strongly you feel something.

★    GAD-7 (Generalized Anxiety Disorder Scale): A short set of questions about common anxiety symptoms.

★    PHQ-8 (Patient Health Questionnaire): Questions about your mood and well-being over the past two weeks.

★    STAI-Y1 (State-Trait Anxiety Inventory): A questionnaire that measures your current level of anxiety.

★    BFNE (Brief Fear of Negative Evaluation): Questions about concerns of how others view you.

★    WEMWBS (Warwick-Edinburgh Mental Well-being Scale): A short survey about your overall mental well-being.

★    Rosenberg Self-Esteem Scale (exploratory): Questions about how you see and value yourself.

★    Feedback questions: At the end, you will be asked for feedback about your experience in the study.""")
        layout.addWidget(final_section)
        
        print("📄 Added structured consent content with images")
    
    def create_text_section(self, text_content):
        """Create a label for a section of content with no borders."""
        # Get font sizes from config
        try:
            from config import CONSENT_BODY_TEXT_SIZE, CONSENT_SUBTITLE_SIZE
        except ImportError:
            CONSENT_BODY_TEXT_SIZE = 16
            CONSENT_SUBTITLE_SIZE = 20
            
        # Bold and enlarge the specified subtitles using config size
        formatted_text = text_content
        subtitle_size_html = str(CONSENT_SUBTITLE_SIZE)
        formatted_text = formatted_text.replace("Study Overview", f"<b><span style='font-size: {subtitle_size_html}px'>Study Overview</span></b>")
        formatted_text = formatted_text.replace("Devices and Setup", f"<b><span style='font-size: {subtitle_size_html}px'>Devices and Setup</span></b>")
        formatted_text = formatted_text.replace("Session Outline", f"<b><span style='font-size: {subtitle_size_html}px'>Session Outline</span></b>")
        formatted_text = formatted_text.replace("Questionnaires", f"<b><span style='font-size: {subtitle_size_html}px'>Questionnaires</span></b>")
        
        # Replace newlines with HTML line breaks for proper formatting
        formatted_text = formatted_text.replace('\n', '<br>')
        
        text_label = QLabel()
        text_label.setFont(QFont('Arial', CONSENT_BODY_TEXT_SIZE, QFont.Weight.Normal))
        text_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: black;
                border: none;
                padding: 10px;
                line-height: 1.6;
                font-size: {CONSENT_BODY_TEXT_SIZE}px;
            }}
        """)
        text_label.setText(formatted_text)
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        return text_label
    
    def add_single_image(self, layout, image_path, screen_width, title):
        """Add a single image to the layout."""
        try:
            abs_image_path = os.path.abspath(image_path)
            if os.path.exists(abs_image_path):
                print(f"📷 Loading image: {abs_image_path}")
                
                # Create title for image only if title is not empty
                if title.strip():
                    image_title = QLabel(title)
                    image_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin: 10px;")
                    layout.addWidget(image_title)
                
                # Load and display image
                pixmap = QPixmap(abs_image_path)
                if not pixmap.isNull():
                    # Scale image to fit width while maintaining aspect ratio
                    max_width = min(600, int(screen_width * 0.6))
                    if pixmap.width() > max_width:
                        scaled_pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
                    else:
                        scaled_pixmap = pixmap
                    
                    # Create label for image
                    image_label = QLabel()
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setFixedSize(scaled_pixmap.size())
                    layout.addWidget(image_label)
                    
                    print(f"✅ Added image: {title}")
                else:
                    print(f"⚠️ Failed to load image: {abs_image_path}")
                    # Add error message
                    error_label = QLabel(f"⚠️ Could not load {title}")
                    error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    error_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
                    layout.addWidget(error_label)
            else:
                print(f"⚠️ Image not found: {abs_image_path}")
                # Add missing file message
                missing_label = QLabel(f"⚠️ {title} not found: {os.path.basename(image_path)}")
                missing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                missing_label.setStyleSheet("color: orange; font-size: 14px; margin: 10px;")
                layout.addWidget(missing_label)
        
        except Exception as e:
            print(f"⚠️ Error loading image {title}: {e}")
            error_label = QLabel(f"⚠️ Error loading {title}: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
            layout.addWidget(error_label)
    
    def try_pdf_to_images_inline(self, layout, pdf_path, colors):
        """Try to convert PDF to images and add them inline to the layout."""
        try:
            from pdf2image import convert_from_path
            
            print(f"📄 Converting PDF to images for inline display: {pdf_path}")
            
            # Convert PDF pages to images
            images = convert_from_path(pdf_path, dpi=150, poppler_path=self._get_poppler_path())
            
            if images:
                # Add each page as an image
                for i, image in enumerate(images):
                    # Convert PIL image to QPixmap
                    page_pixmap = self.pil_to_qpixmap(image)
                    
                    if page_pixmap:
                        # Scale to fit width while maintaining aspect ratio
                        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
                        max_width = min(800, int(screen_width * 0.7))
                        
                        if page_pixmap.width() > max_width:
                            scaled_pixmap = page_pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
                        else:
                            scaled_pixmap = page_pixmap
                        
                        # Create label for this page
                        page_label = QLabel()
                        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        page_label.setPixmap(scaled_pixmap)
                        page_label.setFixedSize(scaled_pixmap.size())
                        
                        layout.addWidget(page_label)
                        print(f"📄 Added PDF page {i+1} as image")
                
                print(f"✅ PDF loaded successfully as {len(images)} images")
                return True
            else:
                print("❌ PDF conversion returned no images")
                return False
                
        except Exception as e:
            print(f"⚠️ Error converting PDF to images for inline display: {e}")
            return False
    
    def load_pdf_text_inline(self, layout, pdf_path, colors):
        """Load PDF text content inline to the layout."""
        try:
            pdf_content = self.read_pdf_file(pdf_path)
            
            # Create text widget for PDF content
            pdf_text_widget = QTextEdit()
            pdf_text_widget.setFont(QFont('Arial', 12, QFont.Weight.Normal))
            pdf_text_widget.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {colors.get('pdf_background', '#2a2a2a')};
                    color: {colors.get('pdf_text', '#ffffff')};
                    border: 2px solid #555555;
                    border-radius: 5px;
                    padding: 20px;
                    line-height: 1.6;
                    font-size: 12px;
                    max-height: 400px;
                }}
            """)
            
            # Add warning message
            warning_text = "⚠️ PDF IMAGE CONVERSION FAILED ⚠️\n"
            warning_text += "Showing text-only content below:\n\n"
            warning_text += "=" * 60 + "\n\n"
            
            pdf_text_widget.setPlainText(warning_text + pdf_content)
            pdf_text_widget.setReadOnly(True)
            
            layout.addWidget(pdf_text_widget)
            
            print("📄 Added PDF as text content")
            
        except Exception as e:
            print(f"⚠️ Error loading PDF text: {e}")
            error_label = QLabel(f"⚠️ Error loading PDF: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
            layout.addWidget(error_label)

    def setup_pdf_display(self):
        """Set up the PDF display area with proper PDF viewer for original formatting."""
        try:
            from config import COLORS
        except ImportError:
            COLORS = {'pdf_background': '#2a2a2a', 'pdf_text': '#ffffff'}
        
        # Get screen dimensions for responsive sizing
        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
        screen_height = self.app.screen_height if hasattr(self.app, 'screen_height') else 1080
        
        # Calculate responsive frame height
        pdf_frame_height = max(400, min(700, int(screen_height * 0.6)))
            
        # Create frame for PDF content - responsive sizing
        pdf_frame = QFrame()
        pdf_frame.setFrameStyle(QFrame.Shape.Box)
        pdf_frame.setLineWidth(3)
        pdf_frame.setStyleSheet(f"QFrame {{ border: 3px solid #444444; background-color: {COLORS['pdf_background']}; border-radius: 8px; }}")
        pdf_frame.setMinimumHeight(pdf_frame_height)
        pdf_frame.setMaximumHeight(int(screen_height * 0.65))
        
        # Layout for PDF frame
        pdf_layout = QVBoxLayout(pdf_frame)
        pdf_layout.setContentsMargins(10, 10, 10, 10)
        
        # Load and display PDF content with proper viewer
        self.load_pdf_viewer(pdf_layout)
        
        self.layout.addWidget(pdf_frame)
        self.add_widget(pdf_frame)
    
    def load_pdf_viewer(self, parent_layout):
        """Load PDF viewer that preserves original formatting and images."""
        try:
            from config import CONSENT_PDF_PATH, COLORS
        except ImportError:
            CONSENT_PDF_PATH = "res/brief.pdf"  # Default path
            COLORS = {'pdf_background': '#2a2a2a', 'pdf_text': '#ffffff'}
            
        try:
            # Get absolute path to PDF
            abs_pdf_path = os.path.abspath(CONSENT_PDF_PATH)
            
            if os.path.exists(abs_pdf_path):
                print(f"📄 Starting PDF loading process")
                print(f"🔍 PDF file: {abs_pdf_path}")
                print(f"🔍 File size: {os.path.getsize(abs_pdf_path)} bytes")
                print(f"🔍 File permissions: {oct(os.stat(abs_pdf_path).st_mode)[-3:]}")
                
                # Try multiple approaches in order of preference
                success = False
                
                # Method 1: Try PDF to images conversion
                print("🔄 Attempting Method 1: PDF to images conversion")
                if not success:
                    success = self.try_pdf_to_images(parent_layout, abs_pdf_path, COLORS)
                    if success:
                        print("✅ Method 1 succeeded: PDF loaded as images")
                        self.log_action("PDF_METHOD_SUCCESS", "PDF loaded using image conversion method")
                    else:
                        print("❌ Method 1 failed: PDF to images conversion failed")
                        self.log_action("PDF_METHOD_FAILED", "PDF image conversion method failed")
                
                # Method 2: Try web engine with PDF.js (if available)
                print("🔄 Attempting Method 2: Web engine PDF viewer")
                if not success:
                    success = self.try_web_pdf_viewer(parent_layout, abs_pdf_path, COLORS)
                    if success:
                        print("✅ Method 2 succeeded: Web engine viewer created")
                        self.log_action("PDF_METHOD_SUCCESS", "PDF loaded using web engine method")
                    else:
                        print("❌ Method 2 failed: Web engine viewer failed")
                        self.log_action("PDF_METHOD_FAILED", "PDF web engine method failed")
                
                # Method 3: Fallback to text extraction
                if not success:
                    print("🔄 Attempting Method 3: Text extraction fallback")
                    print("📄 All PDF viewer methods failed, using text extraction")
                    self.log_action("PDF_METHOD_FALLBACK", "Using text extraction fallback - images/web viewer failed")
                    self.load_pdf_fallback(parent_layout, abs_pdf_path, COLORS)
                    
            else:
                print(f"⚠️ PDF file not found: {abs_pdf_path}")
                self.show_pdf_error(parent_layout, f"PDF file not found at: {abs_pdf_path}", COLORS)
                
        except Exception as e:
            print(f"⚠️ Error setting up PDF viewer: {e}")
            self.show_pdf_error(parent_layout, f"Error setting up PDF viewer: {e}", COLORS)
    
    def try_pdf_to_images(self, parent_layout, pdf_path, colors):
        """Try to convert PDF to images and display them."""
        try:
            # Try to import pdf2image
            from pdf2image import convert_from_path
            
            print(f"📄 Converting PDF to images: {pdf_path}")
            print(f"🔍 PDF file exists: {os.path.exists(pdf_path)}")
            print(f"🔍 PDF file size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
            
            # Check if we have preloaded images
            if self.preloaded_images:
                print("⚡ Using preloaded PDF images")
                images = self.preloaded_images
            else:
                # Check if poppler is available with proper environment
                import subprocess
                try:
                    env = self._get_conda_environment()
                    result = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True, timeout=5, env=env)
                    print(f"🔍 Poppler availability: {result.returncode == 0}")
                    if result.returncode != 0:
                        print(f"🔍 Poppler error: {result.stderr}")
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    print(f"🔍 Poppler check failed: {e}")
                
                # Convert PDF pages to images with proper environment
                print("🔄 Converting PDF to images...")
                print(f"🔍 Using poppler path: {self._get_poppler_path()}")
                print(f"🔍 PDF file size: {os.path.getsize(pdf_path)} bytes")
                print(f"🔍 PDF file permissions: {oct(os.stat(pdf_path).st_mode)[-3:]}")
                
                try:
                    images = convert_from_path(pdf_path, dpi=150, poppler_path=self._get_poppler_path())
                    print(f"🔍 PDF conversion returned {len(images) if images else 0} images")
                except Exception as conversion_error:
                    print(f"🔍 PDF conversion error details: {conversion_error}")
                    print(f"🔍 Error type: {type(conversion_error).__name__}")
                    # Try without explicit poppler path
                    print("🔄 Retrying without explicit poppler path...")
                    try:
                        images = convert_from_path(pdf_path, dpi=150)
                        print(f"🔍 Retry successful: {len(images) if images else 0} images")
                    except Exception as retry_error:
                        print(f"🔍 Retry also failed: {retry_error}")
                        raise retry_error
            
            if images:
                # Create widget to hold all PDF pages directly (no scroll area)
                pdf_widget = QFrame()
                pdf_widget.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 2px solid #555555;
                        border-radius: 5px;
                    }
                """)
                pdf_layout = QVBoxLayout(pdf_widget)
                pdf_layout.setSpacing(10)
                pdf_layout.setContentsMargins(20, 20, 20, 20)
                pdf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center pages within widget
                
                # Add each page as an image
                self.pdf_page_labels = []
                for i, image in enumerate(images):
                    # Convert PIL image to QPixmap
                    page_pixmap = self.pil_to_qpixmap(image)
                    
                    if page_pixmap:
                        # Create label for this page
                        page_label = QLabel()
                        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        # Don't use setScaledContents to prevent stretching
                        
                        # Scale to fit width while maintaining aspect ratio
                        screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
                        max_width = min(800, int(screen_width * 0.7))
                        
                        # Always scale the pixmap to maintain aspect ratio
                        if page_pixmap.width() > max_width:
                            scaled_pixmap = page_pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
                        else:
                            scaled_pixmap = page_pixmap
                        
                        page_label.setPixmap(scaled_pixmap)
                        # Set the label size to match the scaled pixmap
                        page_label.setFixedSize(scaled_pixmap.size())
                        
                        pdf_layout.addWidget(page_label)
                        self.pdf_page_labels.append(page_label)
                        
                        print(f"📄 Added PDF page {i+1} as image")
                
                # Adjust widget size to content
                pdf_widget.adjustSize()
                from PyQt6.QtWidgets import QSizePolicy
                pdf_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                
                # Add PDF widget directly to parent layout (no scroll area)
                parent_layout.addWidget(pdf_widget)
                self.add_widget(pdf_widget)
                
                # Store reference
                self.pdf_viewer = pdf_widget
                
                print(f"✅ PDF loaded successfully as {len(images)} images")
                self.log_action("PDF_LOADED_SUCCESS", f"PDF loaded as {len(images)} image pages")
                return True
                
        except ImportError as e:
            print(f"⚠️ pdf2image library not available: {e}")
            print("🔧 Install with: pip install pdf2image")
            print("🔧 Also requires poppler-utils:")
            print("   - macOS: brew install poppler")
            print("   - Linux: sudo apt-get install poppler-utils")
            print("   - Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/")
            print("🔧 Or run diagnostic: python utils/diagnose_pdf.py")
            return False
        except Exception as e:
            print(f"⚠️ Error converting PDF to images: {e}")
            print(f"🔍 Exception type: {type(e).__name__}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            
            # Provide specific troubleshooting for common errors
            error_msg = str(e).lower()
            if "poppler" in error_msg or "pdftoppm" in error_msg:
                print("🔧 This looks like a poppler installation issue.")
                print("   - Make sure poppler-utils is installed")
                print("   - Check that pdftoppm is in your PATH")
                print("   - Run diagnostic: python utils/diagnose_pdf.py")
            elif "permission" in error_msg or "access" in error_msg:
                print("🔧 This looks like a file permission issue.")
                print(f"   - Check PDF file permissions: {pdf_path}")
                print("   - Make sure the file is readable")
            elif "memory" in error_msg or "allocation" in error_msg:
                print("🔧 This looks like a memory issue.")
                print("   - Try reducing DPI (currently 150)")
                print("   - Check available system memory")
            
            return False
            
        return False
    
    def try_web_pdf_viewer(self, parent_layout, pdf_path, colors):
        """Try to load PDF using web engine with PDF.js."""
        try:
            print(f"📄 Attempting web engine PDF viewer")
            print(f"🔍 PyQt6.QtWebEngineWidgets available: True")
            print(f"🔍 PDF path: {pdf_path}")
            print(f"🔍 PDF file readable: {os.access(pdf_path, os.R_OK) if os.path.exists(pdf_path) else False}")
            
            # Create web engine view
            self.pdf_viewer = QWebEngineView()
            
            # Set up viewer styling
            self.pdf_viewer.setStyleSheet("""
                QWebEngineView {
                    background-color: white;
                    border: 2px solid #555555;
                    border-radius: 5px;
                }
            """)
            
            # Try to load PDF directly
            pdf_url = QUrl.fromLocalFile(pdf_path)
            print(f"🔍 Generated URL: {pdf_url.toString()}")
            print(f"🔍 URL is valid: {pdf_url.isValid()}")
            print(f"🔍 URL scheme: {pdf_url.scheme()}")
            
            self.pdf_viewer.load(pdf_url)
            
            # Add loading status handler
            self.pdf_viewer.loadFinished.connect(self.on_pdf_loaded)
            
            # Add to layout
            parent_layout.addWidget(self.pdf_viewer)
            self.add_widget(self.pdf_viewer)
            
            print(f"📄 Web engine PDF viewer created successfully")
            self.log_action("PDF_WEB_VIEWER_ATTEMPT", f"Attempting web engine PDF load: {pdf_path}")
            
            return True
            
        except ImportError as e:
            print(f"⚠️ QWebEngineView not available: {e}")
            print("🔧 Web engine widgets may not be installed")
            return False
        except Exception as e:
            print(f"⚠️ Error creating web PDF viewer: {e}")
            print(f"🔍 Exception type: {type(e).__name__}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return False
    
    def pil_to_qpixmap(self, pil_image):
        """Convert PIL image to QPixmap."""
        try:
            import io
            
            # Convert PIL image to bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Load into QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            return pixmap
            
        except Exception as e:
            print(f"⚠️ Error converting PIL to QPixmap: {e}")
            return None
    
    def on_pdf_loaded(self, success):
        """Handle PDF loading completion."""
        if success:
            print("✅ PDF loaded successfully in viewer")
            self.log_action("PDF_LOADED_SUCCESS", "PDF document loaded successfully in web viewer")
        else:
            print("⚠️ PDF failed to load in viewer")
            self.log_action("PDF_LOADED_FAILED", "PDF document failed to load in web viewer")
            
            # Get more details about the failure
            if hasattr(self, 'pdf_viewer') and hasattr(self.pdf_viewer, 'page'):
                # Try to get error details from the web page
                js_code = """
                (function() {
                    var errors = [];
                    var consoleLogs = window.console._logs || [];
                    for (var i = 0; i < consoleLogs.length; i++) {
                        errors.push(consoleLogs[i]);
                    }
                    return {
                        url: window.location.href,
                        errors: errors,
                        title: document.title,
                        hasContent: document.body.innerHTML.length > 0
                    };
                })();
                """
                self.pdf_viewer.page().runJavaScript(js_code, self.on_error_details_received)
            
            # Try fallback approach
            try:
                from config import CONSENT_PDF_PATH, COLORS
                abs_pdf_path = os.path.abspath(CONSENT_PDF_PATH)
                self.load_pdf_fallback(self.pdf_viewer.parent().layout(), abs_pdf_path, COLORS)
            except Exception as e:
                print(f"⚠️ Fallback also failed: {e}")
    
    def on_error_details_received(self, result):
        """Handle error details from JavaScript."""
        if result:
            print(f"🔍 Web viewer URL: {result.get('url', 'unknown')}")
            print(f"🔍 Page title: {result.get('title', 'unknown')}")
            print(f"🔍 Has content: {result.get('hasContent', False)}")
            if result.get('errors'):
                print(f"🔍 Console errors: {result['errors']}")
        else:
            print("🔍 Could not retrieve error details from web viewer")
    
    def load_pdf_fallback(self, parent_layout, pdf_path, colors):
        """Fallback method using text extraction if web viewer fails."""
        try:
            print(f"📄 Starting PDF fallback mode for: {pdf_path}")
            print(f"🔍 PDF file exists: {os.path.exists(pdf_path)}")
            print(f"🔍 PDF file size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
            
            # Remove the web viewer if it exists
            if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
                self.pdf_viewer.hide()
                parent_layout.removeWidget(self.pdf_viewer)
            
            # Create text widget with extracted content
            pdf_content = self.read_pdf_file(pdf_path)
            
            screen_width = self.app.screen_width if hasattr(self.app, 'screen_width') else 1920
            pdf_font_size = max(12, min(18, int(screen_width * 0.01)))
            
            fallback_widget = QTextEdit()
            fallback_widget.setFont(QFont('Arial', pdf_font_size, QFont.Weight.Normal))
            fallback_widget.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {colors.get('pdf_background', '#2a2a2a')};
                    color: {colors.get('pdf_text', '#ffffff')};
                    border: 2px solid #555555;
                    border-radius: 5px;
                    padding: 20px;
                    line-height: 1.6;
                    font-size: {pdf_font_size}px;
                }}
            """)
            
            # Add warning message
            warning_text = "⚠️ PDF VIEWER FALLBACK MODE ⚠️\n"
            warning_text += "Original formatting and images may not be displayed.\n"
            warning_text += "Text-only content shown below:\n\n"
            warning_text += "=" * 60 + "\n\n"
            
            fallback_widget.setPlainText(warning_text + pdf_content)
            fallback_widget.setReadOnly(True)
            
            # Store reference for scroll detection
            self.pdf_text_widget = fallback_widget
            
            parent_layout.addWidget(fallback_widget)
            self.add_widget(fallback_widget)
            
            print("📄 Using PDF fallback mode (text extraction)")
            self.log_action("PDF_FALLBACK_MODE", "Using text extraction fallback for PDF display")
            
        except Exception as e:
            print(f"⚠️ Error in PDF fallback: {e}")
            self.show_pdf_error(parent_layout, f"Error in PDF fallback: {e}", colors)
    
    def show_pdf_error(self, parent_layout, error_message, colors):
        """Show error message when PDF cannot be loaded."""
        try:
            error_widget = QTextEdit()
            error_widget.setFont(QFont('Arial', 16))
            error_widget.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {colors.get('pdf_background', '#2a2a2a')};
                    color: {colors.get('pdf_text', '#ffffff')};
                    border: 2px solid #ff6666;
                    border-radius: 5px;
                    padding: 20px;
                }}
            """)
            error_widget.setPlainText(f"❌ ERROR LOADING CONSENT FORM ❌\n\n{error_message}\n\nPlease contact the administrator.")
            error_widget.setReadOnly(True)
            
            parent_layout.addWidget(error_widget)
            self.add_widget(error_widget)
            
        except Exception as e:
            print(f"⚠️ Error showing PDF error: {e}")
    
    def read_pdf_file(self, pdf_path):
        """Read PDF file content and return as text."""
        try:
            # Get absolute path
            abs_path = os.path.abspath(pdf_path)
            print(f"🔍 Reading PDF file: {abs_path}")
            
            if os.path.exists(abs_path):
                print(f"🔍 File exists, attempting text extraction")
                try:
                    # Try to extract actual PDF content using PyPDF2
                    import PyPDF2
                    print(f"🔍 PyPDF2 imported successfully")
                    
                    pdf_text = ""
                    with open(abs_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        print(f"🔍 PDF has {len(pdf_reader.pages)} pages")
                        
                        # Check if PDF is encrypted
                        if pdf_reader.is_encrypted:
                            print("🔍 PDF is encrypted/password protected")
                            return f"PDF file is encrypted or password protected: {pdf_path}\n\nCannot extract text from encrypted PDF."
                        
                        # Extract text from all pages
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            print(f"🔍 Page {page_num + 1} extracted {len(page_text)} characters")
                            pdf_text += page_text + "\n\n"
                    
                    # Clean up the text
                    pdf_text = pdf_text.strip()
                    print(f"🔍 Total extracted text length: {len(pdf_text)} characters")
                    
                    if pdf_text:
                        return pdf_text
                    else:
                        return f"PDF file exists but no text could be extracted from {pdf_path}.\n\nThis may be a scanned PDF or contain only images."
                        
                except ImportError as e:
                    print(f"🔍 PyPDF2 import error: {e}")
                    return f"PyPDF2 library not available. Cannot extract text from {pdf_path}.\n\nPlease install PyPDF2 to read PDF content."
                except Exception as pdf_error:
                    print(f"🔍 PDF reading error: {pdf_error}")
                    print(f"🔍 Error type: {type(pdf_error).__name__}")
                    import traceback
                    print(f"🔍 Full traceback: {traceback.format_exc()}")
                    return f"Error reading PDF {pdf_path}: {pdf_error}\n\nThe file may be corrupted or password protected."
            else:
                print(f"🔍 File does not exist: {abs_path}")
                return f"ERROR: PDF file not found at {abs_path}"
                
        except Exception as e:
            print(f"🔍 General error reading PDF: {e}")
            return f"ERROR reading PDF file: {str(e)}"
    
    def _get_conda_environment(self):
        """Get the conda environment variables for subprocess calls."""
        env = os.environ.copy()
        
        # Try to detect conda environment paths - flexible for deployment
        conda_paths = [
            # Check common conda installation locations
            '~/miniconda3/envs/moly/bin',
            '~/anaconda3/envs/moly/bin',
            '~/miniconda3/envs/mellowmind/bin',
            '~/anaconda3/envs/mellowmind/bin',
            '/opt/miniconda3/envs/moly/bin',
            '/opt/anaconda3/envs/moly/bin',
            '/usr/local/miniconda3/envs/moly/bin',
            '/usr/local/anaconda3/envs/moly/bin',
            # Check if conda is in PATH and try to find environments
        ]
        
        # Also check for conda environments via conda command if available
        try:
            import subprocess
            result = subprocess.run(['conda', 'info', '--envs'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'moly' in line or 'mellowmind' in line:
                        parts = line.split()
                        if len(parts) > 1 and os.path.exists(parts[-1]):
                            conda_paths.insert(0, os.path.join(parts[-1], 'bin'))
        except:
            pass  # conda command not available, continue with hardcoded paths
        
        # Check for existing conda environment paths
        conda_env_bin = None
        for path in conda_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                conda_env_bin = expanded_path
                break
        
        # Also check CONDA_PREFIX if set
        if not conda_env_bin and 'CONDA_PREFIX' in env:
            potential_path = os.path.join(env['CONDA_PREFIX'], 'bin')
            if os.path.exists(potential_path):
                conda_env_bin = potential_path
        
        # Update PATH to include conda environment
        if conda_env_bin:
            current_path = env.get('PATH', '')
            if conda_env_bin not in current_path:
                env['PATH'] = f"{conda_env_bin}:{current_path}"
                print(f"🔧 Added conda env to PATH: {conda_env_bin}")
        
        return env
    
    def _get_poppler_path(self):
        """Get the path to poppler binaries for pdf2image."""
        # Try to find poppler in conda environment - flexible for deployment
        conda_paths = [
            # Check user home directory first (most portable)
            '~/miniconda3/envs/moly/bin',
            '~/anaconda3/envs/moly/bin',
            '~/miniconda3/envs/mellowmind/bin',
            '~/anaconda3/envs/mellowmind/bin',
            # Check system-wide installations
            '/opt/miniconda3/envs/moly/bin',
            '/opt/anaconda3/envs/moly/bin',
            '/usr/local/miniconda3/envs/moly/bin',
            '/usr/local/anaconda3/envs/moly/bin',
            # Check Homebrew on macOS
            '/opt/homebrew/miniconda3/envs/moly/bin',
            '/usr/local/Caskroom/miniconda/base/envs/moly/bin'
        ]
        
        for path in conda_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(os.path.join(expanded_path, 'pdftoppm')):
                print(f"🔧 Found poppler at: {expanded_path}")
                return expanded_path
        
        # Check CONDA_PREFIX if set
        if 'CONDA_PREFIX' in os.environ:
            potential_path = os.path.join(os.environ['CONDA_PREFIX'], 'bin')
            if os.path.exists(os.path.join(potential_path, 'pdftoppm')):
                print(f"🔧 Found poppler at CONDA_PREFIX: {potential_path}")
                return potential_path
        
        print("⚠️ Could not find poppler path, using system default")
        return None

    def preload_pdf_images(self):
        """Preload PDF images in the background for faster display."""
        if self.preloaded_images:
            return  # Already preloaded
            
        try:
            from config import CONSENT_PDF_PATH
        except ImportError:
            CONSENT_PDF_PATH = "res/brief.pdf"
            
        try:
            from pdf2image import convert_from_path
            import threading
            
            def load_images():
                try:
                    abs_pdf_path = os.path.abspath(CONSENT_PDF_PATH)
                    if os.path.exists(abs_pdf_path):
                        print("🔄 Preloading PDF images in background...")
                        self.preloaded_images = convert_from_path(abs_pdf_path, dpi=150, poppler_path=self._get_poppler_path())
                        print(f"⚡ PDF images preloaded: {len(self.preloaded_images)} pages")
                except Exception as e:
                    print(f"⚠️ Failed to preload PDF images: {e}")
            
            # Start preloading in background thread
            thread = threading.Thread(target=load_images, daemon=True)
            thread.start()
            
        except ImportError:
            print("📄 pdf2image not available, skipping preload")
        except Exception as e:
            print(f"⚠️ Error setting up PDF preload: {e}")
    
    def setup_scroll_detection(self):
        """Set up scroll detection to enable consent button when user scrolled to bottom."""
        def check_scroll():
            if not self.consent_enabled:
                # Check different viewer types
                if hasattr(self, 'pdf_viewer') and self.pdf_viewer and self.pdf_viewer.isVisible():
                    # Check if it's a QScrollArea (image-based viewer)
                    if isinstance(self.pdf_viewer, QScrollArea):
                        self.check_scroll_area_position()
                    # Check if it's a QWebEngineView
                    elif hasattr(self.pdf_viewer, 'load'):  # QWebEngineView has load method
                        self.check_web_scroll()
                elif hasattr(self, 'pdf_text_widget') and self.pdf_text_widget:
                    # For text widget, use traditional scroll detection
                    scrollbar = self.pdf_text_widget.verticalScrollBar()
                    if scrollbar.maximum() > 0:
                        # Calculate percentage scrolled
                        scroll_percent = scrollbar.value() / scrollbar.maximum()
                        
                        # Enable button when scrolled near the bottom (90% or more)
                        if scroll_percent >= 0.90:
                            self.enable_consent_button()
                            return
            
            # Continue checking if not enabled yet
            if not self.consent_enabled:
                QTimer.singleShot(200, check_scroll)
        
        # Start checking after delay
        QTimer.singleShot(1000, check_scroll)
    
    def check_scroll_area_position(self):
        """Check scroll position in QScrollArea (for image-based PDF viewer)."""
        if hasattr(self, 'pdf_viewer') and isinstance(self.pdf_viewer, QScrollArea):
            scrollbar = self.pdf_viewer.verticalScrollBar()
            if scrollbar.maximum() > 0:
                # Calculate percentage scrolled
                scroll_percent = scrollbar.value() / scrollbar.maximum()
                
                # Enable button when scrolled near the bottom (90% or more)
                if scroll_percent >= 0.90:
                    self.enable_consent_button()
    
    def check_web_scroll(self):
        """Check scroll position in web engine viewer using JavaScript."""
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
            # JavaScript to check if user has scrolled near the bottom
            js_code = """
            (function() {
                var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                var windowHeight = window.innerHeight;
                var documentHeight = document.documentElement.scrollHeight;
                var scrollPercent = (scrollTop + windowHeight) / documentHeight;
                return scrollPercent >= 0.90;
            })();
            """
            
            self.pdf_viewer.page().runJavaScript(js_code, self.on_scroll_check_result)
    
    def on_scroll_check_result(self, result):
        """Handle result from JavaScript scroll check."""
        if result and not self.consent_enabled:
            self.enable_consent_button()
    
    def enable_consent_button(self):
        """Enable the consent button when scrolling requirement is met."""
        self.consent_enabled = True
        self.consent_button.setEnabled(True)
        self.consent_button.setStyleSheet(
            "background-color: #DC143C; color: white; border: 2px solid gray; border-radius: 5px;"
        )
        print("📋 User scrolled to bottom - consent button enabled")
        self.log_action("CONSENT_SCROLL_COMPLETE", "User scrolled to bottom of consent document")
    
    def on_consent_given(self):
        """Handle when user gives consent."""
        print("✅ User gave consent - proceeding to prestudy survey")
        self.log_action("CONSENT_GIVEN", "User clicked consent button")
        
        if hasattr(self.app, 'prestudy_screen'):
            print("🔍 Using app.prestudy_screen for navigation")
            self.app.switch_to_screen(self.app.prestudy_screen)
        elif hasattr(self.app, 'switch_to_prestudy_survey'):
            print("🔍 Using switch_to_prestudy_survey() method")
            # Fallback to direct method call
            self.app.switch_to_prestudy_survey()
        else:
            print("⚠️ No prestudy survey screen available - this should not happen")
            raise RuntimeError("Prestudy survey screen not available")