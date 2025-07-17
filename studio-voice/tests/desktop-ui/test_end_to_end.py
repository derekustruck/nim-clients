#!/usr/bin/env python3
"""
End-to-end test of large file processing workflow
Tests the complete process: detection -> chunking -> processing -> merging
"""

import os
import sys
import subprocess
import tempfile

# Add desktop-ui directory to Python path
desktop_ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../desktop-ui'))
sys.path.insert(0, desktop_ui_path)
from large_file_handler import LargeFileProcessor

def test_end_to_end_large_file():
    """Test the complete large file processing workflow"""
    print("🔬 End-to-End Large File Processing Test")
    print("=" * 60)
    
    processor = LargeFileProcessor()
    
    # Use the large test file
    large_file = os.path.join('..', 'assets', 'audio.wav')
    
    if not os.path.exists(large_file):
        print(f"❌ Large file not found: {large_file}")
        return False
    
    print(f"📁 Testing complete workflow with: {os.path.basename(large_file)}")
    
    # Step 1: Check if file needs chunking
    info = processor.get_file_size_info(large_file)
    print(f"📊 File info:")
    print(f"   Size: {info['file_size_mb']:.1f}MB")
    print(f"   Duration: {info['duration_seconds']:.1f}s")
    print(f"   Exceeds limit: {info['exceeds_limit']}")
    
    if not info['exceeds_limit']:
        print("⚠️  File doesn't exceed limit - skipping chunking test")
        return True
    
    # Step 2: Split into chunks
    print(f"\n🔪 Step 2: Splitting file...")
    chunk_duration = processor.estimate_chunk_duration(large_file)
    chunk_files = processor.split_audio_file(large_file, chunk_duration)
    print(f"✅ Created {len(chunk_files)} chunks")
    
    # Verify all chunks are under limit
    all_under_limit = True
    for i, chunk_file in enumerate(chunk_files):
        chunk_info = processor.get_file_size_info(chunk_file)
        under_limit = not chunk_info['exceeds_limit']
        print(f"   Chunk {i+1}: {chunk_info['file_size_mb']:.1f}MB - Under limit: {under_limit}")
        if not under_limit:
            all_under_limit = False
    
    if not all_under_limit:
        print("❌ Some chunks still exceed limit!")
        processor.cleanup_chunks(chunk_files)
        return False
    
    # Step 3: Simulate processing each chunk (without actual server call)
    print(f"\n🔄 Step 3: Simulating chunk processing...")
    processed_chunks = []
    
    for i, chunk_file in enumerate(chunk_files):
        # Create a "processed" version by copying the chunk
        processed_chunk = chunk_file.replace('.wav', '_processed.wav')
        
        # In real workflow, this would be the server processing
        # For test, just copy the file to simulate processing
        import shutil
        shutil.copy2(chunk_file, processed_chunk)
        
        processed_chunks.append(processed_chunk)
        print(f"   ✅ Chunk {i+1} processed")
    
    # Step 4: Merge processed chunks
    print(f"\n🔗 Step 4: Merging processed chunks...")
    
    with tempfile.NamedTemporaryFile(suffix='_temp_enhanced.wav', delete=False) as tmp_file:
        temp_output = tmp_file.name
    
    success = processor.merge_audio_files(processed_chunks, temp_output)
    
    if success and os.path.exists(temp_output):
        merged_info = processor.get_file_size_info(temp_output)
        print(f"✅ Merge successful!")
        print(f"   Merged size: {merged_info['file_size_mb']:.1f}MB")
        print(f"   Merged duration: {merged_info['duration_seconds']:.1f}s")
        print(f"   Duration difference: {abs(merged_info['duration_seconds'] - info['duration_seconds']):.1f}s")
        
        # Verify the merged file is close to original
        size_diff = abs(merged_info['file_size_mb'] - info['file_size_mb'])
        duration_diff = abs(merged_info['duration_seconds'] - info['duration_seconds'])
        
        if size_diff < 0.1 and duration_diff < 0.1:
            print(f"✅ Quality preserved (size diff: {size_diff:.2f}MB, duration diff: {duration_diff:.2f}s)")
            success = True
        else:
            print(f"⚠️  Quality differences detected (size diff: {size_diff:.2f}MB, duration diff: {duration_diff:.2f}s)")
            success = False
        
        # Clean up temp output
        os.remove(temp_output)
    else:
        print("❌ Merge failed!")
        success = False
    
    # Step 5: Cleanup
    print(f"\n🧹 Step 5: Cleaning up...")
    processor.cleanup_chunks(chunk_files)
    processor.cleanup_chunks(processed_chunks)
    print("✅ Cleanup complete")
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 END-TO-END TEST PASSED!")
        print("   Large file processing workflow is working correctly.")
    else:
        print("❌ END-TO-END TEST FAILED!")
        print("   There are issues with the large file processing workflow.")
    
    return success

if __name__ == "__main__":
    test_end_to_end_large_file()
