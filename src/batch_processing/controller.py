"""
Batch Processing Controller
============================
Orchestrates the complete batch processing workflow.
Coordinates ZIP extraction, validation, encoding, and reporting.
"""

import logging
import os
from pathlib import Path
from typing import Union, List

from .zip_handler import extract_zip, validate_images, cleanup_extracted
from .batch_encoder import batch_encode_images
from .report_generator import generate_batch_report, generate_csv_report, export_summary
from ..db.db_utils import log_operation

logger = logging.getLogger(__name__)

DATA_INPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'input'
DATA_OUTPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'output'


class BatchProcessingController:
    """
    Orchestrates batch image encoding workflow.
    Handles both direct image inputs and ZIP file uploads.
    """
    
    def __init__(self):
        """Initialize controller and create required directories."""
        # Define paths as instance variables
        self.base_path = Path(__file__).parent.parent.parent
        self.input_images_path = self.base_path / 'data' / 'input' / 'images'
        self.input_zips_path = self.base_path / 'data' / 'input' / 'zips'
        self.output_encoded_path = self.base_path / 'data' / 'output' / 'encoded'
        self.output_decoded_path = self.base_path / 'data' / 'output' / 'decoded'
        self.output_reports_path = self.base_path / 'data' / 'output' / 'reports'
        self.batches_path = self.base_path / 'data' / 'output' / 'batches'
        
        # Create required directories
        self._ensure_directories()
        self.current_batch = None
    
    def _ensure_directories(self):
        """Ensure all required data directories exist."""
        directories = [
            self.input_images_path,
            self.input_zips_path,
            self.output_encoded_path,
            self.output_decoded_path,
            self.output_reports_path,
            self.batches_path
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory ready: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
    
    def process_zip_batch(
        self,
        zip_path: str,
        secret_message: str,
        methods: list = None,
        encrypt: bool = False,
        encrypt_password: str = None,
        username: str = 'batch_user'  # Add username parameter
    ) -> dict:
        """
        Process entire batch from ZIP file.
        
        Args:
            zip_path (str): Path to ZIP file
            secret_message (str): Message to encode
            methods (list): Encoding methods
            encrypt (bool): Whether to encrypt
            encrypt_password (str): Encryption password
            username (str): Username for logging
        """
        try:
            import uuid
            from datetime import datetime
            
            # Generate unique batch ID
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Starting ZIP batch processing: {zip_path}")
            logger.info(f"Batch ID: {batch_id}")
            
            zip_path = Path(zip_path)
            if not zip_path.exists():
                return {
                    'success': False,
                    'message': f"ZIP file not found: {zip_path}"
                }
            
            # Step 1: Extract ZIP
            logger.info("Step 1: Extracting ZIP...")
            extract_result = extract_zip(str(zip_path), str(self.input_images_path))
            
            if not extract_result['success']:
                return {
                    'success': False,
                    'message': f"ZIP extraction failed: {extract_result['message']}"
                }
            
            image_paths = extract_result['extracted_files']
            logger.info(f"Extracted {len(image_paths)} images")
            
            # Step 2: Validate images
            logger.info("Step 2: Validating images...")
            validation_result = validate_images(image_paths)
            valid_images = validation_result['valid']
            
            if not valid_images:
                return {
                    'success': False,
                    'message': f"No valid images found. Errors: {validation_result['invalid']}"
                }
            
            logger.info(f"Validated {len(valid_images)} images")
            
            # Step 3: Encode images with batch ID
            logger.info("Step 3: Encoding images...")
            if methods is None:
                methods = ['LSB', 'DCT', 'DWT']
            
            encode_result = batch_encode_images(
                valid_images,
                secret_message,
                methods=methods,
                encrypt=encrypt,
                encrypt_password=encrypt_password,
                batch_id=batch_id  # <-- PASS BATCH ID
            )
            
            if not encode_result['success']:
                logger.error(f"Encoding failed: {encode_result['message']}")
            
            # Log the batch encoding operation
            try:
                log_operation(
                    username=username,
                    operation_type='batch_encode',
                    method=','.join(methods),
                    image_count=len(valid_images),
                    success=encode_result['success']
                )
            except Exception as e:
                logger.warning(f"Could not log operation: {str(e)}")
            
            # Step 4: Generate reports (in batch-specific folder)
            logger.info("Step 4: Generating reports...")
            batch_report_dir = Path(encode_result['output_path']).parent / 'reports'
            batch_report_dir.mkdir(parents=True, exist_ok=True)
            
            report_json = generate_batch_report(encode_result, f"{batch_id}_report")
            report_csv = generate_csv_report(encode_result, f"{batch_id}_report")
            
            # Step 5: Cleanup extracted images
            logger.info("Step 5: Cleaning up...")
            cleanup_result = cleanup_extracted(str(self.input_images_path))
            
            # Prepare final result
            final_result = {
                'success': encode_result['success'],
                'batch_id': batch_id,
                'zip_file': str(zip_path),
                'extracted_images': len(image_paths),
                'valid_images': len(valid_images),
                'output_path': encode_result['output_path'],
                'processing_results': encode_result,
                'report_json': report_json['report_path'] if report_json['success'] else None,
                'report_csv': report_csv['report_path'] if report_csv['success'] else None,
                'summary': export_summary(encode_result),
                'message': f"Batch processing complete: {encode_result['total_processed']} processed, {encode_result['total_failed']} failed"
            }
            
            self.current_batch = final_result
            logger.info(f"Batch {batch_id} processing complete: {final_result['message']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"Batch processing failed: {str(e)}"
            }
    
    def process_image_batch(
        self,
        image_paths: List[str],
        secret_message: str,
        methods: List[str] = None,
        encrypt: bool = False,
        encrypt_password: str = None,
        username: str = 'batch_user'  # Add username parameter
    ) -> dict:
        """
        Process batch of individual images.
        
        Args:
            image_paths (list): List of image file paths
            secret_message (str): Message to encode
            methods (list): Encoding methods
            encrypt (bool): Apply encryption
            encrypt_password (str): Encryption password
        
        Returns:
            dict: Batch processing results
        """
        try:
            logger.info(f"Starting image batch processing: {len(image_paths)} images")
            
            # Validate paths exist
            valid_paths = []
            for path in image_paths:
                p = Path(path)
                if p.exists():
                    valid_paths.append(str(p.absolute()))
                else:
                    logger.warning(f"Image not found: {path}")
            
            if not valid_paths:
                return {
                    'success': False,
                    'message': "❌ No valid image paths provided"
                }
            
            # Validate images
            logger.info("Validating images...")
            validation_result = validate_images(valid_paths)
            valid_images = validation_result['valid']
            
            if not valid_images:
                return {
                    'success': False,
                    'message': f"❌ No valid images. Errors: {validation_result['invalid']}"
                }
            
            logger.info(f"Validated {len(valid_images)} images")
            
            # Encode
            logger.info("Encoding images...")
            if methods is None:
                methods = ['LSB', 'DCT', 'DWT']
            
            encode_result = batch_encode_images(
                valid_images,
                secret_message,
                methods=methods,
                encrypt=encrypt,
                encrypt_password=encrypt_password
            )
            
            # Log the batch encoding operation
            log_operation(
                username=username,
                operation_type='batch_encode',
                method=','.join(methods),
                image_count=len(valid_images),
                success=encode_result['success']
            )
            
            # Generate reports
            logger.info("Generating reports...")
            report_json = generate_batch_report(encode_result, "batch_images")
            report_csv = generate_csv_report(encode_result, "batch_images")
            
            final_result = {
                'success': encode_result['success'],
                'input_images': len(image_paths),
                'valid_images': len(valid_images),
                'processing_results': encode_result,
                'report_json': report_json['report_path'] if report_json['success'] else None,
                'report_csv': report_csv['report_path'] if report_csv['success'] else None,
                'summary': export_summary(encode_result),
                'message': f"✅ Batch complete: {encode_result['total_processed']} processed, {encode_result['total_failed']} failed"
            }
            
            self.current_batch = final_result
            logger.info(f"Image batch processing complete: {final_result['message']}")
            return final_result
        
        except Exception as e:
            logger.error(f"Image batch processing failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Image batch processing failed: {str(e)}"
            }
    
    def get_batch_status(self) -> dict:
        """
        Get status of current batch.
        
        Returns:
            dict: Current batch information
        """
        if self.current_batch is None:
            return {'message': 'No active batch'}
        
        return self.current_batch
    
    def get_processing_stats(self) -> dict:
        """
        Get statistics from last batch.
        
        Returns:
            dict: Processing statistics
        """
        if self.current_batch is None:
            return {}
        
        return self.current_batch.get('summary', {})
