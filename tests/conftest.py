"""
Pytest Configuration & Shared Fixtures
=====================================
Central location for pytest configuration and reusable test fixtures.
"""

import sys
from pathlib import Path
import pytest
import numpy as np
from PIL import Image
import tempfile

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
#                          IMAGE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_image_800x600():
    """Create RGB test image (800×600) - session scope."""
    arr = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
    return Image.fromarray(arr, 'RGB')


@pytest.fixture(scope="session")
def test_image_512x512():
    """Create RGB test image (512×512) - session scope."""
    arr = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
    return Image.fromarray(arr, 'RGB')


@pytest.fixture(scope="session")
def test_image_1024x768():
    """Create larger RGB test image (1024×768) - session scope."""
    arr = np.random.randint(50, 200, (768, 1024, 3), dtype=np.uint8)
    return Image.fromarray(arr, 'RGB')


@pytest.fixture(scope="session")
def test_image_grayscale():
    """Create grayscale test image (512×512) - session scope."""
    arr = np.random.randint(50, 200, (512, 512), dtype=np.uint8)
    return Image.fromarray(arr, 'L')


@pytest.fixture(scope="session")
def test_image_rgba():
    """Create RGBA test image (512×512) - session scope."""
    arr = np.random.randint(50, 200, (512, 512, 4), dtype=np.uint8)
    return Image.fromarray(arr, 'RGBA')


# ============================================================================
#                    TEMPORARY DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_image_dir():
    """Create temporary directory for image files - function scope."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
#                      SAMPLE IMAGES FIXTURE
# ============================================================================

@pytest.fixture
def sample_images(temp_image_dir):
    """Create sample images in various formats - function scope."""
    images = {}
    
    # Create RGB image
    rgb_arr = np.random.randint(50, 200, (768, 1024, 3), dtype=np.uint8)
    rgb_img = Image.fromarray(rgb_arr, 'RGB')
    images['rgb_path'] = temp_image_dir / 'sample_rgb.png'
    rgb_img.save(images['rgb_path'])
    images['rgb'] = rgb_img
    
    # Create JPEG
    jpeg_path = temp_image_dir / 'sample.jpg'
    rgb_img.save(jpeg_path, quality=90)
    images['jpeg_path'] = jpeg_path
    
    # Create grayscale
    gray_arr = np.random.randint(50, 200, (768, 1024), dtype=np.uint8)
    gray_img = Image.fromarray(gray_arr, 'L')
    images['gray'] = gray_img
    
    return images


# ============================================================================
#                      DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def fresh_db():
    """Initialize a fresh database for testing.
    
    Ensures database tables exist before tests run.
    Skips if database is unavailable.
    """
    try:
        from src.db.db_utils import initialize_database
        initialize_database()
        yield True
    except Exception as e:
        pytest.skip(f"Database unavailable: {e}")


@pytest.fixture
def test_user(fresh_db):
    """Create a test user in the database.
    
    Creates user 'test_user_pytest' with password 'test_password_123'.
    Cleans up after test completes.
    Skips if database is unavailable.
    """
    from src.db.db_utils import add_user, get_db_connection
    
    username = "test_user_pytest"
    password = "test_password_123"
    
    try:
        # Clean up any existing test user first
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass
    
    try:
        # Create the test user
        result = add_user(username, password)
        
        yield {
            "username": username,
            "password": password,
            "result": result,
        }
        
        # Cleanup: remove test user after test
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass
    except Exception as e:
        pytest.skip(f"Could not create test user: {e}")


# ============================================================================
#                      PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "fixtures: mark test as a fixture test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database"
    )


# ============================================================================
#                      TEST COLLECTION HOOKS
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Modify test collection - add markers based on location."""
    for item in items:
        # Auto-mark tests by directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "fixtures" in str(item.fspath):
            item.add_marker(pytest.mark.fixtures)