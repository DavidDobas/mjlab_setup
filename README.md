## Installation

1. Clone mjlab:

```bash
git clone https://github.com/mujocolab/mjlab
```

2. Clone this repo:

```bash
git clone https://github.com/DavidDobas/mjlab_setup
cd mjlab_setup
```

3. Install dependencies using uv sync (assuming mjlab is now in `../mjlab`):

```bash
uv sync
```

4. Download the required csv data from [this Google Drive folder](https://drive.google.com/drive/folders/1-qpHdq5N7E0VBkaaI3MC79NhmSKjYmnt?usp=sharing) - we provide sample in `data/lafang_original`

## Data Processing Workflow

### 1. Visualize CSV in Rerun

Quickly preview your motion data using Rerun's 3D visualization (G1 robot only):

```bash
python src/scripts/rerun_visualize.py --file_name data/lafang_original/fight1_subject2.csv 
```

Replace with your filename.

### 2. Crop Motion by Time

Extract a specific time segment from your motion data:

```bash
python src/scripts/crop_motion.py \
  --input-file data/lafang_original/fight1_subject2.csv \
  --output-file data/lafang_cropped/fight1_subject2_0to10s.csv \
  --start-time 0.0 \
  --end-time 10.0
```

**Note:** If your dataset has a different FPS, you can set it with the optional `--fps` parameter (default: 30.0).

### 3. (Optional) Convert to Arms-Only Motion

Create an arms-only motion by freezing the root and replacing legs/waist with a neutral standing pose:

```bash
python src/scripts/create_arms_only_motion.py \
  --input-file data/lafang_original/fight1_subject2.csv \
  --output-file data/lafang_arms_only/fight1_subject2_arms_only_0to10s.csv \
  --start-time 0.0 \
  --end-time 10.0
```

This script also crops the motion to the specified time range.

### 4. Convert CSV to NPZ

Convert CSV motion data to NPZ format for training. This script:
- Simulates the motion in MuJoCo
- Computes joint velocities and other physics-based data
- Uploads the NPZ file to Weights & Biases
- **Optionally renders and saves a video to `renders/{input_name}.mp4`**

**Setup:**

1. In Weights and Biases, create a Registry called `Motions`. Follow the official guide: [How to create a Registry in W&B Models](https://docs.wandb.ai/models/registry/create_registry)

2. Run the conversion:

```bash
MUJOCO_GL=egl python src/scripts/csv_to_npz.py \
  --input-file {your_csv_file} \
  --output-name {your_wandb_output_name} \
  --input-fps 30 \
  --output-fps 50 \
  --render
```

The `--render` flag is optional but recommended for verification. Videos are saved to `renders/` directory with the same base name as the input CSV.

## Training

Train the motion tracking policy using the processed motion data:

```bash
MUJOCO_GL=egl uv run train Mjlab-Tracking-Flat-Unitree-G1 \
  --registry-name {your_organization}-org/wandb-registry-Motions/{your_wandb_output_name} \
  --env.scene.num-envs 4096
```

**Note:** Replace `{your_organization}` with your actual Weights & Biases organization name, and `{your_wandb_output_name}` with the name you used in step 4.

## Visualizing Training

To visualize the trained policy in real-time:

1. **Find your run ID:** When training starts, W&B prints a URL like:
   ```
   wandb: 🚀 View run at https://wandb.ai/{your_org}/mjlab/runs/abc12xyz
   ```
   Copy the run ID (e.g., `abc12xyz`) from the URL or from your W&B dashboard.

2. **Run the visualization:**
   ```bash
   uv run play Mjlab-Tracking-Flat-Unitree-G1 \
     --wandb-run-path {your_organization}/mjlab/{run_id} \
     --num-envs 8
   ```

The run path format is: `{your_organization}/mjlab/{run_id}` where `mjlab` is the default project name.