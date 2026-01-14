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
