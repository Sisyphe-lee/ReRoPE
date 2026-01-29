#!/usr/bin/env python3
"""
Burn pose overlay images onto synthesized videos using ffmpeg.
The pose image will be placed at the bottom-right corner, sized to 20% of video width.
"""

import os
import subprocess
import shutil

# Base paths
BASE_DIR = "/data1/lcy/projects/Space-Time-Pilot"
POSE_DIR = os.path.join(BASE_DIR, "assets/pose_vis_processed")
V2V_DIR = os.path.join(BASE_DIR, "assets/demos/v2v")
I2V_DIR = os.path.join(BASE_DIR, "assets/demos/i2v")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

# Ensure tmp directory exists
os.makedirs(TMP_DIR, exist_ok=True)

# Video to pose mapping
# Format: (video_filename, pose_number)
v2v_videos = [
    ("00a0b28deb3c46889dca9c23f5ce7012_cam07.mp4", 7),
    ("00a0b28deb3c46889dca9c23f5ce7012_cam05.mp4", 5),
    ("00a587d336a348cdb3e149a49ca282f1_cam07.mp4", 7),
    ("00a587d336a348cdb3e149a49ca282f1_cam10.mp4", 10),
    ("00b543a310314893a1f2bac85d1f52e4_cam08.mp4", 8),
    ("00b543a310314893a1f2bac85d1f52e4_cam10.mp4", 10),
    ("00bb468618614ce783adefc4446239b1_cam02.mp4", 2),
    ("00bb468618614ce783adefc4446239b1_cam07.mp4", 7),
    ("00bf8a382c8f4b46b210a4bed2cd0602_cam08.mp4", 8),
    ("00bf8a382c8f4b46b210a4bed2cd0602_cam10.mp4", 10),
    ("00bfd68f27bf433e9ddfa16f43042945_cam05.mp4", 5),
    ("00bfd68f27bf433e9ddfa16f43042945_cam06.mp4", 6),
]

i2v_videos = [
    ("7_cam07.mp4", 7),
    ("7_cam10.mp4", 10),
    ("9_cam05.mp4", 5),
    ("9_cam09.mp4", 9),
    ("10_cam05.mp4", 5),
    ("10_cam09.mp4", 9),
    ("b93f5691ba1cc8890d0b0fb5792668d8c8e084e3b3ae1a476fc5e2c1e38b79ae_cam06.mp4", 6),
    ("b93f5691ba1cc8890d0b0fb5792668d8c8e084e3b3ae1a476fc5e2c1e38b79ae_cam07.mp4", 7),
    ("f20fc26d6d46029dc7dac01435523d4d015b27ef2d53bc415007ee695edc8a17_cam02.mp4", 2),
    ("f20fc26d6d46029dc7dac01435523d4d015b27ef2d53bc415007ee695edc8a17_cam03.mp4", 3),
]

def burn_overlay(video_path, pose_path, output_path):
    """
    Burn pose overlay onto video using ffmpeg.
    Overlay is a square with side length = 1/5 of video width.
    """
    # ffmpeg command to overlay image on video
    # scale2ref: set both width and height to video_width/5 to keep square shape
    # iw in scale2ref refers to the reference (video) width
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", pose_path,
        "-filter_complex",
        "[1:v][0:v]scale2ref=iw/5:iw/5[ovrl][main];[main][ovrl]overlay=W-w:H-h",
        "-c:a", "copy",
        output_path
    ]

    print(f"Processing: {os.path.basename(video_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    return True

def process_videos(video_list, video_dir):
    """Process a list of videos in a directory."""
    for video_name, pose_num in video_list:
        video_path = os.path.join(video_dir, video_name)
        pose_path = os.path.join(POSE_DIR, f"{pose_num}.png")
        tmp_output = os.path.join(TMP_DIR, video_name)

        if not os.path.exists(video_path):
            print(f"  SKIP: Video not found - {video_name}")
            continue

        if not os.path.exists(pose_path):
            print(f"  SKIP: Pose not found - {pose_num}.png")
            continue

        if burn_overlay(video_path, pose_path, tmp_output):
            # Replace original with processed video
            shutil.move(tmp_output, video_path)
            print(f"  OK: {video_name}")
        else:
            print(f"  FAILED: {video_name}")

if __name__ == "__main__":
    print("=" * 50)
    print("Burning pose overlays onto videos")
    print("=" * 50)

    print("\n--- Processing V2V videos ---")
    process_videos(v2v_videos, V2V_DIR)

    print("\n--- Processing I2V videos ---")
    process_videos(i2v_videos, I2V_DIR)

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)
