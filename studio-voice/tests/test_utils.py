"""
Test utilities and configuration for Studio Voice tests.
"""

import os
import sys
from pathlib import Path

def setup_test_environment():
    """
    Set up the test environment with proper Python paths.
    Call this at the beginning of test files to ensure imports work correctly.
    """
    # Get the project root directory (parent of tests directory)
    test_file_dir = Path(__file__).parent
    project_root = test_file_dir.parent
    
    # Add required paths
    paths_to_add = [
        str(project_root),                    # Project root
        str(project_root / "desktop-ui"),     # Desktop UI modules
        str(project_root / "scripts"),        # Core scripts
        str(project_root / "interfaces"),     # gRPC interfaces
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return project_root

def get_test_assets_dir():
    """Get the path to test assets directory."""
    project_root = setup_test_environment()
    return project_root / "assets"

def get_temp_dir():
    """Get a temporary directory for test files."""
    import tempfile
    return Path(tempfile.mkdtemp(prefix="studio_voice_test_"))

def cleanup_temp_files(*paths):
    """Clean up temporary test files and directories."""
    import shutil
    for path in paths:
        if isinstance(path, (str, Path)):
            path = Path(path)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
