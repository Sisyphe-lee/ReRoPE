#!/usr/bin/env python3
"""
Create a combined video for Toy Case Experiment:
- Left: motivation-1.png (spectral analysis)
- Right: 3x3 grid of videos with row/column labels
All videos are resized to uniform dimensions before combining.
Uses PIL for text labels (supports rotation).
"""

import os
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/data1/lcy/projects/Space-Time-Pilot"
TOY_EXP_DIR = os.path.join(BASE_DIR, "assets/toy_exp")
INSIGHT_DIR = os.path.join(BASE_DIR, "assets/high_level_insight")
TMP_DIR = os.path.join(BASE_DIR, "tmp")
OUTPUT_PATH = os.path.join(INSIGHT_DIR, "toycase_combined.mp4")

os.makedirs(TMP_DIR, exist_ok=True)

# Video grid layout (3 rows x 3 cols)
videos = [
    ["wan2.1_h.mp4", "wan2.1_w.mp4", "wan2.1_wo.mp4"],
    ["cogvideox_h.mp4", "cogvideox_w.mp4", "cogvideox_wo.mp4"],
    ["wan2.2_h.mp4", "wan2.2_w.mp4", "wan2.2_wo.mp4"],
]

# Row labels (will be rotated 90 degrees, vertical)
row_labels = ["Wan2.1 T2V", "CogVideoX1.5", "Wan2.2 TI2V"]
# Column labels (horizontal)
col_labels = ["high freq Identity", "low freq Identity", "w/o Identity"]

LEFT_IMG = os.path.join(INSIGHT_DIR, "motivation-1.png")

# Target size for each cell video
CELL_WIDTH = 320
CELL_HEIGHT = 180

# Label dimensions
COL_LABEL_HEIGHT = 20  # Height for horizontal column labels
ROW_LABEL_WIDTH = 20   # Width for vertical row labels

# Gap between text and video edge
TEXT_GAP = 2

def get_video_info(path):
    """Get video duration and dimensions using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    info = json.loads(result.stdout)
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            return {
                "width": stream.get("width"),
                "height": stream.get("height"),
                "duration": float(info.get("format", {}).get("duration", 5))
            }
    return None

def create_label_image(grid_width, grid_height):
    """Create a PNG with labels. Video areas are transparent."""
    # Try to load Times New Roman, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf", 14)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", 14)
        except:
            font = ImageFont.load_default()

    # Create transparent image
    img = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw white background only for label areas (top row and left column)
    # Top label area
    draw.rectangle([0, 0, grid_width, COL_LABEL_HEIGHT], fill=(255, 255, 255, 255))
    # Left label area
    draw.rectangle([0, 0, ROW_LABEL_WIDTH, grid_height], fill=(255, 255, 255, 255))

    # Draw column labels (horizontal, at top)
    for i, label in enumerate(col_labels):
        x = ROW_LABEL_WIDTH + CELL_WIDTH * i + CELL_WIDTH // 2
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        y = COL_LABEL_HEIGHT - TEXT_GAP - text_h
        draw.text((x - text_w // 2, y), label, fill='black', font=font)

    # Draw row labels (rotated 90 degrees)
    for i, label in enumerate(row_labels):
        # Create a temporary image for rotated text
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Create small image for text, then rotate
        txt_img = Image.new('RGBA', (text_w + 4, text_h + 4), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((2, 2), label, fill='black', font=font)

        # Rotate 90 degrees counter-clockwise
        rotated = txt_img.rotate(90, expand=True)

        # Calculate position (centered vertically in the row, right-aligned to video edge)
        video_top = COL_LABEL_HEIGHT + CELL_HEIGHT * i
        video_center_y = video_top + CELL_HEIGHT // 2
        paste_x = ROW_LABEL_WIDTH - TEXT_GAP - rotated.width
        paste_y = video_center_y - rotated.height // 2

        img.paste(rotated, (paste_x, paste_y), rotated)

    label_path = os.path.join(TMP_DIR, "labels.png")
    img.save(label_path)
    return label_path

def main():
    print("=" * 60)
    print("Creating Toy Case Experiment combined video")
    print("=" * 60)

    # Step 1: Get minimum duration across all videos
    print("\n[Step 1] Analyzing video durations...")
    min_duration = float('inf')
    for row in videos:
        for v in row:
            path = os.path.join(TOY_EXP_DIR, v)
            info = get_video_info(path)
            if info:
                min_duration = min(min_duration, info["duration"])
                print(f"  {v}: {info['width']}x{info['height']}, {info['duration']:.2f}s")

    print(f"  Using duration: {min_duration:.2f}s")

    # Grid dimensions
    grid_width = ROW_LABEL_WIDTH + CELL_WIDTH * 3
    grid_height = COL_LABEL_HEIGHT + CELL_HEIGHT * 3

    # Step 2: Create label image with PIL
    print("\n[Step 2] Creating label image...")
    label_img_path = create_label_image(grid_width, grid_height)
    print(f"  Labels saved to: {label_img_path}")

    # Step 3: Build ffmpeg filter
    print("\n[Step 3] Building ffmpeg filter...")

    # Input files: 9 videos + left image + label image
    inputs = []
    for row in videos:
        for v in row:
            inputs.extend(["-i", os.path.join(TOY_EXP_DIR, v)])
    inputs.extend(["-i", LEFT_IMG])       # Input 9: left image
    inputs.extend(["-i", label_img_path]) # Input 10: labels

    # Build filter_complex
    filters = []

    # Scale all 9 videos to uniform size using center crop
    for i in range(9):
        filters.append(f"[{i}:v]scale={CELL_WIDTH}:{CELL_HEIGHT}:force_original_aspect_ratio=increase,crop={CELL_WIDTH}:{CELL_HEIGHT},setsar=1[v{i}]")

    # Create white background for the grid
    filters.append(f"color=c=white:s={grid_width}x{grid_height}:d={min_duration}[bg]")

    # Overlay videos onto grid
    filters.append(f"[bg][v0]overlay={ROW_LABEL_WIDTH}:{COL_LABEL_HEIGHT}[t0]")
    filters.append(f"[t0][v1]overlay={ROW_LABEL_WIDTH + CELL_WIDTH}:{COL_LABEL_HEIGHT}[t1]")
    filters.append(f"[t1][v2]overlay={ROW_LABEL_WIDTH + CELL_WIDTH*2}:{COL_LABEL_HEIGHT}[t2]")
    filters.append(f"[t2][v3]overlay={ROW_LABEL_WIDTH}:{COL_LABEL_HEIGHT + CELL_HEIGHT}[t3]")
    filters.append(f"[t3][v4]overlay={ROW_LABEL_WIDTH + CELL_WIDTH}:{COL_LABEL_HEIGHT + CELL_HEIGHT}[t4]")
    filters.append(f"[t4][v5]overlay={ROW_LABEL_WIDTH + CELL_WIDTH*2}:{COL_LABEL_HEIGHT + CELL_HEIGHT}[t5]")
    filters.append(f"[t5][v6]overlay={ROW_LABEL_WIDTH}:{COL_LABEL_HEIGHT + CELL_HEIGHT*2}[t6]")
    filters.append(f"[t6][v7]overlay={ROW_LABEL_WIDTH + CELL_WIDTH}:{COL_LABEL_HEIGHT + CELL_HEIGHT*2}[t7]")
    filters.append(f"[t7][v8]overlay={ROW_LABEL_WIDTH + CELL_WIDTH*2}:{COL_LABEL_HEIGHT + CELL_HEIGHT*2}[grid]")

    # Overlay labels
    filters.append(f"[grid][10:v]overlay=0:0[labeled]")

    # Scale left image to match grid height, ensure even width
    filters.append(f"[9:v]scale=-2:{grid_height}[leftimg]")

    # Combine left image and grid horizontally, then ensure even dimensions
    filters.append(f"[leftimg][labeled]hstack=inputs=2,pad=ceil(iw/2)*2:ceil(ih/2)*2[final]")

    filter_complex = ";".join(filters)

    # Step 4: Run ffmpeg
    print("\n[Step 4] Running ffmpeg...")
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-t", str(min_duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        OUTPUT_PATH
    ]

    print(f"  Output: {OUTPUT_PATH}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"\nERROR: {result.stderr}")
        return False

    print("\n" + "=" * 60)
    print("Done! Video created at:")
    print(OUTPUT_PATH)
    print("=" * 60)
    return True

if __name__ == "__main__":
    main()
