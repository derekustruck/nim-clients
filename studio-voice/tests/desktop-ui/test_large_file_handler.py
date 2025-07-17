#!/usr/bin/env python3
"""
Test the large file handler functionality
"""

import os
import sys

# Add desktop-ui directory to Python path
desktop_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../desktop-ui'))
sys.path.insert(0, desktop_ui_path)
from large_file_handler import LargeFileProcessor

def test_large_file_handler():
    """Test the large file processor"""
    print("🔬 Testing Large File Handler")
    print("=" * 50)
    
    processor = LargeFileProcessor()
    
    # Test with the large audio file
    large_file = os.path.join('..', 'assets', 'audio.wav')
    small_file = os.path.join('..', 'assets', 'studio_voice_48k_input.wav')
    
    for test_file in [small_file, large_file]:
        if os.path.exists(test_file):
            print(f"\n📁 Testing: {os.path.basename(test_file)}")
            
            # Get file info
            info = processor.get_file_size_info(test_file)
            print(f"   Size: {info['file_size_mb']:.1f}MB")
            print(f"   Duration: {info['duration_seconds']:.1f}s")
            print(f"   Exceeds limit: {info['exceeds_limit']}")
            
            if info['exceeds_limit']:
                chunk_duration = processor.estimate_chunk_duration(test_file)
                print(f"   Recommended chunk duration: {chunk_duration:.0f}s")
                
                # Estimate number of chunks
                num_chunks = int(info['duration_seconds'] / chunk_duration) + 1
                print(f"   Estimated chunks needed: {num_chunks}")
        else:
            print(f"❌ File not found: {test_file}")

if __name__ == "__main__":
    test_large_file_handler()
