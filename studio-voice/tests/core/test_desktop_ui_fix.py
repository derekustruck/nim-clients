#!/usr/bin/env python3
"""
Test script to verify the desktop UI zero-byte file fix
This simulates the desktop UI processing logic to test the improvements
"""

import os
import sys
import subprocess
import shutil
import tempfile

def test_processing_logic():
    """Test the improved processing logic"""
    print("Testing Desktop UI Zero-Byte File Fix")
    print("=" * 50)
    
    # Paths
    input_file = os.path.join(os.path.dirname(__file__), 'assets', 'studio_voice_48k_input.wav')
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'studio_voice.py')
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
        
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    print(f"✅ Input file found: {input_file}")
    print(f"✅ Script found: {script_path}")
    print(f"Input file size: {os.path.getsize(input_file)} bytes")
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_output = temp_file.name
    
    print(f"Temp output: {temp_output}")
    
    # Build command (same as desktop UI)
    cmd = [
        sys.executable, script_path,
        '--input', input_file,
        '--output', temp_output,
        '--model-type', '48k-hq'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("Running subprocess with 30-second timeout...")
    
    try:
        # Run with shorter timeout for testing
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        
        # Test the NEW improved logic
        if result.returncode == 0 and os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
            print(f"✅ NEW LOGIC: Processing successful!")
            print(f"   Output file size: {os.path.getsize(temp_output)} bytes")
            success = True
        else:
            print("❌ NEW LOGIC: Processing failed - detailed analysis:")
            
            if result.returncode != 0:
                print(f"   - Return code was non-zero: {result.returncode}")
                
            if not os.path.exists(temp_output):
                print(f"   - Output file was not created")
                
            elif os.path.getsize(temp_output) == 0:
                print(f"   - Output file exists but is empty (0 bytes)")
                print(f"   - This indicates a server connection issue")
                
            if result.stderr:
                print(f"   - Error output: {result.stderr}")
            if result.stdout:
                print(f"   - Standard output: {result.stdout}")
                
            success = False
        
        # Test the OLD logic for comparison
        if result.returncode == 0 and os.path.exists(temp_output):
            print(f"⚠️  OLD LOGIC: Would have reported success (but file might be empty)")
        else:
            print(f"❌ OLD LOGIC: Would have reported failure")
    
    except subprocess.TimeoutExpired:
        print("❌ Processing timed out (30 seconds)")
        print("   This suggests server connectivity issues")
        success = False
    
    except Exception as e:
        print(f"❌ Error running subprocess: {e}")
        success = False
    
    finally:
        # Clean up
        if os.path.exists(temp_output):
            os.remove(temp_output)
            print(f"Cleaned up temp file: {temp_output}")
    
    return success

if __name__ == "__main__":
    test_processing_logic()
