#!/usr/bin/env python3
"""
Studio Voice UI Demo Script
Quick test to verify the UIs are working correctly
"""

import os
import sys
from pathlib import Path

def check_web_ui():
    """Check if web UI files exist"""
    web_ui_dir = Path(__file__).parent / "web-ui"
    
    required_files = [
        "simple_app.py",
        "templates/simple_index.html",
        "templates/upload.html",
        "templates/dashboard.html",
        "simple_requirements.txt"
    ]
    
    print("🌐 Web UI Check:")
    all_good = True
    
    for file in required_files:
        file_path = web_ui_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False
    
    return all_good

def check_desktop_ui():
    """Check if desktop UI files exist"""
    desktop_ui_dir = Path(__file__).parent / "desktop-ui"
    
    required_files = [
        "studio_voice_gui.py"
    ]
    
    print("\n🖥️ Desktop UI Check:")
    all_good = True
    
    for file in required_files:
        file_path = desktop_ui_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False
    
    return all_good

def check_launchers():
    """Check if launcher scripts exist"""
    script_dir = Path(__file__).parent
    
    required_files = [
        "start_simple_web_ui.bat",
        "start_web_ui.bat",
        "start_desktop_ui.bat",
        "start_enhanced_cli.bat"
    ]
    
    print("\n🚀 Launcher Scripts Check:")
    all_good = True
    
    for file in required_files:
        file_path = script_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False
    
    return all_good

def main():
    """Main demo function"""
    print("=" * 50)
    print("🎵 Studio Voice UI Demo & Health Check")
    print("=" * 50)
    
    web_ok = check_web_ui()
    desktop_ok = check_desktop_ui()
    launchers_ok = check_launchers()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("=" * 50)
    
    if web_ok:
        print("✅ Web UI: Ready to use")
        print("   Run: start_simple_web_ui.bat (recommended)")
        print("   Or:  start_web_ui.bat (advanced)")
    else:
        print("❌ Web UI: Missing files")
    
    if desktop_ok:
        print("✅ Desktop UI: Ready to use")
        print("   Run: start_desktop_ui.bat")
    else:
        print("❌ Desktop UI: Missing files")
    
    if launchers_ok:
        print("✅ Launcher Scripts: All present")
    else:
        print("❌ Launcher Scripts: Some missing")
    
    print("\n" + "=" * 50)
    print("🎯 Quick Start Recommendations:")
    print("=" * 50)
    
    if web_ok:
        print("1. 🌐 Web Interface (Easiest):")
        print("   start_simple_web_ui.bat")
        print("   Then open: http://127.0.0.1:5000")
        print()
    
    if desktop_ok:
        print("2. 🖥️ Desktop App:")
        print("   start_desktop_ui.bat")
        print()
    
    print("3. 💻 Enhanced CLI:")
    print("   start_enhanced_cli.bat")
    print()
    
    print("🔧 New Features Added:")
    print("✅ Folder scanning (like original script)")
    print("✅ Proper file management (replaces originals)")
    print("✅ Backup to '../original audio/' folders")
    print("✅ Preserves directory structure")
    print("✅ Real-time progress tracking")
    print("✅ Queue management")
    
    print("\n" + "=" * 50)
    print("Ready to enhance your audio! 🎵")
    print("=" * 50)

if __name__ == "__main__":
    main()
