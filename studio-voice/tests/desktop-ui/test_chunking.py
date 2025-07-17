#!/usr/bin/env python3
"""
Test script for chunking and processing large files
"""

import os
import sys

# Add desktop-ui directory to Python path
desktop_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../desktop-ui'))
sys.path.insert(0, desktop_ui_path)
from large_file_handler import LargeFileProcessor

def test_chunking():
    """Test the actual chunking process"""
    print("🔬 Testing Audio Chunking")
    print("=" * 50)
    
    processor = LargeFileProcessor()
    
    # Use the large audio file
    large_file = os.path.join('..', 'assets', 'audio.wav')
    
    if not os.path.exists(large_file):
        print(f"❌ Large file not found: {large_file}")
        return
    
    print(f"📁 Testing chunking with: {os.path.basename(large_file)}")
    
    # Get file info
    info = processor.get_file_size_info(large_file)
    print(f"   Original size: {info['file_size_mb']:.1f}MB")
    print(f"   Duration: {info['duration_seconds']:.1f}s")
    
    # Estimate chunk duration
    chunk_duration = processor.estimate_chunk_duration(large_file)
    print(f"   Chunk duration: {chunk_duration:.0f}s")
    
    # Split the file
    print("🔪 Splitting file...")
    try:
        chunk_files = processor.split_audio_file(large_file, chunk_duration)
        print(f"✅ Created {len(chunk_files)} chunks:")
        
        total_chunk_size = 0
        for i, chunk_file in enumerate(chunk_files):
            chunk_size = os.path.getsize(chunk_file) / (1024 * 1024)  # MB
            total_chunk_size += chunk_size
            chunk_info = processor.get_file_size_info(chunk_file)
            print(f"   Chunk {i+1}: {chunk_size:.1f}MB ({chunk_info['duration_seconds']:.1f}s) - Under limit: {not chunk_info['exceeds_limit']}")
        
        print(f"\n📊 Total chunk size: {total_chunk_size:.1f}MB")
        print(f"   Original size: {info['file_size_mb']:.1f}MB")
        print(f"   Size difference: {abs(total_chunk_size - info['file_size_mb']):.1f}MB")
        
        # Test merge
        print("\n🔗 Testing merge...")
        merged_file = "test_merged_output.wav"
        
        success = processor.merge_audio_files(chunk_files, merged_file)
        
        if success and os.path.exists(merged_file):
            merged_size = os.path.getsize(merged_file) / (1024 * 1024)
            merged_info = processor.get_file_size_info(merged_file)
            print(f"✅ Merge successful!")
            print(f"   Merged size: {merged_size:.1f}MB ({merged_info['duration_seconds']:.1f}s)")
            print(f"   Duration difference: {abs(merged_info['duration_seconds'] - info['duration_seconds']):.1f}s")
            
            # Clean up merged file
            os.remove(merged_file)
        else:
            print("❌ Merge failed")
        
        # Clean up chunks
        processor.cleanup_chunks(chunk_files)
        print("🧹 Cleaned up chunk files")
        
    except Exception as e:
        print(f"❌ Error during chunking test: {e}")

if __name__ == "__main__":
    test_chunking()
