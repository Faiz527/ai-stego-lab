"""
Batch Encoder Module
====================
Encodes secret messages into multiple images using three methods:
LSB, Hybrid DCT, and Haar DWT.

Supports two batch modes:
- MODE_1 (Uniform): Same message embedded in all images
- MODE_2 (Packetized): Message split across images
"""

import os
import time
import logging
from pathlib import Path
from PIL import Image
from datetime import datetime
from typing import List, Optional

from ..stego import encode_image, encode_dct, encode_dwt
from ..encryption.encryption import encrypt_message
from .packet_handler import packetize_message, get_packet_map

logger = logging.getLogger(__name__)

DATA_OUTPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'output' / 'encoded'

# Batch mode constants
MODE_UNIFORM = "uniform"      # MODE_1: Same message in all images
MODE_PACKETIZED = "packetized"  # MODE_2: Message split across images


def batch_encode_images(
    image_paths: list,
    secret_message: str,
    methods: list = None,
    encrypt_password: str = None,
    encrypt: bool = False,
    batch_id: str = None,
    batch_mode: str = MODE_UNIFORM
) -> dict:
    """
    Encode secret message into multiple images using selected methods.
    
    Supports two batch modes:
    - MODE_UNIFORM: Embeds the complete message into every image (default)
    - MODE_PACKETIZED: Splits message into packets, one per image
    
    Args:
        image_paths (list): List of image file paths
        secret_message (str): Message to encode
        methods (list): Methods to use ['LSB', 'DCT', 'DWT', 'Hybrid DCT', 'Hybrid DWT', 'all']
        encrypt_password (str): Password for encryption
        encrypt (bool): Whether to encrypt message
        batch_id (str): Unique batch identifier for output folder
        batch_mode (str): 'uniform' or 'packetized'
    
    Returns:
        dict: {
            'success': bool,
            'total_processed': int,
            'total_failed': int,
            'methods_used': list,
            'batch_mode': str,
            'results': {
                'LSB': [...],
                'DCT': [...],
                'DWT': [...]
            },
            'timings': {...},
            'message': str,
            'output_path': str,
            'packet_map': dict (MODE_2 only)
        }
    """
    # Validate batch mode
    if batch_mode not in [MODE_UNIFORM, MODE_PACKETIZED]:
        batch_mode = MODE_UNIFORM
    
    # Validate minimum images for packetized mode
    if batch_mode == MODE_PACKETIZED and len(image_paths) < 2:
        return {
            'success': False,
            'message': 'Packetized mode requires at least 2 images',
            'batch_mode': batch_mode,
            'total_processed': 0,
            'total_failed': 0,
            'methods_used': [],
            'results': {},
            'output_path': ''
        }
    
    # Normalize method names (handle "Hybrid DCT" -> "DCT", etc.)
    normalized_methods = []
    if methods is None or 'all' in methods:
        normalized_methods = ['LSB', 'DCT', 'DWT']
    else:
        method_mapping = {
            'Hybrid DCT': 'DCT',
            'Hybrid DWT': 'DWT',
            'DCT': 'DCT',
            'DWT': 'DWT',
            'LSB': 'LSB'
        }
        for m in methods:
            normalized = method_mapping.get(m, m)
            if normalized not in normalized_methods:
                normalized_methods.append(normalized)
    
    methods = normalized_methods
    
    # Use batch-specific output directory
    if batch_id:
        output_base = Path(__file__).parent.parent.parent / 'data' / 'output' / 'batches' / batch_id / 'encoded'
    else:
        output_base = Path(__file__).parent.parent.parent / 'data' / 'output' / 'encoded'
    
    result = {
        'success': True,
        'total_processed': 0,
        'total_failed': 0,
        'methods_used': methods,
        'batch_mode': batch_mode,
        'results': {method: [] for method in methods},
        'timings': {},
        'message': '',
        'output_path': str(output_base),
        'packet_map': None
    }
    
    # Prepare message (encrypt if requested) - encrypt BEFORE packetization
    message_to_use = secret_message
    if encrypt and encrypt_password:
        try:
            message_to_use = encrypt_message(secret_message, encrypt_password)
            logger.info("Message encrypted with password")
        except Exception as e:
            result['message'] = f"Error: Encryption failed: {str(e)}"
            result['success'] = False
            return result
    
    # Sort image paths for deterministic ordering (important for MODE_2)
    sorted_image_paths = sorted(image_paths, key=lambda x: Path(x).name.lower())
    
    # Prepare messages for each image based on mode
    if batch_mode == MODE_PACKETIZED:
        try:
            packets = packetize_message(message_to_use, len(sorted_image_paths))
            messages_per_image = packets
            
            # Create packet map for reports
            filenames = [Path(p).name for p in sorted_image_paths]
            result['packet_map'] = get_packet_map(filenames, packets)
            
            logger.info(f"MODE_2: Created {len(packets)} packets for {len(sorted_image_paths)} images")
        except Exception as e:
            result['message'] = f"Error: Packetization failed: {str(e)}"
            result['success'] = False
            return result
    else:
        # MODE_1: Same message for all images
        messages_per_image = [message_to_use] * len(sorted_image_paths)
        logger.info(f"MODE_1: Using same message for all {len(sorted_image_paths)} images")
    
    # Create output directories
    for method in methods:
        method_dir = output_base / method
        os.makedirs(method_dir, exist_ok=True)
    
    # Process each image
    for idx, (img_path, msg_to_embed) in enumerate(zip(sorted_image_paths, messages_per_image)):
        try:
            img = Image.open(img_path)
            img_path_obj = Path(img_path)
            filename = img_path_obj.stem
            original_extension = img_path_obj.suffix.lower()
            
            logger.info(f"Processing {idx+1}/{len(sorted_image_paths)}: {filename}")
            
            # Encode with each method
            for method in methods:
                start_time = time.time()
                
                try:
                    logger.debug(f"  {method}: Starting encoding...")
                    
                    if method == 'LSB':
                        encoded_img = encode_image(img, msg_to_embed)
                    elif method == 'DCT':
                        encoded_img = encode_dct(img, msg_to_embed)
                    elif method == 'DWT':
                        encoded_img = encode_dwt(img, msg_to_embed)
                    else:
                        logger.warning(f"  {method}: Unknown method")
                        continue
                    
                    # Save encoded image with appropriate format
                    output_dir = output_base / method
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # For frequency domain methods (DCT, DWT), use PNG to preserve coefficients
                    if method in ['DCT', 'DWT']:
                        output_extension = '.png'
                        pil_format = 'PNG'
                    else:
                        output_extension = original_extension if original_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'] else '.png'
                        pil_format = output_extension.lstrip('.').upper()
                        if pil_format == 'JPG':
                            pil_format = 'JPEG'
                    
                    # Add packet info to filename for MODE_2
                    if batch_mode == MODE_PACKETIZED:
                        output_path = output_dir / f"{filename}_{method}_pkt{idx+1}of{len(sorted_image_paths)}{output_extension}"
                    else:
                        output_path = output_dir / f"{filename}_{method}{output_extension}"
                    
                    # Save with appropriate format
                    encoded_img.save(output_path, pil_format)
                    
                    elapsed_time = time.time() - start_time
                    
                    result_entry = {
                        'filename': filename,
                        'input_path': img_path,
                        'output_path': str(output_path),
                        'size': img.size,
                        'encoding_time': round(elapsed_time, 3),
                        'status': 'Success',
                        'batch_mode': batch_mode
                    }
                    
                    # Add packet info for MODE_2
                    if batch_mode == MODE_PACKETIZED:
                        result_entry['packet_id'] = idx
                        result_entry['total_packets'] = len(sorted_image_paths)
                    
                    result['results'][method].append(result_entry)
                    
                    logger.info(f"  {method}: Encoded in {elapsed_time:.3f}s - {output_path}")
                    result['total_processed'] += 1
                
                except ValueError as e:
                    result['results'][method].append({
                        'filename': filename,
                        'status': f'Failed: {str(e)}'
                    })
                    result['total_failed'] += 1
                    logger.error(f"  {method}: ValueError - {str(e)}")
                
                except Exception as e:
                    result['results'][method].append({
                        'filename': filename,
                        'status': f'Error: {str(e)}'
                    })
                    result['total_failed'] += 1
                    logger.error(f"  {method}: Exception - {str(e)}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Failed to process image {img_path}: {str(e)}", exc_info=True)
            for method in methods:
                result['results'][method].append({
                    'filename': Path(img_path).stem,
                    'status': f'Error: {str(e)}'
                })
            result['total_failed'] += 1
    
    mode_name = "Uniform" if batch_mode == MODE_UNIFORM else "Packetized"
    result['message'] = f"[{mode_name}] Processed {result['total_processed']} images successfully"
    logger.info(result['message'])
    
    return result


def batch_decode_images(
    image_paths: list,
    methods: list = None,
    decrypt_password: str = None,
    decrypt: bool = False
) -> dict:
    """
    Decode messages from multiple images.
    
    Automatically detects if images contain packetized messages (MODE_2)
    and attempts to reconstruct the full message.
    
    Args:
        image_paths (list): List of encoded image file paths
        methods (list): Methods to try for decoding
        decrypt_password (str): Password for decryption
        decrypt (bool): Whether to decrypt after decoding
    
    Returns:
        dict: Decoding results with auto-detected mode handling
    """
    from ..stego import decode_image, decode_dct, decode_dwt
    from ..encryption.encryption import decrypt_message
    from .packet_handler import extract_packet_data, reconstruct_message, is_packetized_message
    
    # Normalize methods
    if methods is None:
        methods = ['LSB', 'DCT', 'DWT']
    
    result = {
        'success': True,
        'total_decoded': 0,
        'total_failed': 0,
        'detected_mode': None,
        'results': [],
        'reconstructed_message': None,
        'message': ''
    }
    
    # Sort for deterministic order
    sorted_paths = sorted(image_paths, key=lambda x: Path(x).name.lower())
    
    decoded_packets = []  # For MODE_2 reconstruction
    
    for img_path in sorted_paths:
        try:
            img = Image.open(img_path)
            filename = Path(img_path).name
            
            decoded_message = None
            used_method = None
            
            # Try each method
            method_funcs = {
                'LSB': decode_image,
                'DCT': decode_dct,
                'DWT': decode_dwt
            }
            
            for method in methods:
                if method not in method_funcs:
                    continue
                try:
                    decoded = method_funcs[method](img)
                    if decoded:
                        decoded_message = decoded
                        used_method = method
                        break
                except Exception:
                    continue
            
            if decoded_message:
                # Check if it's a packet (MODE_2)
                if is_packetized_message(decoded_message):
                    result['detected_mode'] = 'packetized'
                    packet_data = extract_packet_data(decoded_message)
                    if packet_data:
                        decoded_packets.append(packet_data)
                        result['results'].append({
                            'filename': filename,
                            'status': 'Success (Packet)',
                            'method': used_method,
                            'packet_id': packet_data[0]['packet_id'] + 1,
                            'total_packets': packet_data[0]['total_packets']
                        })
                    else:
                        result['results'].append({
                            'filename': filename,
                            'status': 'Failed: Invalid packet format',
                            'method': used_method
                        })
                        result['total_failed'] += 1
                        continue
                else:
                    result['detected_mode'] = result['detected_mode'] or 'uniform'
                    
                    # Decrypt if needed
                    if decrypt and decrypt_password:
                        try:
                            decoded_message = decrypt_message(decoded_message, decrypt_password)
                        except Exception as e:
                            logger.warning(f"Decryption failed for {filename}: {e}")
                    
                    result['results'].append({
                        'filename': filename,
                        'status': 'Success',
                        'method': used_method,
                        'message': decoded_message,
                        'message_length': len(decoded_message)
                    })
                
                result['total_decoded'] += 1
            else:
                result['results'].append({
                    'filename': filename,
                    'status': 'Failed: No message found'
                })
                result['total_failed'] += 1
                
        except Exception as e:
            result['results'].append({
                'filename': Path(img_path).name,
                'status': f'Error: {str(e)}'
            })
            result['total_failed'] += 1
    
    # If packetized mode detected, try to reconstruct
    if result['detected_mode'] == 'packetized' and decoded_packets:
        success, message, details = reconstruct_message(decoded_packets)
        
        if success:
            # Decrypt reconstructed message if needed
            if decrypt and decrypt_password:
                try:
                    message = decrypt_message(message, decrypt_password)
                except Exception as e:
                    logger.warning(f"Decryption of reconstructed message failed: {e}")
            
            result['reconstructed_message'] = message
            result['message'] = f"Packetized mode: {details}"
        else:
            result['success'] = False
            result['message'] = f"Reconstruction failed: {details}"
    else:
        result['message'] = f"Decoded {result['total_decoded']} images"
    
    return result


def get_encoding_capacity(image_path: str) -> dict:
    """
    Calculate message capacity for each method.
    
    Args:
        image_path (str): Path to image
    
    Returns:
        dict: Capacity information for each method
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        pixels = width * height
        
        return {
            'LSB': {
                'bits': pixels * 3,
                'bytes': (pixels * 3) // 8,
                'kb': ((pixels * 3) // 8) / 1024
            },
            'DCT': {
                'bits': pixels,
                'bytes': pixels // 8,
                'kb': (pixels // 8) / 1024
            },
            'DWT': {
                'bits': pixels // 4 * 3,
                'bytes': (pixels // 4 * 3) // 8,
                'kb': ((pixels // 4 * 3) // 8) / 1024
            }
        }
    except Exception as e:
        logger.error(f"Capacity calculation failed: {str(e)}")
        return {}
