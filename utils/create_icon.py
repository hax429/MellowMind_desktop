#!/usr/bin/env python3
"""
Create a simple icon for MellowMind app
This creates a basic icon using PIL/Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a 512x512 icon (macOS will scale down)
    size = 512
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Create a circular background with gradient-like effect
    center = size // 2
    
    # Draw circles for a zen-like meditation symbol
    # Outer circle - light blue
    draw.ellipse([50, 50, size-50, size-50], fill=(70, 130, 180, 255), outline=(25, 25, 112, 255), width=8)
    
    # Inner circle - white with meditation symbol
    draw.ellipse([150, 150, size-150, size-150], fill=(245, 245, 245, 255), outline=(70, 130, 180, 255), width=6)
    
    # Draw a simple meditation figure or om symbol
    # Simple zen circle (enso-style)
    draw.ellipse([200, 200, size-200, size-200], fill=None, outline=(25, 25, 112, 255), width=12)
    
    # Add a small gap to make it look like an enso circle
    draw.ellipse([240, 240, size-240, size-240], fill=(245, 245, 245, 255), outline=None)
    
    # Try to add text "MM" for MellowMind
    try:
        # Try to use a system font
        font_size = 100
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "MM" text in the center
    text = "MM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    draw.text((text_x, text_y), text, fill=(25, 25, 112, 255), font=font)
    
    # Save as PNG first
    icon_path = "MellowMind.app/Contents/Resources/mellowmind.png"
    icon.save(icon_path, "PNG")
    print(f"✅ Icon created: {icon_path}")
    
    # Try to convert to ICNS format for macOS
    try:
        # Create different sizes for the ICNS file
        sizes = [16, 32, 64, 128, 256, 512]
        icns_path = "MellowMind.app/Contents/Resources/mellowmind.icns"
        
        # For now, just copy the PNG - you'd need additional tools for proper ICNS
        import shutil
        shutil.copy(icon_path, icns_path.replace('.icns', '.png'))
        print(f"✅ Icon copied for app bundle")
        
    except Exception as e:
        print(f"⚠️  Could not create ICNS file: {e}")
        print("The PNG icon will work for basic functionality")
    
    print("🎨 Icon creation complete!")
    
except ImportError:
    print("⚠️  PIL/Pillow not available. Creating a simple text-based icon...")
    
    # Create a simple script that generates a basic icon
    icon_script = '''
import os
import subprocess

# Create a simple colored square using ImageMagick if available
try:
    subprocess.run([
        "convert", "-size", "512x512", "xc:#4682B4", 
        "-fill", "white", "-gravity", "center", 
        "-pointsize", "200", "-annotate", "+0+0", "MM",
        "MellowMind.app/Contents/Resources/mellowmind.png"
    ], check=True)
    print("✅ Icon created using ImageMagick")
except:
    print("⚠️  ImageMagick not available, using default icon")
'''
    
    with open("temp_icon_generator.py", "w") as f:
        f.write(icon_script)
    
    os.system("python3 temp_icon_generator.py")
    os.remove("temp_icon_generator.py")

except Exception as e:
    print(f"❌ Error creating icon: {e}")
    print("The app will work without a custom icon")