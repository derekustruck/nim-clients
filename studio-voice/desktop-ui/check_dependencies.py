#!/usr/bin/env python3
"""
Desktop UI Dependency Checker
Simple script to test if all required dependencies are available
"""

import sys
import importlib
import subprocess
import os

def check_dependency(module_name, description=""):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - OK {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - MISSING {description}")
        print(f"   Error: {e}")
        return False

def install_requirements():
    """Try to install requirements.txt from the parent directory"""
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(parent_dir, 'requirements.txt')
    
    if os.path.exists(requirements_file):
        try:
            print(f"\nInstalling requirements from: {requirements_file}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return False
    else:
        print(f"Requirements file not found at: {requirements_file}")
        return False

def main():
    print("Studio Voice Desktop UI - Dependency Check")
    print("=" * 50)
    print()
    
    # Core Python modules (should always be available)
    core_modules = [
        ('tkinter', '(GUI framework)'),
        ('threading', '(background processing)'),
        ('queue', '(thread communication)'),
        ('subprocess', '(running external commands)'),
        ('os', '(file operations)'),
        ('shutil', '(file copying)'),
        ('pathlib', '(path handling)'),
    ]
    
    # Optional modules for full functionality
    optional_modules = [
        ('grpc', '(for Studio Voice communication)'),
        ('google.protobuf', '(for protocol buffers)'),
    ]
    
    print("Checking core dependencies:")
    core_ok = all(check_dependency(module, desc) for module, desc in core_modules)
    
    print("\nChecking optional dependencies:")
    optional_ok = all(check_dependency(module, desc) for module, desc in optional_modules)
    
    print("\n" + "=" * 50)
    
    if core_ok and optional_ok:
        print("✅ All dependencies are available!")
        print("The desktop UI should work properly.")
    elif core_ok:
        print("⚠️  Core dependencies OK, but some optional features may not work.")
        print("You can use the desktop UI, but Studio Voice integration might be limited.")
        
        install_choice = input("\nWould you like to try installing missing dependencies? (y/n): ")
        if install_choice.lower() in ['y', 'yes']:
            if install_requirements():
                print("\nRe-checking dependencies after installation:")
                all(check_dependency(module, desc) for module, desc in optional_modules)
    else:
        print("❌ Critical dependencies are missing!")
        print("The desktop UI will not work properly.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
