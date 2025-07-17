#!/usr/bin/env python3
"""
Test script to verify the desktop UI processing fix works correctly
"""

import os
import sys
import subprocess
import shutil

def test_processing_fix():
    """Test the fixed processing logic"""
    print("🔬 Testing Desktop UI Processing Fix")
    print("=" * 50)
    
    # Test file paths
    input_file = os.path.join('..', 'assets', 'studio_voice_48k_input.wav')
    test_output = "test_ui_output.wav"
    
    # Simulate the desktop UI command
    script_path = os.path.join('..', 'scripts', 'studio_voice.py')
    
    cmd = [
        sys.executable, script_path,
        '--input', input_file,
        '--output', test_output,
        '--model-type', '48k-hq'
    ]
    
    print(f"📋 Command: {' '.join(cmd)}")
    print("⏳ Running processing...")
    
    try:
        # Run the processing command (same as desktop UI)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"📤 Return code: {result.returncode}")
        print(f"📤 Stdout: {result.stdout}")
        if result.stderr:
            print(f"📤 Stderr: {result.stderr}")
        
        # Test our improved logic
        print("\n🔍 Testing fixed detection logic:")
        
        # OLD LOGIC (would have failed to detect zero-byte files)
        old_logic_pass = result.returncode == 0 and os.path.exists(test_output)
        print(f"❌ Old logic (returncode==0 AND exists): {old_logic_pass}")
        
        # NEW LOGIC (correctly detects zero-byte files)
        new_logic_pass = (result.returncode == 0 and 
                         os.path.exists(test_output) and 
                         os.path.getsize(test_output) > 0)
        print(f"✅ New logic (returncode==0 AND exists AND size>0): {new_logic_pass}")
        
        if os.path.exists(test_output):
            file_size = os.path.getsize(test_output)
            print(f"📊 Output file size: {file_size} bytes")
            
            if file_size > 0:
                print("🎉 SUCCESS: Processing completed with valid output!")
            else:
                print("⚠️  DETECTED: Zero-byte file (old UI would have claimed success)")
        else:
            print("❌ FAILURE: No output file created")
            
    except subprocess.TimeoutExpired:
        print("⏰ ERROR: Processing timed out")
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(test_output):
            os.remove(test_output)
            print("🧹 Cleaned up test file")

if __name__ == "__main__":
    test_processing_fix()
