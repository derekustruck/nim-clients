#!/usr/bin/env python3
"""
Studio Voice Large File Handler
Utility for processing audio files that exceed the NIM server size limit
"""

import os
import tempfile
import subprocess
import soundfile as sf
import numpy as np
from typing import List, Tuple, Optional

# Default server file size limit (can be overridden)
DEFAULT_FILE_SIZE_LIMIT = 36700160  # ~35MB

class LargeFileProcessor:
    """Handles processing of audio files larger than server limits"""
    
    def __init__(self, file_size_limit: int = DEFAULT_FILE_SIZE_LIMIT):
        self.file_size_limit = file_size_limit
        
    def needs_chunking(self, file_path: str) -> bool:
        """Check if file exceeds size limit and needs chunking"""
        return os.path.getsize(file_path) > self.file_size_limit
    
    def estimate_chunk_duration(self, file_path: str, target_size: Optional[int] = None) -> float:
        """Estimate duration per chunk to stay under size limit"""
        if target_size is None:
            target_size = int(self.file_size_limit * 0.8)  # 80% of limit for safety
            
        file_size = os.path.getsize(file_path)
        
        # Get audio info
        info = sf.info(file_path)
        duration = info.duration
        
        # Calculate target duration to achieve target size
        bytes_per_second = file_size / duration
        target_duration = target_size / bytes_per_second
        
        # Round down to nearest 10 seconds for clean chunks
        return max(10.0, int(target_duration / 10) * 10)
    
    def split_audio_file(self, input_file: str, chunk_duration: float) -> List[str]:
        """Split audio file into chunks of specified duration"""
        temp_dir = tempfile.mkdtemp(prefix="studio_voice_chunks_")
        chunk_files = []
        
        # Get audio info
        info = sf.info(input_file)
        total_duration = info.duration
        
        chunk_index = 0
        start_time = 0.0
        
        while start_time < total_duration:
            end_time = min(start_time + chunk_duration, total_duration)
            
            # Create chunk filename
            chunk_file = os.path.join(temp_dir, f"chunk_{chunk_index:04d}.wav")
            
            # Extract chunk using soundfile
            data, sample_rate = sf.read(input_file, 
                                      start=int(start_time * info.samplerate),
                                      stop=int(end_time * info.samplerate))
            
            sf.write(chunk_file, data, sample_rate)
            chunk_files.append(chunk_file)
            
            start_time = end_time
            chunk_index += 1
        
        return chunk_files
    
    def merge_audio_files(self, chunk_files: List[str], output_file: str) -> bool:
        """Merge processed audio chunks back into single file"""
        try:
            if not chunk_files:
                return False
            
            # Read first chunk to get format info
            first_data, sample_rate = sf.read(chunk_files[0])
            
            # Collect all audio data
            all_data = [first_data]
            
            for chunk_file in chunk_files[1:]:
                data, _ = sf.read(chunk_file)
                all_data.append(data)
            
            # Concatenate all chunks
            merged_data = np.concatenate(all_data, axis=0)
            
            # Write merged file with explicit format
            sf.write(output_file, merged_data, sample_rate, format='WAV')
            
            return True
            
        except Exception as e:
            print(f"Error merging audio files: {e}")
            return False
    
    def cleanup_chunks(self, chunk_files: List[str]):
        """Clean up temporary chunk files"""
        for chunk_file in chunk_files:
            try:
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
            except:
                pass
        
        # Try to remove temp directory
        if chunk_files:
            temp_dir = os.path.dirname(chunk_files[0])
            try:
                os.rmdir(temp_dir)
            except:
                pass
    
    def get_file_size_info(self, file_path: str) -> dict:
        """Get comprehensive file size information"""
        file_size = os.path.getsize(file_path)
        info = sf.info(file_path)
        
        return {
            'file_size_bytes': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'limit_bytes': self.file_size_limit,
            'limit_mb': self.file_size_limit / (1024 * 1024),
            'exceeds_limit': file_size > self.file_size_limit,
            'duration_seconds': info.duration,
            'sample_rate': info.samplerate,
            'channels': info.channels
        }
