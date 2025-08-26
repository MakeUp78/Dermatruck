#!/usr/bin/env python3
"""
Main entry point for the Dermograph Tracking Application.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui import DermographGUI
    print("Starting Dermograph Movement Tracker...")
    
    # Create and run the application
    app = DermographGUI()
    app.run()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except KeyboardInterrupt:
    print("\nApplication interrupted by user")
    sys.exit(0)
    
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)