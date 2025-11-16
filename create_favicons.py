#!/usr/bin/env python3
"""
create_favicons.py

Generates a multi-resolution favicon.ico and a 32x32 PNG from `images/logo.png`, cropping to match the reference emblem.

Usage: py -3 create_favicons.py
"""
from PIL import Image
import os
import sys

ROOT = os.path.dirname(__file__)
SRC = os.path.join(ROOT, 'images', 'logo.png')
OUT_ICO = os.path.join(ROOT, 'favicon.ico')
OUT_32 = os.path.join(ROOT, 'favicon-32.png')

if not os.path.isfile(SRC):
    print(f"Source logo not found at {SRC}")
    sys.exit(2)

print('Opening source:', SRC)
img = Image.open(SRC).convert('RGBA')

# Crop parameters based on reference image proportions
# Reference image: 211x254, logo area is centered and triangle-shaped
# We'll crop a centered square, but bias slightly lower to match the triangle
w, h = img.size
crop_w = int(w * 0.55)
crop_h = int(h * 0.55)
center_x = w // 2
center_y = int(h * 0.56)  # bias lower for triangle
left = max(0, center_x - crop_w // 2)
upper = max(0, center_y - crop_h // 2)
right = min(w, left + crop_w)
lower = min(h, upper + crop_h)
crop = img.crop((left, upper, right, lower))

# Resize to 64x64 for base
base_size = (64, 64)
c64 = crop.copy()
c64.thumbnail(base_size, Image.LANCZOS)

# Save 32x32 PNG
icon32_32 = c64.resize((32,32), Image.LANCZOS)
icon32_32.save(OUT_32, format='PNG')
print('Wrote', OUT_32)

# Create multi-size .ico
sizes = [(16,16),(32,32),(48,48),(64,64)]
try:
    c64.save(OUT_ICO, format='ICO', sizes=sizes)
    print('Wrote', OUT_ICO)
except Exception as e:
    print('Failed to write ICO:', e)
    sys.exit(3)

print('Done.')