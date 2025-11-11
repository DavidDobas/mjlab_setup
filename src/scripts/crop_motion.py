"""Crop a motion CSV file by start and end time.

This script extracts a time segment from a motion capture CSV file
without modifying the motion data itself.
"""

import numpy as np
import tyro
from pathlib import Path


def main(
    input_file: str,
    output_file: str,
    start_time: float = 0.0,
    end_time: float = 5.0,
    fps: float = 30.0,
):
    """Crop motion to specified time range.
    
    Args:
        input_file: Path to input CSV file with motion data.
        output_file: Path to output CSV file for cropped motion.
        start_time: Start time in seconds.
        end_time: End time in seconds.
        fps: Frame rate of the motion.
    """
    print(f"Loading motion from: {input_file}")
    data = np.loadtxt(input_file, delimiter=",")
    
    print(f"Original motion shape: {data.shape}")
    print(f"Total duration: {data.shape[0] / fps:.2f} seconds ({data.shape[0]} frames)")
    
    # Calculate frame indices
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    
    # Validate frame range
    if start_frame < 0 or end_frame > data.shape[0]:
        print(f"ERROR: Requested time range [{start_time}s, {end_time}s] = frames [{start_frame}, {end_frame}]")
        print(f"       exceeds available motion (0 to {data.shape[0] / fps:.2f}s)")
        return
    
    if start_frame >= end_frame:
        print(f"ERROR: Start time ({start_time}s) must be less than end time ({end_time}s)")
        return
    
    print(f"\nCropping segment:")
    print(f"  Time range: {start_time:.2f}s to {end_time:.2f}s")
    print(f"  Frame range: {start_frame} to {end_frame}")
    print(f"  Duration: {end_time - start_time:.2f}s ({end_frame - start_frame} frames)")
    
    # Extract segment
    segment = data[start_frame:end_frame].copy()
    
    # Save cropped motion
    print(f"\nSaving cropped motion to: {output_file}")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    np.savetxt(output_file, segment, delimiter=",", fmt="%.8f")
    
    print("\n✓ Done!")
    print(f"\nOutput summary:")
    print(f"  File: {output_file}")
    print(f"  Shape: {segment.shape}")
    print(f"  Duration: {segment.shape[0] / fps:.2f}s")
    print(f"  Frames: {segment.shape[0]}")


if __name__ == "__main__":
    tyro.cli(main)

