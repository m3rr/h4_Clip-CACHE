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
