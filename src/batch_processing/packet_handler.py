# src/batch_processing/packet_handler.py
"""
Packet Handler Module
=====================
Handles message packetization for distributed steganography.
Splits messages into packets and reconstructs them from multiple images.
"""

import json
import logging
import math
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Packet header format: JSON with metadata
HEADER_DELIMITER = "|||PACKET_HEADER|||"
PAYLOAD_DELIMITER = "|||PAYLOAD|||"


def create_packet_header(packet_id: int, total_packets: int, payload_length: int, checksum: str = "") -> str:
    """
    Create a packet header with metadata.
    
    Args:
        packet_id: Zero-indexed packet number
        total_packets: Total number of packets
        payload_length: Length of the payload in this packet
        checksum: Optional checksum for verification
    
    Returns:
        str: JSON header string
    """
    header = {
        "packet_id": packet_id,                     #Packet ID            
        "total_packets": total_packets,             #Total Packets
        "payload_length": payload_length,           #Payload Length
        "checksum": checksum                        #Checksum  
    }
    return json.dumps(header)


def parse_packet_header(header_str: str) -> Optional[dict]:
    """
    Parse a packet header from string.
    
    Args:
        header_str: JSON header string
    
    Returns:
        dict: Parsed header or None if invalid
    """
    try:
        header = json.loads(header_str)
        required_keys = ["packet_id", "total_packets", "payload_length"]
        if all(key in header for key in required_keys):
            return header
        return None
    except json.JSONDecodeError:
        return None


def calculate_checksum(data: str) -> str:
    """Calculate simple checksum for data verification."""
    import hashlib
    return hashlib.md5(data.encode('utf-8')).hexdigest()[:8]


def is_packetized_message(message: str) -> bool:
    """
    Check if a message is a packetized message (contains packet headers).
    
    Args:
        message: The decoded message to check
    
    Returns:
        bool: True if message contains packet header markers
    """
    return HEADER_DELIMITER in message and PAYLOAD_DELIMITER in message


def packetize_message(message: str, num_packets: int) -> List[str]:
    """
    Split a message into equal packets with metadata.
    
    Args:
        message: The complete secret message
        num_packets: Number of packets (should equal number of images)
    
    Returns:
        List of packet strings ready for embedding
    """
    if num_packets < 2:
        raise ValueError("Packetized mode requires at least 2 images")
    
    # Calculate packet size (ceiling division for last packet padding)
    packet_size = math.ceil(len(message) / num_packets)
    
    packets = []
    for i in range(num_packets):
        start_idx = i * packet_size
        end_idx = min(start_idx + packet_size, len(message))
        payload = message[start_idx:end_idx]
        
        # Pad last packet if needed
        if len(payload) < packet_size and i < num_packets - 1:
            payload = payload.ljust(packet_size, '\x00')
        
        # Create header
        checksum = calculate_checksum(payload)
        header = create_packet_header(
            packet_id=i,
            total_packets=num_packets,
            payload_length=len(payload.rstrip('\x00')),
            checksum=checksum
        )
        
        # Combine header and payload
        packet = f"{HEADER_DELIMITER}{header}{PAYLOAD_DELIMITER}{payload}"
        packets.append(packet)
        
        logger.debug(f"Created packet {i+1}/{num_packets}: {len(payload)} chars")
    
    return packets


def extract_packet_data(encoded_message: str) -> Optional[Tuple[dict, str]]:
    """
    Extract header and payload from a decoded packet.
    
    Args:
        encoded_message: The decoded message from an image
    
    Returns:
        Tuple of (header_dict, payload) or None if not a valid packet
    """
    try:
        if HEADER_DELIMITER not in encoded_message:
            return None
        
        # Find header start
        header_start = encoded_message.find(HEADER_DELIMITER) + len(HEADER_DELIMITER)
        payload_marker = encoded_message.find(PAYLOAD_DELIMITER)
        
        if payload_marker == -1:
            return None
        
        header_str = encoded_message[header_start:payload_marker]
        payload = encoded_message[payload_marker + len(PAYLOAD_DELIMITER):]
        
        header = parse_packet_header(header_str)
        if header is None:
            return None
        
        # Trim payload to declared length
        actual_payload = payload[:header["payload_length"]]
        
        return header, actual_payload
    
    except Exception as e:
        logger.error(f"Failed to extract packet data: {e}")
        return None


def reconstruct_message(packets: List[Tuple[dict, str]]) -> Tuple[bool, str, str]:
    """
    Reconstruct the original message from decoded packets.
    
    Args:
        packets: List of (header, payload) tuples
    
    Returns:
        Tuple of (success, message_or_error, details)
    """
    if not packets:
        return False, "", "No packets provided"
    
    # Get total packet count from first packet
    total_packets = packets[0][0]["total_packets"]
    
    # Validate we have all packets
    packet_ids = {p[0]["packet_id"] for p in packets}
    expected_ids = set(range(total_packets))
    
    missing_ids = expected_ids - packet_ids
    if missing_ids:
        return False, "", f"Missing packets: {sorted(missing_ids)}"
    
    # Check for duplicates
    if len(packets) != total_packets:
        return False, "", f"Expected {total_packets} packets, got {len(packets)}"
    
    # Sort by packet_id and reconstruct
    sorted_packets = sorted(packets, key=lambda x: x[0]["packet_id"])
    
    # Verify checksums and reconstruct
    message_parts = []
    for header, payload in sorted_packets:
        expected_checksum = header.get("checksum", "")
        if expected_checksum and calculate_checksum(payload) != expected_checksum:
            logger.warning(f"Checksum mismatch for packet {header['packet_id']}")
        message_parts.append(payload)
    
    reconstructed = "".join(message_parts)
    
    return True, reconstructed, f"Successfully reconstructed from {total_packets} packets"


def get_packet_map(image_filenames: List[str], packets: List[str]) -> dict:
    """
    Create a mapping of images to their packet assignments.
    
    Args:
        image_filenames: Sorted list of image filenames
        packets: List of packet strings
    
    Returns:
        dict: Mapping of filename to packet info
    """
    if len(image_filenames) != len(packets):
        raise ValueError("Number of images must match number of packets")
    
    packet_map = {}
    for idx, (filename, packet) in enumerate(zip(image_filenames, packets)):
        packet_map[filename] = {
            "packet_id": idx,
            "total_packets": len(packets),
            "packet_preview": packet[:50] + "..." if len(packet) > 50 else packet
        }
    
    return packet_map