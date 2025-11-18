import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import io

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def convert_to_webp(image_path, quality=85):
    """
    Convert image to WebP format.
    
    Args:
        image_path: Path to the image file
        quality: WebP quality (1-100, default 85)
        
    Returns:
        Path to the converted WebP file, or None if conversion fails
    """
    try:
        # Open image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary (WebP supports RGBA, but we'll use RGB for better compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Generate WebP filename
        webp_path = os.path.splitext(image_path)[0] + '.webp'
        
        # Save as WebP
        img.save(webp_path, 'WEBP', quality=quality, optimize=True)
        
        # Delete original file
        if os.path.exists(image_path):
            os.remove(image_path)
        
        return webp_path
    except Exception as e:
        # If conversion fails, return original path
        current_app.logger.error(f'WebP conversion failed: {str(e)}')
        return image_path

def save_uploaded_file(file, subfolder='', convert_webp=True):
    """
    Save uploaded file and optionally convert to WebP format.
    
    Args:
        file: Uploaded file object
        subfolder: Subfolder within uploads directory
        convert_webp: Whether to convert image to WebP format (default: True)
        
    Returns:
        Relative path to saved file (WebP if converted, original otherwise)
    """
    if file and allowed_file(file.filename):
        # Generate unique filename
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        
        # Create directory if not exists
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Check if it's an image file
        is_image = original_ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        
        if is_image and convert_webp:
            # For images, save as WebP
            filename = f"{uuid.uuid4().hex}.webp"
            filepath = os.path.join(upload_folder, filename)
            
            try:
                # Open and convert image
                img = Image.open(io.BytesIO(file.read()))
                
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as WebP
                img.save(filepath, 'WEBP', quality=85, optimize=True)
                
                # Return relative path
                return os.path.join(subfolder, filename).replace('\\', '/')
            except Exception as e:
                # If conversion fails, save original format
                current_app.logger.error(f'WebP conversion failed: {str(e)}')
                filename = f"{uuid.uuid4().hex}.{original_ext}"
                filepath = os.path.join(upload_folder, filename)
                file.seek(0)  # Reset file pointer
                file.save(filepath)
                return os.path.join(subfolder, filename).replace('\\', '/')
        else:
            # For non-image files or when conversion is disabled, save as original
            filename = f"{uuid.uuid4().hex}.{original_ext}"
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            return os.path.join(subfolder, filename).replace('\\', '/')
    return None

def delete_file(filepath):
    """
    Delete file from uploads directory.
    Also handles WebP files - if deleting a non-WebP file, will also try to delete corresponding WebP.
    
    Args:
        filepath: Relative path to file (e.g., 'products/image.jpg' or 'products/image.webp')
        
    Returns:
        True if file was deleted, False otherwise
    """
    if filepath:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
        
        # Try to delete the file
        deleted = False
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                deleted = True
            except Exception as e:
                current_app.logger.error(f'Failed to delete file {filepath}: {str(e)}')
        
        # If deleting a non-WebP file, also try to delete corresponding WebP file
        if not filepath.endswith('.webp'):
            webp_path = os.path.splitext(full_path)[0] + '.webp'
            if os.path.exists(webp_path):
                try:
                    os.remove(webp_path)
                except Exception as e:
                    current_app.logger.error(f'Failed to delete WebP file {webp_path}: {str(e)}')
        
        return deleted
    return False

def slugify(text):
    """Convert text to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

