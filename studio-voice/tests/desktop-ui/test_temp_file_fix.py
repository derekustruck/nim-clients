#!/usr/bin/env python3
"""
Test for temp file extension handling fix
"""

import os
import sys
import shutil

# Add desktop-ui directory to Python path
desktop_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../desktop-ui'))
sys.path.insert(0, desktop_ui_path)
from large_file_handler import LargeFileProcessor

def test_temp_file_naming():
    """Test the merge functionality with proper temp file extensions"""
    print("🔬 Testing Temp File Extension Fix")
    print("=" * 50)
    
    processor = LargeFileProcessor()
    
    # Use a small test file to create chunks quickly
    test_file = os.path.join('..', '..', 'assets', 'studio_voice_48k_input.wav')
    test_file = os.path.abspath(test_file)
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📁 Testing with: {os.path.basename(test_file)}")
    
    # Split the file into very small chunks (force multiple chunks)
    print("🔪 Splitting file into small chunks...")
    try:
        chunk_files = processor.split_audio_file(test_file, 3.0)  # 3-second chunks
        print(f"✅ Created {len(chunk_files)} chunks")
        
        # Test merge with problematic extension (like the error showed)
        print("\n🔗 Testing merge with problematic extension...")
        problematic_output = "test_audio.wav.temp_enhanced"  # This caused the original error
        
        success = processor.merge_audio_files(chunk_files, problematic_output)
        
        if success and os.path.exists(problematic_output):
            merged_size = os.path.getsize(problematic_output) / (1024 * 1024)
            print(f"✅ Merge with problematic extension successful!")
            print(f"   Output file: {problematic_output}")
            print(f"   Size: {merged_size:.1f}MB")
            
            # Clean up
            os.remove(problematic_output)
        else:
            print("❌ Merge failed even with format fix")
        
        # Test merge with proper .wav extension
        print("\n🔗 Testing merge with proper .wav extension...")
        proper_output = "test_audio_temp_enhanced.wav"  # Fixed naming
        
        success = processor.merge_audio_files(chunk_files, proper_output)
        
        if success and os.path.exists(proper_output):
            merged_size = os.path.getsize(proper_output) / (1024 * 1024)
            print(f"✅ Merge with proper extension successful!")
            print(f"   Output file: {proper_output}")
            print(f"   Size: {merged_size:.1f}MB")
            
            # Clean up
            os.remove(proper_output)
        else:
            print("❌ Merge failed")
        
        # Clean up chunks
        processor.cleanup_chunks(chunk_files)
        print("🧹 Cleaned up chunk files")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_temp_file_naming()
