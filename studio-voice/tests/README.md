# Studio Voice Test Suite

This directory contains organized tests for the Studio Voice project.

## Structure

```
tests/
├── core/                    # Core functionality tests
│   └── test_desktop_ui_fix.py
├── desktop-ui/              # Desktop UI specific tests
│   ├── test_chunking.py
│   ├── test_end_to_end.py
│   ├── test_large_file_handler.py
│   ├── test_processing_fix.py
│   └── test_temp_file_fix.py
├── scripts/                 # Batch script tests
│   ├── test_loop.bat
│   ├── test_podman.bat
│   └── test_server.bat
├── test_utils.py           # Test utilities and helpers
└── README.md               # This file
```

## Running Tests

From the project root directory:

```bash
# Activate virtual environment
nim\Scripts\activate.bat

# Run all tests
python run_tests.py

# Run individual tests
cd tests\desktop-ui
python test_large_file_handler.py
```

## Test Categories

### Core Tests
- **test_desktop_ui_fix.py**: Tests basic desktop UI functionality and zero-byte file detection

### Desktop UI Tests
- **test_chunking.py**: Tests audio file chunking for large files
- **test_end_to_end.py**: Complete workflow testing from chunking to merging
- **test_large_file_handler.py**: LargeFileProcessor class functionality
- **test_processing_fix.py**: Audio processing fixes and error handling
- **test_temp_file_fix.py**: Temporary file extension handling

### Script Tests
- **test_loop.bat**: Loop testing functionality
- **test_podman.bat**: Podman container testing
- **test_server.bat**: Server connectivity testing

## Test Requirements

Tests require:
- Active Python virtual environment (`nim`)
- NVIDIA Studio Voice NIM server (for integration tests)
- Sample audio files in `assets/` directory
- Required Python packages: `soundfile`, `numpy`, etc.

## Adding New Tests

1. Create test files with `test_` prefix
2. Use `test_utils.py` for common setup and utilities
3. Place in appropriate subdirectory based on test category
4. Update this README if adding new categories

## Notes

- Some tests require an active NIM server connection
- Large file tests may take several minutes to complete
- Integration tests create temporary files that are automatically cleaned up
- Batch script tests are skipped by the Python test runner but can be run manually
