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

from PIL import Image
import os

img_path = r"assets\image_assets\icon.png"
ico_path = r"assets\image_assets\icon.ico"

if os.path.exists(img_path):
    img = Image.open(img_path)
    # Save as ICO (containing 256x256, 128x128, 64x64, 48x48, 32x32, 16x16 sizes)
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Created {ico_path}")
else:
    print(f"Error: {img_path} not found")
