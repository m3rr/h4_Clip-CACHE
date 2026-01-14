# ------------------------------------------------------------------------------
# COPYRIGHT (C) 2026 h4. ALL RIGHTS RESERVED.
#
# This software is provided under a SOURCE-AVAILABLE COMMERCIAL LICENSE.
# You may view and use this code for personal, non-commercial purposes only.
#
# ANY COMMERCIAL USE, REDISTRIBUTION, OR DERIVATIVE WORK FOR FINANCIAL GAIN
# REQUIRES A 50% ROYALTY PAYMENT TO THE AUTHOR (h4) FROM THE FIRST DOLLAR EARNED.
#
# See LICENSE.md for full legal terms and royalty obligations.
# ------------------------------------------------------------------------------

import sys
import subprocess
import os
import importlib.util

def install_dependencies():
    """
    Checks for requirements.txt and installs/updates dependencies.
    """
    # Helper to install specific packages if missing from requirements or hard failure
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    if not os.path.exists(req_file):
        print(f"[ERROR] requirements.txt not found at {req_file}")
        return

    print("[BOOTSTRAP] Checking and Updating Dependencies (Nuclear Protocol)...")
    try:
        # We use sys.executable to ensure we install into the CURRENT python environment
        # Added --user to avoid permission issues
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file, "--upgrade", "--user"])
        print("[BOOTSTRAP] Dependencies verified.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        # We try to continue? standard protocol says ensure deps. 
        # But if it fails due to network or something, user might still want to run.
        # However rule says "bootstrapping everytime", so check call implies we stop if fail.
        sys.exit(1)

def main():
    print("[BOOTSTRAP] Initializing Clip-CACHE...")
    install_dependencies()
    
    # Dynamic import of main
    try:
        # Append current dir to path to find 'src'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        import src.main
        print("[BOOTSTRAP] Launching Main Application...")
        
        # Parse arguments
        start_bg = "--background" in sys.argv
        
        # Pass args or handle config override in src.main
        # We'll update src.main.main to accept kwargs
        src.main.main(start_in_background=start_bg)
    except ImportError as e:
        print(f"[ERROR] Import Failure: {e}")
        print("Ensure 'src/main.py' exists and dependencies (PyQt6) are healthy.")
    except Exception as e:
        print(f"[CRITICAL] Application Crash: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
