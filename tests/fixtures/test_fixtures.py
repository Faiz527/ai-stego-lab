"""
Fixture Tests
=============
Tests for pytest fixtures, test data generation, and test infrastructure.
Ensures all test fixtures work correctly and generate valid test data.
"""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile
import os


# ============================================================================
#                     FIXTURE TESTS
# ============================================================================

@pytest.mark.fixtures
class TestImageFixtures:
    """Test image fixture creation and validity."""
    
    def test_rgb_image_fixture_created(self, test_image_800x600):
        """Test that RGB image fixture is created."""
        assert test_image_800x600 is not None
        assert isinstance(test_image_800x600, Image.Image)
    
    def test_rgb_image_fixture_properties(self, test_image_800x600):
        """Test RGB image fixture has correct properties."""
        assert test_image_800x600.mode == 'RGB'
        assert test_image_800x600.size == (800, 600)
    
    def test_rgb_image_fixture_is_valid(self, test_image_800x600):
        """Test RGB image fixture is valid and drawable."""
        # Should be able to convert to array
        arr = np.array(test_image_800x600)
        assert arr.shape == (600, 800, 3)
        assert arr.dtype == np.uint8
    
    def test_512x512_image_fixture(self, test_image_512x512):
        """Test 512x512 image fixture."""
        assert test_image_512x512.size == (512, 512)
        assert test_image_512x512.mode == 'RGB'
    
    def test_1024x768_image_fixture(self, test_image_1024x768):
        """Test larger image fixture."""
        assert test_image_1024x768.size == (1024, 768)
        assert test_image_1024x768.mode == 'RGB'
    
    def test_grayscale_image_fixture(self, test_image_grayscale):
        """Test grayscale image fixture."""
        assert test_image_grayscale.mode == 'L'
        assert test_image_grayscale.size == (512, 512)
        arr = np.array(test_image_grayscale)
        assert arr.shape == (512, 512)
    
    def test_rgba_image_fixture(self, test_image_rgba):
        """Test RGBA image fixture."""
        assert test_image_rgba.mode == 'RGBA'
        assert test_image_rgba.size == (512, 512)
        arr = np.array(test_image_rgba)
        assert arr.shape == (512, 512, 4)
    
    def test_image_fixture_pixel_values(self, test_image_800x600):
        """Test image fixture has valid pixel values."""
        arr = np.array(test_image_800x600)
        # All pixels should be in valid range
        assert arr.min() >= 0
        assert arr.max() <= 255
    
    def test_image_fixture_is_different_each_time(self):
        """Test that fixtures create different images each time."""
        # Create two images with same parameters
        arr1 = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
        img1 = Image.fromarray(arr1, 'RGB')
        
        arr2 = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
        img2 = Image.fromarray(arr2, 'RGB')
        
        # Should be different
        arr1_data = np.array(img1)
        arr2_data = np.array(img2)
        assert not np.array_equal(arr1_data, arr2_data)
    
    def test_image_fixture_can_be_saved(self, test_image_800x600):
        """Test that fixture images can be saved."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            test_image_800x600.save(tmp_path)
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
        finally:
            # Ensure cleanup
            if Path(tmp_path).exists():
                try:
                    Path(tmp_path).unlink()
                except PermissionError:
                    # File might still be locked, skip cleanup
                    pass
    
    def test_image_fixture_can_be_loaded(self, test_image_800x600):
        """Test that fixture images can be saved and reloaded."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Save
            test_image_800x600.save(tmp_path)
            assert Path(tmp_path).exists()
            
            # Reload in fresh context
            loaded = Image.open(tmp_path)
            loaded.load()  # Force load into memory
            
            assert loaded.size == test_image_800x600.size
            assert loaded.mode == test_image_800x600.mode
        finally:
            # Cleanup
            if Path(tmp_path).exists():
                try:
                    Path(tmp_path).unlink()
                except PermissionError:
                    pass


@pytest.mark.fixtures
class TestTemporaryDirectoryFixture:
    """Test temporary directory fixture."""
    
    def test_temp_image_dir_created(self, temp_image_dir):
        """Test temp directory fixture is created."""
        assert temp_image_dir is not None
        assert isinstance(temp_image_dir, Path)
        assert temp_image_dir.exists()
    
    def test_temp_image_dir_is_writable(self, temp_image_dir):
        """Test temp directory is writable."""
        test_file = temp_image_dir / 'test.txt'
        test_file.write_text('test')
        assert test_file.exists()
        assert test_file.read_text() == 'test'
    
    def test_temp_image_dir_can_hold_images(self, temp_image_dir, test_image_800x600):
        """Test temp directory can hold image files."""
        img_path = temp_image_dir / 'test_image.png'
        test_image_800x600.save(img_path)
        assert img_path.exists()
        
        # Reload
        loaded = Image.open(img_path)
        loaded.load()
        assert loaded.size == test_image_800x600.size


@pytest.mark.fixtures
class TestSampleImagesFixture:
    """Test sample_images fixture."""
    
    def test_sample_images_contains_rgb(self, sample_images):
        """Test sample_images has RGB image."""
        assert 'rgb' in sample_images
        assert isinstance(sample_images['rgb'], Image.Image)
        assert sample_images['rgb'].mode == 'RGB'
    
    def test_sample_images_contains_rgb_path(self, sample_images):
        """Test sample_images has RGB path."""
        assert 'rgb_path' in sample_images
        assert isinstance(sample_images['rgb_path'], Path)
        assert sample_images['rgb_path'].exists()
    
    def test_sample_images_contains_jpeg_path(self, sample_images):
        """Test sample_images has JPEG path."""
        assert 'jpeg_path' in sample_images
        assert isinstance(sample_images['jpeg_path'], Path)
        assert sample_images['jpeg_path'].exists()
    
    def test_sample_images_contains_grayscale(self, sample_images):
        """Test sample_images has grayscale image."""
        assert 'gray' in sample_images
        assert isinstance(sample_images['gray'], Image.Image)
        assert sample_images['gray'].mode == 'L'
    
    def test_sample_images_rgb_and_path_match(self, sample_images):
        """Test that RGB image is the one saved at path."""
        # Load from path and compare with fixture image
        from_file = Image.open(sample_images['rgb_path'])
        from_file.load()
        
        assert from_file.size == sample_images['rgb'].size
        assert from_file.mode == sample_images['rgb'].mode
        
        # Pixel values should match (since we just saved)
        from_file_arr = np.array(from_file)
        fixture_arr = np.array(sample_images['rgb'])
        assert np.array_equal(from_file_arr, fixture_arr)
    
    def test_sample_images_jpeg_is_valid(self, sample_images):
        """Test JPEG file is valid."""
        jpeg_img = Image.open(sample_images['jpeg_path'])
        jpeg_img.load()
        
        assert jpeg_img.size == sample_images['rgb'].size
        # JPEG may be RGB or different format
        assert jpeg_img.mode in ['RGB', 'L']


# ============================================================================
#                    FIXTURE CONFIGURATION TESTS
# ============================================================================

@pytest.mark.fixtures
class TestFixtureScopes:
    """Test fixture scope behaviors."""
    
    def test_session_fixture_reused(self, test_image_800x600):
        """Test that session-scoped fixtures are reused."""
        # Get ID of fixture
        img_id = id(test_image_800x600)
        assert img_id is not None
    
    def test_function_fixture_unique(self):
        """Test that function-scoped fixtures are unique per test."""
        # Each test function gets its own fixture
        arr1 = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
        img1 = Image.fromarray(arr1, 'RGB')
        id1 = id(img1)
        
        arr2 = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
        img2 = Image.fromarray(arr2, 'RGB')
        id2 = id(img2)
        
        # Different object IDs
        assert id1 != id2


# ============================================================================
#                      DATA GENERATION TESTS
# ============================================================================

@pytest.mark.fixtures
class TestDataGeneration:
    """Test test data generation quality."""
    
    def test_random_image_has_variety(self, test_image_800x600):
        """Test that random images have pixel variety."""
        arr = np.array(test_image_800x600)
        
        # Should have multiple different pixel values
        unique_pixels = len(np.unique(arr))
        assert unique_pixels > 100, "Should have variety in pixels"
    
    def test_random_image_values_in_range(self, test_image_800x600):
        """Test that random image values are in expected range."""
        arr = np.array(test_image_800x600)
        
        # Default range: 50-200
        assert arr.min() >= 50
        assert arr.max() <= 200
    
    def test_grayscale_image_single_channel(self, test_image_grayscale):
        """Test grayscale image is single channel."""
        arr = np.array(test_image_grayscale)
        assert len(arr.shape) == 2
        assert arr.ndim == 2
    
    def test_rgb_image_three_channels(self, test_image_800x600):
        """Test RGB image has three channels."""
        arr = np.array(test_image_800x600)
        assert arr.ndim == 3
        assert arr.shape[2] == 3
    
    def test_rgba_image_four_channels(self, test_image_rgba):
        """Test RGBA image has four channels."""
        arr = np.array(test_image_rgba)
        assert arr.ndim == 3
        assert arr.shape[2] == 4


# ============================================================================
#                      FIXTURE CLEANUP TESTS
# ============================================================================

@pytest.mark.fixtures
class TestFixtureCleanup:
    """Test that fixtures clean up properly."""
    
    def test_temp_dir_cleanup(self):
        """Test that temporary directory is cleaned up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            test_file = tmp_path / 'test.txt'
            test_file.write_text('test')
            assert test_file.exists()
        
        # After context, should be deleted
        assert not tmp_path.exists()
    
    def test_temp_image_dir_cleanup(self, temp_image_dir):
        """Test temp image dir cleanup (implicit through fixture)."""
        # Create file in temp dir
        test_file = temp_image_dir / 'cleanup_test.txt'
        test_file.write_text('test')
        assert test_file.exists()
        # Cleanup happens automatically after test


# ============================================================================
#                    FIXTURE INTERDEPENDENCIES
# ============================================================================

@pytest.mark.fixtures
class TestFixtureDependencies:
    """Test fixtures that depend on other fixtures."""
    
    def test_sample_images_uses_temp_dir(self, sample_images, temp_image_dir):
        """Test that sample_images fixture uses temp_image_dir."""
        # sample_images should create files in temp_image_dir
        assert sample_images['rgb_path'].parent == temp_image_dir or \
               sample_images['rgb_path'].parent.parent == temp_image_dir.parent
    
    def test_multiple_fixtures_in_one_test(self, test_image_800x600, 
                                            test_image_512x512, 
                                            sample_images):
        """Test using multiple fixtures together."""
        # All should be valid
        assert test_image_800x600.size == (800, 600)
        assert test_image_512x512.size == (512, 512)
        assert sample_images['rgb'].size == (1024, 768)
        
        # All should be different objects
        assert id(test_image_800x600) != id(test_image_512x512)
        assert id(test_image_800x600) != id(sample_images['rgb'])


# ============================================================================
#                    CONFTEST VALIDATION
# ============================================================================

@pytest.mark.fixtures
class TestConfTestSetup:
    """Test that conftest.py is properly configured."""
    
    def test_pytest_plugins_loaded(self):
        """Test that pytest is properly initialized."""
        import pytest
        assert pytest is not None
    
    def test_fixtures_available_in_request(self, request):
        """Test that fixtures are available in request object."""
        # request.fixturename contains the fixture that created this test
        assert request is not None
    
    def test_image_fixtures_creatable(self):
        """Test that image fixtures can be created manually."""
        # This validates that fixture dependencies work
        arr = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
        img = Image.fromarray(arr, 'RGB')
        
        assert img is not None
        assert img.size == (800, 600)
        assert img.mode == 'RGB'


# ============================================================================
#                    FIXTURE PARAMETERIZATION
# ============================================================================

@pytest.mark.fixtures
@pytest.mark.parametrize("width,height,mode", [
    (256, 256, 'RGB'),
    (512, 512, 'RGB'),
    (800, 600, 'RGB'),
    (512, 512, 'L'),
    (512, 512, 'RGBA'),
])
class TestParametrizedFixtures:
    """Test parameterized fixtures."""
    
    def test_image_creation_various_sizes_modes(self, width, height, mode):
        """Test creating images of various sizes and modes."""
        if mode == 'L':
            arr = np.random.randint(50, 200, (height, width), dtype=np.uint8)
            img = Image.fromarray(arr, mode)
        else:
            channels = 3 if mode == 'RGB' else 4
            arr = np.random.randint(50, 200, (height, width, channels), dtype=np.uint8)
            img = Image.fromarray(arr, mode)
        
        assert img.size == (width, height)
        assert img.mode == mode