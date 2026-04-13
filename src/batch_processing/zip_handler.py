"""
ZIP Handler Module
==================
Extracts and validates ZIP files containing images.
Organizes extracted images for batch processing.
"""

import zipfile
import os
import logging
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


def _is_valid_image_file(file_path: str) -> bool:
    """
    Validate image file by checking magic bytes (file signature).
    
    Args:
        file_path (str): Path to file to validate
    
    Returns:
        bool: True if file signature matches known image format
    """
    try:
        magic_bytes = {
            b'\x89PNG': 'png',
            b'\xff\xd8\xff': 'jpeg',
            b'BM': 'bmp',
            b'GIF8': 'gif',
            b'II\x2a\x00': 'tiff',  # Little-endian TIFF
            b'MM\x00\x2a': 'tiff',  # Big-endian TIFF
        }
        with open(file_path, 'rb') as f:
            header = f.read(8)
            for magic, fmt in magic_bytes.items():
                if header.startswith(magic):
                    return True
        return False
    except Exception as e:
        logger.debug(f"Magic byte check failed: {str(e)}")
        return False


def extract_zip(uploaded_file, extract_path: str) -> dict:
    """
    Extract ZIP file and return list of extracted image files.
    Handles both Streamlit uploaded file objects and file paths.
    Case-insensitive extension matching.
    
    Args:
        uploaded_file: Streamlit uploaded file object OR file path (string)
        extract_path (str): Path to extract files to
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'extracted_files': list of file paths,
            'file_count': int
        }
    """
    tmp_zip_path = None
    
    try:
        # Create extract directory if it doesn't exist
        os.makedirs(extract_path, exist_ok=True)
        
        # Handle Streamlit uploaded file object vs file path string
        if isinstance(uploaded_file, str):
            # It's a file path
            tmp_zip_path = uploaded_file
        else:
            # It's a Streamlit uploaded file object
            # Save it to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_zip_path = tmp.name
        
        # Extract ZIP
        extracted_files = []
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
        
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                # Case-insensitive extension check
                file_lower = file_info.filename.lower()
                
                # Check if file has image extension
                if any(file_lower.endswith(ext) for ext in image_extensions):
                    extracted_file = zip_ref.extract(file_info, extract_path)
                    # Normalize path for consistency
                    extracted_file = os.path.normpath(extracted_file)
                    
                    # Validate file content with magic bytes
                    if _is_valid_image_file(extracted_file):
                        extracted_files.append(extracted_file)
                        logger.info(f"Extracted and validated: {file_info.filename}")
                    else:
                        # File extension is image but content is not - remove it
                        logger.warning(f"File has image extension but invalid content: {file_info.filename}")
                        try:
                            os.remove(extracted_file)
                        except Exception as e:
                            logger.warning(f"Could not remove invalid file: {str(e)}")
        
        if not extracted_files:
            logger.warning(f"No image files found in ZIP. Files in ZIP:")
            with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    logger.warning(f"  - {file_info.filename}")
            
            return {
                'success': False,
                'message': 'No image files found in ZIP (supported: .png, .jpg, .jpeg, .bmp, .gif, .tiff)',
                'extracted_files': [],
                'file_count': 0
            }
        
        logger.info(f"Successfully extracted {len(extracted_files)} images")
        return {
            'success': True,
            'message': f'Extracted {len(extracted_files)} images',
            'extracted_files': extracted_files,
            'file_count': len(extracted_files)
        }
    
    except zipfile.BadZipFile:
        logger.error("Invalid ZIP file")
        return {
            'success': False,
            'message': 'Invalid ZIP file format',
            'extracted_files': [],
            'file_count': 0
        }
    
    except Exception as e:
        logger.error(f"ZIP extraction failed: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': f'Extraction failed: {str(e)}',
            'extracted_files': [],
            'file_count': 0
        }
    
    finally:
        # Cleanup temporary ZIP file if we created one
        if tmp_zip_path and isinstance(uploaded_file, str) == False:
            try:
                if os.path.exists(tmp_zip_path):
                    os.remove(tmp_zip_path)
            except Exception as e:
                logger.warning(f"Could not clean up temp ZIP: {str(e)}")


def validate_images(image_paths: list) -> dict:
    """
    Validate that files are valid images.
    
    Args:
        image_paths (list): List of image file paths
    
    Returns:
        dict: {
            'valid': list of valid image paths,
            'invalid': list of invalid paths,
            'valid_count': int
        }
    """
    try:
        from PIL import Image
        
        valid = []
        invalid = []
        
        for path in image_paths:
            try:
                with Image.open(path) as img:
                    img.verify()
                valid.append(path)
                logger.info(f"Valid image: {path}")
            except Exception as e:
                logger.warning(f"Invalid image: {path} - {str(e)}")
                invalid.append({'path': path, 'error': str(e)})
        
        return {
            'valid': valid,
            'invalid': invalid,
            'valid_count': len(valid)
        }
    
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return {
            'valid': [],
            'invalid': image_paths,
            'valid_count': 0
        }


def cleanup_extracted(extract_path: str) -> bool:
    """
    Clean up extracted files and directory.
    
    Args:
        extract_path (str): Path to clean up
    
    Returns:
        bool: Success status
    """
    try:
        import shutil
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
            logger.info(f"Cleaned up: {extract_path}")
        return True
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return False
