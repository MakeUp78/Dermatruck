#!/usr/bin/env python3
"""
Installation verification script for the Dermograph Tracker application.
Run this script to verify that all components are installed correctly.
"""
import sys
import os

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python {version.major}.{version.minor} is too old. Python 3.8+ required.")
        return False
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def check_dependencies():
    """Check that all required packages are available."""
    required_packages = ['numpy', 'matplotlib', 'tkinter']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is missing")
            missing.append(package)
    
    if missing:
        print(f"\nTo install missing packages, run:")
        if 'tkinter' in missing:
            print("  sudo apt-get install python3-tk  # On Ubuntu/Debian")
            print("  # On other systems, tkinter usually comes with Python")
        if any(pkg != 'tkinter' for pkg in missing):
            print("  pip install -r requirements.txt")
        return False
    
    return True

def check_application_files():
    """Check that all application files are present."""
    required_files = [
        'main.py', 'gui.py', 'imu_simulator.py', 'movement_tracker.py',
        'visualizer.py', 'utils.py', 'requirements.txt', 'README.md'
    ]
    
    missing = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} found")
        else:
            print(f"✗ {filename} missing")
            missing.append(filename)
    
    return len(missing) == 0

def test_core_functionality():
    """Test basic functionality without GUI."""
    try:
        # Set matplotlib to non-interactive mode
        import matplotlib
        matplotlib.use('Agg')
        
        from imu_simulator import IMUSimulator
        from movement_tracker import MovementTracker
        
        # Quick functionality test
        sim = IMUSimulator(sample_rate=10.0)
        tracker = MovementTracker()
        
        sim.set_mode('demo', speed=1.0)
        
        for _ in range(5):
            imu_data = sim.generate_sample()
            tracker.process_imu_sample(imu_data)
        
        state = tracker.get_current_state()
        if len(tracker.get_trajectory()) > 0:
            print("✓ Core functionality test passed")
            return True
        else:
            print("✗ Core functionality test failed - no trajectory data")
            return False
            
    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Dermograph Tracker - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Application Files", check_application_files),
        ("Core Functionality", test_core_functionality)
    ]
    
    passed = 0
    failed = 0
    
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if check_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Verification Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 Installation verification successful!")
        print("   You can now run the application with: python main.py")
        print("   Note: A display is required for the GUI interface.")
        return True
    else:
        print("\n❌ Installation verification failed.")
        print("   Please address the issues above before running the application.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)