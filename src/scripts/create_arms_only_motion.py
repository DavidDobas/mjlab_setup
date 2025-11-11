"""Extract arms-only motion segment from a full-body motion CSV.

This script:
1. Extracts a time segment from the motion
2. Keeps the original arm joint values
3. Replaces legs and waist with neutral standing pose
4. Keeps the root position and orientation stationary
"""

import numpy as np
import tyro
from pathlib import Path


def main(
    input_file: str = "motions_csv/30fps/lafang/dance1_subject2.csv",
    output_file: str = "motions_csv/30fps/lafang/dance1_subject2_arms_only.csv",
    start_time: float = 0.0,
    end_time: float = 5.0,
    fps: float = 30.0,
    keep_root_moving: bool = False,
):
    """Extract arms-only motion segment.
    
    Args:
        input_file: Path to input CSV file with full motion.
        output_file: Path to output CSV file for arms-only motion.
        start_time: Start time in seconds.
        end_time: End time in seconds.
        fps: Frame rate of the motion.
        keep_root_moving: If True, keep original root position/orientation. 
                         If False, freeze root at start position.
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
    
    print(f"\nExtracting segment:")
    print(f"  Time range: {start_time:.2f}s to {end_time:.2f}s")
    print(f"  Frame range: {start_frame} to {end_frame}")
    print(f"  Duration: {end_time - start_time:.2f}s ({end_frame - start_frame} frames)")
    
    # Extract segment
    segment = data[start_frame:end_frame].copy()
    
    # Define neutral pose for legs and waist (from pkl_to_csv.py SAFE_POSE_JOINTS)
    neutral_left_leg = np.array([-0.312, 0, 0, 0.669, -0.363, 0])    # 6 DOF
    neutral_right_leg = np.array([-0.312, 0, 0, 0.669, -0.363, 0])   # 6 DOF  
    neutral_waist = np.array([0, 0, 0])                               # 3 DOF
    
    print("\nApplying modifications:")
    print("  - Keeping original arm motion")
    print(f"  - Setting legs and waist to neutral standing pose")
    
    if not keep_root_moving:
        print("  - Freezing root position and orientation at start frame")
        # Save first frame root state
        first_root_pos = segment[0, 0:3].copy()
        first_root_quat = segment[0, 3:7].copy()
    
    # Joint structure in CSV (after 7 columns of root_pos(3) + quat_xyzw(4)):
    # Indices in the joint array (starting from column 7):
    # [7:13]   - left leg (6 DOF)
    # [13:19]  - right leg (6 DOF)
    # [19:22]  - waist (3 DOF)
    # [22:29]  - left arm (7 DOF)
    # [29:36]  - right arm (7 DOF)
    
    for i in range(len(segment)):
        if not keep_root_moving:
            segment[i, 0:3] = first_root_pos     # fix root position
            segment[i, 3:7] = first_root_quat    # fix root orientation
        
        segment[i, 7:13] = neutral_left_leg      # neutral left leg
        segment[i, 13:19] = neutral_right_leg    # neutral right leg
        segment[i, 19:22] = neutral_waist        # neutral waist
        # Arms (columns 22:36) keep original values
    
    # Save modified motion
    print(f"\nSaving arms-only motion to: {output_file}")
    
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
    print(f"  Format: [root_pos(3), quat_xyzw(4), joints(29)]")
    print(f"\nYou can now convert this to NPZ format:")
    print(f"  MUJOCO_GL=egl uv run -m mjlab.scripts.csv_to_npz \\")
    print(f"      --input-file {output_file} \\")
    print(f"      --output-name dance1_arms_only \\")
    print(f"      --input-fps {int(fps)} \\")
    print(f"      --output-fps 50 \\")
    print(f"      --render")


if __name__ == "__main__":
    tyro.cli(main)

