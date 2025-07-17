#!/usr/bin/env python3
"""
Test runner for Studio Voice project.
Runs all test suites from the appropriate directories.
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file."""
    print(f"\n{'='*50}")
    print(f"Running: {test_file}")
    print(f"{'='*50}")
    
    # Change to the directory containing the test file
    test_dir = os.path.dirname(test_file)
    original_dir = os.getcwd()
    
    try:
        if test_dir:
            os.chdir(test_dir)
        
        # Run the test file
        result = subprocess.run([sys.executable, os.path.basename(test_file)], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✅ PASSED: {os.path.basename(test_file)}")
            return True
        else:
            print(f"❌ FAILED: {os.path.basename(test_file)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR running {test_file}: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main test runner."""
    print("Studio Voice Test Runner")
    print("=" * 30)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    # Find all test files
    test_files = []
    for test_pattern in ["tests/**/*.py", "tests/**/*.bat"]:
        test_files.extend(glob.glob(str(project_root / test_pattern), recursive=True))
    
    # Filter only actual test files (starting with test_)
    test_files = [f for f in test_files if os.path.basename(f).startswith('test_')]
    test_files.sort()
    
    if not test_files:
        print("❌ No test files found!")
        return 1
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        rel_path = os.path.relpath(test_file, project_root)
        print(f"  - {rel_path}")
    
    print("\nStarting test execution...")
    
    # Run tests
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if test_file.endswith('.py'):
            if run_test_file(test_file):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⏭️  Skipping batch file: {os.path.basename(test_file)}")
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed > 0:
        print(f"\n❌ {failed} test(s) failed!")
        return 1
    else:
        print(f"\n🎉 All {passed} tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
