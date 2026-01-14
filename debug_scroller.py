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

from PyQt6.QtWidgets import QApplication, QScroller
import sys

app = QApplication(sys.argv)
print("Dir QScroller:")
print(dir(QScroller))

try:
    print("QScroller.ScrollerGesture:", QScroller.ScrollerGesture)
except AttributeError:
    print("QScroller.ScrollerGesture NOT FOUND")

try:
    print("QScroller.LeftMouseButtonGesture:", QScroller.LeftMouseButtonGesture)
except AttributeError:
    print("QScroller.LeftMouseButtonGesture NOT FOUND")
    
# Check for any enum-like inner classes
for item in dir(QScroller):
    if "Gesture" in item:
        print(f"Candidate: {item}")
