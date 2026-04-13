"""
Batch Processing Module
=======================
Handles bulk steganography operations on multiple images.
Supports ZIP uploads, batch encoding, and comprehensive reporting.

Two Batch Modes:
- MODE_1 (Uniform): Same message in all images - each image independently decodable
- MODE_2 (Packetized): Message split across images - all images required for decoding
"""

from .zip_handler import extract_zip, validate_images, cleanup_extracted
from .batch_encoder import (
    batch_encode_images, 
    batch_decode_images,
    get_encoding_capacity,
    MODE_UNIFORM,
    MODE_PACKETIZED
)
from .packet_handler import (
    packetize_message,
    extract_packet_data,
    reconstruct_message,
    is_packetized_message,
    get_packet_map
)
from .report_generator import generate_batch_report, generate_csv_report, export_summary
from .controller import BatchProcessingController

__all__ = [
    # ZIP handling
    'extract_zip',
    'validate_images',
    'cleanup_extracted',
    
    # Batch encoding/decoding
    'batch_encode_images',
    'batch_decode_images',
    'get_encoding_capacity',
    
    # Mode constants
    'MODE_UNIFORM',
    'MODE_PACKETIZED',
    
    # Packet handling
    'packetize_message',
    'extract_packet_data',
    'reconstruct_message',
    'is_packetized_message',
    'get_packet_map',
    
    # Reporting
    'generate_batch_report',
    'generate_csv_report',
    'export_summary',
    
    # Controller
    'BatchProcessingController'
]
