"""
Custom views for serving certificate images with proper headers
"""
from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
@cache_control(max_age=3600, public=True)
def serve_certificate_image(request, path):
    """
    Serve certificate PNG images with proper Content-Type headers
    """
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'certificates', path)
    
    # Normalize paths for security check
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    file_path_abs = os.path.abspath(file_path)
    
    # Security check: ensure the file is within MEDIA_ROOT/certificates
    certificates_dir = os.path.join(media_root, 'certificates')
    if not file_path_abs.startswith(os.path.abspath(certificates_dir)):
        raise Http404("Invalid file path")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("Certificate image not found")
    
    # Read the file
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
    except IOError:
        raise Http404("Error reading certificate image")
    
    # Determine content type based on file extension
    content_type = 'image/png'  # Default to PNG
    if file_path.lower().endswith('.png'):
        content_type = 'image/png'
    elif file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif file_path.lower().endswith('.gif'):
        content_type = 'image/gif'
    elif file_path.lower().endswith('.webp'):
        content_type = 'image/webp'
    
    # Create response with proper headers
    response = HttpResponse(image_data, content_type=content_type)
    response['Content-Length'] = str(len(image_data))
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    response['Cache-Control'] = 'public, max-age=3600'
    response['Access-Control-Allow-Origin'] = '*'  # Allow CORS for images
    response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

