"""
Test Data Fixtures
==================
Provides utility classes for generating test images and data.
"""

from PIL import Image
import numpy as np
import random


class TestImageGenerator:
    """Generate test images for steganography testing."""
    
    @staticmethod
    def create_random_image(width=1024, height=768, mode='RGB'):
        """
        Create a random RGB image for testing.
        
        Args:
            width (int): Image width in pixels
            height (int): Image height in pixels
            mode (str): Image mode ('RGB', 'L', 'RGBA')
        
        Returns:
            PIL.Image: Random image
        """
        if mode == 'RGB':
            # Generate random RGB data
            img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            return Image.fromarray(img_array, 'RGB')
        
        elif mode == 'L':
            # Generate random grayscale data
            img_array = np.random.randint(0, 256, (height, width), dtype=np.uint8)
            return Image.fromarray(img_array, 'L')
        
        elif mode == 'RGBA':
            # Generate random RGBA data
            img_array = np.random.randint(0, 256, (height, width, 4), dtype=np.uint8)
            return Image.fromarray(img_array, 'RGBA')
        
        else:
            raise ValueError(f"Unsupported image mode: {mode}")
    
    @staticmethod
    def create_gradient_image(width=1024, height=768):
        """
        Create a gradient image (deterministic for reproducible tests).
        
        Args:
            width (int): Image width
            height (int): Image height
        
        Returns:
            PIL.Image: Gradient image
        """
        # Create gradient from black to white
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        
        for i in range(height):
            for j in range(width):
                value = int((i + j) / (height + width) * 255)
                gradient[i, j] = [value, value, value]
        
        return Image.fromarray(gradient, 'RGB')
    
    @staticmethod
    def create_solid_color_image(width=1024, height=768, color=(128, 128, 128)):
        """
        Create a solid color image.
        
        Args:
            width (int): Image width
            height (int): Image height
            color (tuple): RGB color tuple
        
        Returns:
            PIL.Image: Solid color image
        """
        img_array = np.full((height, width, 3), color, dtype=np.uint8)
        return Image.fromarray(img_array, 'RGB')
    
    @staticmethod
    def create_pattern_image(width=1024, height=768, pattern='checkerboard'):
        """
        Create a patterned image.
        
        Args:
            width (int): Image width
            height (int): Image height
            pattern (str): Pattern type ('checkerboard', 'stripes', 'dots')
        
        Returns:
            PIL.Image: Patterned image
        """
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        if pattern == 'checkerboard':
            square_size = 16
            for i in range(height):
                for j in range(width):
                    if ((i // square_size) + (j // square_size)) % 2 == 0:
                        img_array[i, j] = [255, 255, 255]
                    else:
                        img_array[i, j] = [0, 0, 0]
        
        elif pattern == 'stripes':
            stripe_width = 16
            for i in range(height):
                for j in range(width):
                    if (j // stripe_width) % 2 == 0:
                        img_array[i, j] = [255, 255, 255]
                    else:
                        img_array[i, j] = [0, 0, 0]
        
        elif pattern == 'dots':
            dot_size = 8
            spacing = 16
            for i in range(height):
                for j in range(width):
                    if ((i % spacing) < dot_size) and ((j % spacing) < dot_size):
                        img_array[i, j] = [255, 0, 0]
                    else:
                        img_array[i, j] = [200, 200, 200]
        
        return Image.fromarray(img_array, 'RGB')
    
    @staticmethod
    def create_natural_like_image(width=1024, height=768):
        """
        Create a more natural-looking image using Perlin noise-like patterns.
        
        Args:
            width (int): Image width
            height (int): Image height
        
        Returns:
            PIL.Image: Natural-looking image
        """
        # Create RGB channels separately with some correlation
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Generate base noise
        base_noise = np.random.randint(50, 200, (height, width), dtype=np.uint8)
        
        # Create channels with slight variations
        img_array[:, :, 0] = base_noise  # Red channel
        img_array[:, :, 1] = np.clip(
            base_noise.astype(int) + np.random.randint(-20, 20, (height, width)), 
            0, 255
        ).astype(np.uint8)  # Green
        img_array[:, :, 2] = np.clip(
            base_noise.astype(int) + np.random.randint(-20, 20, (height, width)), 
            0, 255
        ).astype(np.uint8)  # Blue
        
        return Image.fromarray(img_array, 'RGB')


class TestDataGenerator:
    """Generate test data (messages, passwords, etc.)."""
    
    @staticmethod
    def generate_random_message(length=100, charset='ascii'):
        """
        Generate a random message.
        
        Args:
            length (int): Message length
            charset (str): Character set ('ascii', 'unicode', 'emoji')
        
        Returns:
            str: Random message
        """
        if charset == 'ascii':
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !?.'
            return ''.join(random.choice(chars) for _ in range(length))
        
        elif charset == 'unicode':
            # Mix of ASCII and unicode characters
            chars = 'abcdefghijklmnop世界日本中文العربيةРусскийქართული🌍🔒🎉'
            return ''.join(random.choice(chars) for _ in range(length))
        
        elif charset == 'emoji':
            emojis = '😀😃😄😁😆😅🤣😂😉😊😇🙂🙃😌😍🥰😘😗'
            return ''.join(random.choice(emojis) for _ in range(length))
        
        else:
            raise ValueError(f"Unknown charset: {charset}")
    
    @staticmethod
    def generate_password(length=16):
        """
        Generate a random password.
        
        Args:
            length (int): Password length
        
        Returns:
            str: Random password
        """
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return ''.join(random.choice(chars) for _ in range(length))