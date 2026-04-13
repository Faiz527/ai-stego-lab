"""
Steganography Module
====================
Core steganography engine containing LSB, DCT, and DWT implementations.
"""

from .lsb_steganography import encode_image, decode_image
from .dct_steganography import encode_dct, decode_dct
from .dwt_steganography import encode_dwt, decode_dwt

try:
    from .dwt_steganography import encode_dct_dwt, decode_dct_dwt
except ImportError:
    encode_dct_dwt = encode_dwt
    decode_dct_dwt = decode_dwt

__all__ = [
    'encode_image',
    'decode_image',
    'encode_dct',
    'decode_dct',
    'encode_dwt',
    'decode_dwt',
    'encode_dct_dwt',
    'decode_dct_dwt'
]
