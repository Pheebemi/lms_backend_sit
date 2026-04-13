"""
Certificate Generator Utility
Creates beautiful PNG certificates using PIL/Pillow
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
import os


def generate_certificate_png(student_name, course_title, certificate_id, issued_date=None, completed_date=None):
    """
    Generate a PNG certificate using your custom design

    Args:
        student_name: Full name of the student
        course_title: Title of the completed course
        certificate_id: Unique certificate ID
        issued_date: Date when certificate was issued (defaults to today)

    Returns:
        BytesIO object containing the PNG image
    """
    # Load your custom certificate design
    template_path = "media/certificates/certificate_template.png"  # Change this to your template filename

    try:
        # Open your template image
        img = Image.open(template_path).convert('RGB')
        width, height = img.size
    except FileNotFoundError:
        # Fallback: create a blank certificate if template not found
        width = 3508
        height = 2480
        img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)

    # Load fonts for text overlay (customize for your template)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/times.ttf",
    ]

    # Load fonts with sizes appropriate for your template
    student_name_font = None
    course_name_font = None
    certificate_id_font = None

    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                student_name_font = ImageFont.truetype(font_path, 80)  # Adjust size for student name
                course_name_font = ImageFont.truetype(font_path, 60)   # Adjust size for course name
                certificate_id_font = ImageFont.truetype(font_path, 40) # Adjust size for certificate ID
                break
        except:
            continue

    # Fallback fonts
    if not student_name_font:
        default_font = ImageFont.load_default()
        student_name_font = default_font
        course_name_font = default_font
        certificate_id_font = default_font

    # Add text overlays on your template (CUSTOMIZE THESE COORDINATES FOR YOUR DESIGN)
    # Student Name - adjust x, y coordinates to match your template's name field
    student_name_x = 1000  # Center horizontally (half of 2000px width)
    student_name_y = 620   # ADJUST THIS: Increase to move down, decrease to move up
    draw.text((student_name_x, student_name_y), student_name.upper(),  # Convert to uppercase
              fill='#000000', font=student_name_font, anchor='mm')  # Center anchor

    # Completion Date - below the student name
    if completed_date:
        completion_date_x = 1280  # Center horizontally
        completion_date_y = 920 # CHANGE THIS: Position below student name (increase to move down, decrease to move up)
        completion_text = completed_date.strftime('%B %d, %Y')  # Just the date, no "Completed on"
        draw.text((completion_date_x, completion_date_y), completion_text,
                  fill='#000000', font=certificate_id_font, anchor='mm')  # Same size as certificate ID

    # Course Name - REMOVED for now, will add back later
    # course_name_x = 1000   # Center horizontally
    # course_name_y = 750    # ADJUST THIS: Increase to move down, decrease to move up
    # draw.text((course_name_x, course_name_y), course_title,
    #           fill='#000000', font=course_name_font, anchor='mm')  # Center anchor

    # Certificate ID - shortened and moved to top left
    certificate_id_x = 400  # CHANGE THIS: Increase to move RIGHT, decrease to move LEFT
    certificate_id_y = 420 # CHANGE THIS: Increase to move DOWN, decrease to move UP
    draw.text((certificate_id_x, certificate_id_y), certificate_id,  # Just the ID, no "Certificate ID:" text
              fill='#666666', font=certificate_id_font, anchor='lt')  # Left-top anchor

    # Remove all the decorative drawing code since you're using a custom template
    # Keep only the text overlays above and the image saving code below
    
    # Save to BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG', quality=95, dpi=(300, 300))
    img_buffer.seek(0)
    
    return img_buffer


def save_certificate_image(certificate, student_name, course_title, certificate_id, issued_date=None, completed_date=None):
    """
    Generate and save certificate PNG to the certificate model
    
    Args:
        certificate: Certificate model instance
        student_name: Full name of the student
        course_title: Title of the course
        certificate_id: Unique certificate ID
        issued_date: Date when certificate was issued
    
    Returns:
        The certificate instance with image_file saved
    """
    # Generate the PNG
    img_buffer = generate_certificate_png(
        student_name=student_name,
        course_title=course_title,
        certificate_id=certificate_id,
        issued_date=issued_date,
        completed_date=completed_date
    )
    
    # Create filename
    filename = f"certificate_{certificate_id}_{certificate.student.id}.png"
    
    # Save to the certificate model
    certificate.image_file.save(
        filename,
        ContentFile(img_buffer.read()),
        save=True
    )
    
    return certificate

