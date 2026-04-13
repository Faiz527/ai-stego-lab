"""
Report Generator Module
=======================
Creates batch processing reports in JSON and CSV formats.
Generates timing benchmarks and processing summaries.
"""

import json
import csv
import logging
import os
from datetime import datetime
import zipfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_OUTPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'output' / 'reports'


def generate_batch_report(batch_result: dict, report_name: str = None) -> dict:
    """
    Generate JSON report for batch processing.
    
    Args:
        batch_result (dict): Result from batch_encode_images
        report_name (str): Custom report name
    
    Returns:
        dict: Report information
    """
    try:
        os.makedirs(DATA_OUTPUT_PATH, exist_ok=True)
        
        if report_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_name = f"batch_report_{timestamp}"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_processed': batch_result['total_processed'],
                'total_failed': batch_result['total_failed'],
                'methods_used': batch_result['methods_used'],
                'success': batch_result['success']
            },
            'results': batch_result['results'],
            'timings': calculate_timings(batch_result['results'])
        }
        
        report_path = DATA_OUTPUT_PATH / f"{report_name}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Report generated: {report_path}")
        
        return {
            'success': True,
            'report_path': str(report_path),
            'message': f"✅ Report saved: {report_path}"
        }
    
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return {
            'success': False,
            'message': f"❌ Report generation failed: {str(e)}"
        }


def generate_csv_report(batch_result: dict, report_name: str = None) -> dict:
    """
    Generate CSV report for batch processing.
    
    Args:
        batch_result (dict): Result from batch_encode_images
        report_name (str): Custom report name
    
    Returns:
        dict: Report information
    """
    try:
        os.makedirs(DATA_OUTPUT_PATH, exist_ok=True)
        
        if report_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_name = f"batch_report_{timestamp}"
        
        report_path = DATA_OUTPUT_PATH / f"{report_name}.csv"
        
        # Flatten results for CSV
        rows = []
        for method, results in batch_result['results'].items():
            for item in results:
                row = {
                    'Method': method,
                    'Filename': item.get('filename', 'N/A'),
                    'Status': item.get('status', 'N/A'),
                    'Encoding_Time_s': item.get('encoding_time', 'N/A'),
                    'Image_Size': item.get('size', 'N/A'),
                    'Output_Path': item.get('output_path', 'N/A')
                }
                rows.append(row)
        
        if rows:
            with open(report_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            
            logger.info(f"CSV report generated: {report_path}")
            
            return {
                'success': True,
                'report_path': str(report_path),
                'message': f"✅ CSV report saved: {report_path}"
            }
        else:
            return {
                'success': False,
                'message': "❌ No data to generate CSV report"
            }
    
    except Exception as e:
        logger.error(f"CSV report generation failed: {str(e)}")
        return {
            'success': False,
            'message': f"❌ CSV report generation failed: {str(e)}"
        }


def calculate_timings(results: dict) -> dict:
    """
    Calculate timing statistics from batch results.
    
    Args:
        results (dict): Results by method
    
    Returns:
        dict: Timing statistics
    """
    timings = {}
    
    for method, items in results.items():
        times = [item['encoding_time'] for item in items if 'encoding_time' in item]
        
        if times:
            timings[method] = {
                'min': round(min(times), 3),
                'max': round(max(times), 3),
                'avg': round(sum(times) / len(times), 3),
                'total': round(sum(times), 3),
                'count': len(times)
            }
    
    return timings


def export_summary(batch_result: dict) -> dict:
    """
    Export summary of batch processing.
    
    Args:
        batch_result (dict): Result from batch_encode_images
    
    Returns:
        dict: Summary data
    """
    summary = {
        'processed': batch_result['total_processed'],
        'failed': batch_result['total_failed'],
        'methods': batch_result['methods_used'],
        'timestamp': datetime.now().isoformat(),
        'details': {}
    }
    
    for method, results in batch_result['results'].items():
        successful = [r for r in results if r.get('status', '').startswith('✅')]
        summary['details'][method] = {
            'successful': len(successful),
            'failed': len(results) - len(successful),
            'success_rate': f"{(len(successful) / len(results) * 100):.1f}%" if results else "0%"
        }
    
    return summary


def create_batch_download_zip(batch_result: dict, method: str = None) -> str:
    """
    Create a ZIP file of encoded images from current batch.
    Uses batch-specific output directory.
    
    Args:
        batch_result (dict): Result from batch_encode_images
        method (str): Specific method to zip, or None for all
    
    Returns:
        str: Path to created ZIP file
    """
    try:
        import tempfile
        import zipfile
        
        # Use the batch-specific output path from result
        base_output = Path(batch_result.get('output_path', Path(__file__).parent.parent.parent / 'data' / 'output' / 'encoded'))
        
        # Extract batch ID from output path for ZIP filename
        # Path structure: .../batches/batch_XXXXXXX_XXXXXXXX/encoded
        # So parent.name gives us the batch ID
        batch_id = base_output.parent.name  # Get batch_XXXXXXX_XXXXXXXX from path
        
        # Create temporary ZIP file
        temp_dir = tempfile.gettempdir()
        zip_path = Path(temp_dir) / f"batch_encoded_{batch_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if method:
                # Add specific method's images - search for all image formats
                method_dir = base_output / method
                if method_dir.exists():
                    # Look for all common image formats
                    image_patterns = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff']
                    for pattern in image_patterns:
                        for image_file in method_dir.glob(pattern):
                            arcname = f"{method}/{image_file.name}"
                            zipf.write(image_file, arcname=arcname)
            else:
                # Add all images from all methods in the batch output directory
                for method_dir in base_output.iterdir():
                    if method_dir.is_dir() and method_dir.name in ['LSB', 'DCT', 'DWT']:
                        # Look for all common image formats
                        image_patterns = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff']
                        for pattern in image_patterns:
                            for image_file in method_dir.glob(pattern):
                                arcname = f"{method_dir.name}/{image_file.name}"
                                zipf.write(image_file, arcname=arcname)
        
        logger.info(f"Batch download ZIP created: {zip_path}")
        return str(zip_path)
        
    except Exception as e:
        logger.error(f"Failed to create batch download ZIP: {str(e)}")
        raise
