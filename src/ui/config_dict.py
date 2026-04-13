"""
UI Configuration Dictionary
============================
Centralized configuration for all UI components.
Contains all constants, strings, and styling configs.
"""

# Steganography Methods
METHODS = ["LSB", "Hybrid DCT", "Hybrid DWT"]

# Method Details Configuration
METHOD_DETAILS = {
    "LSB": {
        "name": "Least Significant Bit (LSB)",
        "description": """
**Least Significant Bit (LSB)**
- Replaces least significant bits of pixel values
- Simple and fast implementation
- Large embedding capacity
- Vulnerable to compression and detection
- Best for: Covert communication where quality is not critical
""",
        "capacity": "180 KB",
        "speed": "Very Fast",
        "security": "Low",
        "domain": "Spatial",
        "jpeg_safe": "No",
        "quality_loss": "Minimal"
    },
    "Hybrid DCT": {
        "name": "Hybrid DCT (Y-Channel LSB)",
        "description": """
**Hybrid DCT (Y-Channel LSB)**
- Converts image to YCbCr color space
- Applies DCT on Y channel
- Embeds in AC coefficients using LSB
- JPEG compression safe
- Better security than LSB
- Best for: JPEG images and higher security needs
""",
        "capacity": "60 KB",
        "speed": "Fast",
        "security": "Medium",
        "domain": "Frequency",
        "jpeg_safe": "Yes",
        "quality_loss": "Low"
    },
    "Hybrid DWT": {
        "name": "Hybrid DWT (Haar Wavelet)",
        "description": """
**Hybrid DWT (Haar Wavelet)**
- Applies Haar wavelet transform
- Embeds bits in wavelet coefficients
- High security and imperceptibility
- Lower embedding capacity
- Resistant to attacks
- Best for: Maximum security requirements
""",
        "capacity": "15 KB",
        "speed": "Slow",
        "security": "High",
        "domain": "Frequency",
        "jpeg_safe": "No",
        "quality_loss": "Medium"
    }
}

# Form Labels and Placeholders
FORM_LABELS = {
    "username": {
        "label": "Username",
        "placeholder": "Enter your username"
    },
    "password": {
        "label": "Password",
        "placeholder": "Enter your password"
    },
    "confirm_password": {
        "label": "Confirm Password",
        "placeholder": "Confirm your password"
    },
    "message": {
        "label": "Secret message to encode",
        "max_chars": 1000
    },
    "encryption_password": {
        "label": "Encryption password",
        "placeholder": "Enter encryption password"
    }
}

# File Upload Configuration
FILE_UPLOAD_CONFIG = {
    "images": {
        "label": "Choose an image",
        "types": ["png", "jpg", "jpeg", "bmp"]
    },
    "zip": {
        "label": "Upload ZIP file",
        "types": ["zip"]
    },
    "multiple_images": {
        "label": "Upload multiple images",
        "types": ["png", "jpg", "jpeg", "bmp"]
    }
}

# Error Messages
ERROR_MESSAGES = {
    "empty_fields": "Please enter both username and password",
    "fields_required": "Please fill all fields",
    "passwords_mismatch": "Passwords do not match",
    "min_password_length": "Password must be at least 8 characters",
    "invalid_credentials": "Invalid username or password",
    "username_exists": "Username already exists",
    "no_message": "Please enter a message",
    "no_method": "Please select an encoding method",
    "no_file": "Please upload a file",
    "no_encryption_password": "Please enter encryption password",
    "no_decryption_password": "Please enter decryption password",
    "encoding_failed": "Encoding failed",
    "decoding_failed": "Decoding failed",
    "decode_failed": "No message found in the image",
    "batch_failed": "Batch processing failed"
}

# Success Messages
SUCCESS_MESSAGES = {
    "login": "Welcome back!",
    "login_success": "Welcome back!",
    "register": "Account created successfully! Logging you in...",
    "registration_success": "Account created successfully!",
    "encode": "Message encoded successfully!",
    "encode_success": "Message encoded successfully!",
    "decode": "Message decoded successfully!",
    "decode_success": "Message decoded successfully!",
    "batch_encode": "Batch encoding completed successfully!",
    "batch_encode_success": "Batch encoding completed successfully!",
    "batch_decode": "Batch decoding completed successfully!",
    "batch_decode_success": "Batch decoding completed successfully!"
}

# Section Headers
SECTION_HEADERS = {
    "auth": "🔐 Authentication",
    "encode": "Encode Message into Image",
    "decode": "Decode Message from Image",
    "comparison": "Method Comparison",
    "statistics": "Statistics & Analytics",
    "batch": "Batch Processing"
}

# Tab Names
TAB_NAMES = {
    "auth": ["Login", "Register"],
    "batch": ["Batch Encode", "Batch Decode"],
    "upload": ["ZIP File", "Multiple Images"],
    "method_comparison": ["LSB", "Hybrid DCT", "Hybrid DWT"],
    "statistics": ["Timeline", "Methods", "Distribution", "Activity"]
}

# Button Labels
BUTTON_LABELS = {
    "login": "Login",
    "register": "Register",
    "upload": "Upload Image",
    "download": "Download Encoded Image",
    "decode": "Decode",
    "batch_process": "Start Batch Processing",
    "batch_decode": "Start Batch Decoding",
    "refresh": "🔄 Refresh",
    "download_all_zip": "Download All (ZIP)",
    "download_csv": "Download CSV Report",
    "download_json": "Download JSON Report",
    "download_txt": "Download All Messages (TXT)"
}

# Column Layouts
COLUMN_LAYOUTS = {
    "two_col": 2,
    "three_col": 3,
    "wide_narrow": [2, 1, 1],
    "equal_three": [1, 1, 1]
}

# Metric Labels
METRIC_LABELS = {
    "total_operations": "Total Operations",
    "methods_used": "Methods Used",
    "last_updated": "Last Updated",
    "total_images": "Total Images",
    "successfully_decoded": "Successfully Decoded",
    "failed": "Failed",
    "images_uploaded": "Images Uploaded",
    "images_valid": "Images Valid",
    "images_processed": "Images Processed",
    "images_extracted": "Images Extracted"
}

# Download File Names
DOWNLOAD_FILENAMES = {
    "encoded_image": "encoded_{method}.png",
    "batch_all_zip": "batch_encoded_all.zip",
    "batch_method_zip": "batch_encoded_{method}.zip",
    "batch_report_json": "batch_report.json",
    "batch_report_csv": "batch_report.csv",
    "decoded_txt": "batch_decoded_all.txt",
    "decoded_json": "batch_decoded_messages.json",
    "decode_report_csv": "batch_decode_report.csv",
    "decode_report_json": "batch_decode_report.json"
}

# Comparison Table Data
COMPARISON_TABLE = {
    "Method": ["LSB", "Hybrid DCT", "Hybrid DWT"],
    "Capacity (KB)": [180, 60, 15],
    "Speed": ["Very Fast", "Fast", "Slow"],
    "Security": ["Low", "Medium", "High"],
    "Domain": ["Spatial", "Frequency", "Frequency"],
    "JPEG Safe": ["No", "Yes", "No"],
    "Quality Loss": ["Minimal", "Low", "Medium"]
}

# Validation Config
VALIDATION = {
    "min_password_length": 8,  
    "max_message_chars": 1000
}