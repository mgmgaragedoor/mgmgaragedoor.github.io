#!/usr/bin/env python3
"""
create_favicons.py

Generates a multi-resolution favicon.ico and a 32x32 PNG from `images/logo.png`.

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

# Create 32x32 PNG
icon32 = img.copy()
icon32.thumbnail((32, 32), Image.LANCZOS)
icon32.save(OUT_32, format='PNG')
print('Wrote', OUT_32)

# Create multi-size .ico (sizes will be embedded)
sizes = [(16,16),(32,32),(48,48),(64,64)]
try:
    img.save(OUT_ICO, format='ICO', sizes=sizes)
    print('Wrote', OUT_ICO)
except Exception as e:
    from PIL import Image
    import os
    import sys
    import base64
    from io import BytesIO

    ROOT = os.path.dirname(__file__)
    SRC = os.path.join(ROOT, 'images', 'logo.png')
    OUT_ICO = os.path.join(ROOT, 'favicon.ico')
    OUT_32 = os.path.join(ROOT, 'favicon-32.png')
    OUT_SVG = os.path.join(ROOT, 'favicon.svg')

    if not os.path.isfile(SRC):
        print(f"Source logo not found at {SRC}")
        sys.exit(2)

    print('Opening source:', SRC)
    img = Image.open(SRC).convert('RGBA')

    def detect_crop(im):
        """Detect non-transparent bounding box; fallback to centered square crop.

        Returns a cropped square Image focused on emblem.
        """
        # Try to use alpha channel bbox if available
        try:
            alpha = im.split()[-1]
            bbox = alpha.getbbox()
        except Exception:
            bbox = None

        w, h = im.size

        if bbox:
            bx0, by0, bx1, by1 = bbox
            bw = bx1 - bx0
            bh = by1 - by0
            # add margin
            pad = int(max(bw, bh) * 0.2)
            cx = bx0 + bw // 2
            cy = by0 + bh // 2
            size = max(bw, bh) + pad
        else:
            # no alpha bbox: center square 70% of shortest side
            size = int(min(w, h) * 0.7)
            cx = w // 2
            cy = h // 2

        # ensure size not larger than image
        size = min(size, w, h)
        half = size // 2
        left = max(0, cx - half)
        upper = max(0, cy - half)
        right = min(w, left + size)
        lower = min(h, upper + size)

        # adjust if we hit border and crop is smaller than desired
        if (right - left) < size:
            left = max(0, right - size)
        if (lower - upper) < size:
            upper = max(0, lower - size)

        cropped = im.crop((left, upper, right, lower))
        return cropped

    crop = detect_crop(img)

    # Resize crop to working size (64x64 base)
    base_size = (64, 64)
    c64 = crop.copy()
    c64.thumbnail(base_size, Image.LANCZOS)

    # Save 32x32 PNG
    icon32 = c64.copy()
    icon32_32 = icon32.resize((32,32), Image.LANCZOS)
    icon32_32.save(OUT_32, format='PNG')
    print('Wrote', OUT_32)

    # Create multi-size .ico
    sizes = [(16,16),(32,32),(48,48),(64,64)]
    try:
        # Save ICO from the 64x64 source; Pillow will include the sizes
        c64.save(OUT_ICO, format='ICO', sizes=sizes)
        print('Wrote', OUT_ICO)
    except Exception as e:
        print('Failed to write ICO:', e)
        sys.exit(3)

    # Generate an SVG embedding a base64 PNG of 64x64 for better cross-browser rendering
    buffer = BytesIO()
    c64.save(buffer, format='PNG')
    b64 = base64.b64encode(buffer.getvalue()).decode('ascii')
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="favicon">
      <image href="data:image/png;base64,{b64}" width="64" height="64" />
    </svg>
    '''
    with open(OUT_SVG, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print('Wrote', OUT_SVG)

    print('Done.')
