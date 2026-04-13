"""UI module - Refactored with centralized config and reusable components"""

from .config_dict import (
    METHODS, METHOD_DETAILS, FORM_LABELS, ERROR_MESSAGES, SUCCESS_MESSAGES,
    SECTION_HEADERS, TAB_NAMES, BUTTON_LABELS, COMPARISON_TABLE,
    DOWNLOAD_FILENAMES, VALIDATION, METRIC_LABELS
)
from .reusable_components import (
    create_text_input, create_text_area, create_file_uploader,
    create_method_selector, create_checkbox, show_error, show_success,
    validate_credentials, validate_registration, create_two_column_layout,
    create_three_column_layout, create_metric_cards, display_image_comparison,
    display_encoded_image, display_decoded_message, create_primary_button,
    create_download_button, create_tab_section, display_results_summary,
    show_divider, show_method_details, create_comparison_table,
    show_activity_search, create_batch_upload_section, create_batch_options_section,
    display_batch_results, display_detailed_results, display_progress_indicator
)
from .ui_components import (
    show_encode_section,
    show_decode_section,
    show_comparison_section,
    show_auth_section,
    show_batch_processing_section,
    show_pixel_selector_section,
    show_redundancy_section
)
from .styles import apply_dark_theme

__all__ = [
    # Config exports
    'METHODS', 'METHOD_DETAILS', 'FORM_LABELS', 'ERROR_MESSAGES', 
    'SUCCESS_MESSAGES', 'SECTION_HEADERS', 'TAB_NAMES', 'BUTTON_LABELS',
    'COMPARISON_TABLE', 'DOWNLOAD_FILENAMES', 'VALIDATION', 'METRIC_LABELS',
    
    # Reusable components
    'create_text_input', 'create_text_area', 'create_file_uploader',
    'create_method_selector', 'create_checkbox', 'show_error', 'show_success',
    'validate_credentials', 'validate_registration', 'create_two_column_layout',
    'create_three_column_layout', 'create_metric_cards', 'display_image_comparison',
    'display_encoded_image', 'display_decoded_message', 'create_primary_button',
    'create_download_button', 'create_tab_section', 'display_results_summary',
    'show_divider', 'show_method_details', 'create_comparison_table',
    'show_activity_search', 'create_batch_upload_section', 'create_batch_options_section',
    'display_batch_results', 'display_detailed_results', 'display_progress_indicator',
    
    # Main UI sections
    'show_encode_section', 'show_decode_section', 'show_comparison_section',
    'show_auth_section', 'show_batch_processing_section',
    'show_pixel_selector_section', 'show_redundancy_section',
    
    # Styles
    'apply_dark_theme'
]
