"""
YOLO Trainer for Speed Limit Recognition
"""

import torch
import logging
import sys

from datetime import datetime
from ultralytics import YOLO
from pathlib import Path

class DualLogger:
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleYOLOTrainer:

    def __init__(self, model_name="yolov8m.pt"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.training_start_time = None
        self.training_end_time = None
        logger.info(f"Trainer initialized: model={self.model_name}, device={self.device}")

    def train_model(self, data_config="datasets/yolo_detection/data.yaml", epochs=300):
        logger.info(f"Starting training: config={data_config}, epochs={epochs}")
        self.training_start_time = datetime.now()

        try:
            model = YOLO(self.model_name)

            results = model.train(
                # --- General Training Configuration ---
                data=data_config,           # Path to dataset YAML file (defines train/val/test paths).
                epochs=epochs,              # Total number of training iterations.
                imgsz=640,                  # Input image size (pixels). Higher = better small obj detection, slower speed.
                batch=16,                   # Batch size. Number of images processed at once. Reduce if CUDA OOM error.
                patience=20,                # Early Stopping: Stop training if metric doesn't improve for 20 epochs.
                save=True,                  # Save model checkpoints (best.pt and last.pt).
                plots=True,                 # Generate training graphs (loss curves, confusion matrix, labels).

                # --- Output Management ---
                name='speed_limit_recog',   # Subdirectory name for saving results.
                project='models',           # Root directory where results are saved.
                exist_ok=True,              # If True, does not error if the directory already exists (overwrites/appends).

                # --- Hardware & Performance ---
                device=self.device,         # Computation device ('cuda' for GPU or 'cpu').
                workers=8,                  # Number of CPU threads for data loading (prevents GPU waiting for data).
                amp=True,                   # Automatic Mixed Precision (FP16). Faster training, uses less VRAM.
                cache=False,                # Data caching. Set to True (RAM) if you have lots of RAM (>32GB) for faster training.

                # --- Optimization Dynamics ---
                optimizer='auto',           # Optimization algorithm (usually selects AdamW or SGD automatically).
                weight_decay=0.0005,        # L2 Regularization. Penalizes large weights to reduce overfitting.
                warmup_epochs=3.0,          # "Warmup" period. Uses lower learning rate at start to stabilize gradients.

                # --- Photometric Augmentations (Lighting & Color) ---
                hsv_h=0.025,                # Hue (2.5% shift). Simulates different camera color sensors.
                hsv_s=0.8,                  # Saturation (80% var). CRITICAL: Simulates rainy (dull) vs sunny (vivid) weather.
                hsv_v=0.5,                  # Value/Brightness (50% var). Simulates shadows, tunnels, and sun glare.

                # --- Geometric Augmentations (Position & Shape) ---
                degrees=15.0,               # Rotation (+/- 15 deg). Handles tilted signs or banking car motion.
                translate=0.2,              # Translation (+/- 20%). Model learns signs aren't always centered.
                scale=0.7,                  # Scale (+/- 70%). KEY FOR VIDEO: Detects signs both far away (dots) and very close.
                shear=5.0,                  # Shear (+/- 5 deg). Simulates perspective distortion (viewing angle).
                perspective=0.001,          # Perspective (0-0.001). Slight 3D depth effect.
                flipud=0.0,                 # Vertical flip (Disabled). Traffic signs are never upside down.
                fliplr=0.5,                 # Horizontal flip (50%). Learns general shape symmetry.

                # --- Advanced Regularization (Structure & Overfitting) ---
                mosaic=1.0,             # Mosaic (100%). Stitches 4 images. Forces model to learn context/small objects.
                mixup=0.15,             # MixUp (15%). Blends 2 images. Smooths decision boundaries for ambiguous inputs.
                copy_paste=0.1,         # Copy-Paste (10%). Pastes signs onto random backgrounds to increase density.

                # --- Training Hyperparameters ---
                box=7.5,                # Box loss gain. Higher = stricter bounding box accuracy.
                cls=0.5,                # Class loss gain.
                dfl=1.5,                # Distribution Focal Loss.
                close_mosaic=15,        # Disable Mosaic for the last 15 epochs to stabilize training.
                dropout=0.2,            # Dropout (20%). Randomly drops neurons to prevent memorization (overfitting).
            )

            self.training_end_time = datetime.now()
            logger.info("Training completed successfully")
            return results

        except Exception as e:
            self.training_end_time = datetime.now()
            logger.error(f"Training failed: {e}")
            raise

    @staticmethod
    def validate_model(model_path, data_config="datasets/yolo_detection/data.yaml"):
        try:
            logger.info(f"Validating model: {model_path}")
            model = YOLO(model_path)
            results = model.val(
                data=data_config,
                split='test',
                project='models',
                name='speed_limit_recog',
                exist_ok=True
            )

            logger.info(f"Validation results: mAP@50={results.box.map50:.3f}, "
                       f"mAP@50-95={results.box.map:.3f}")
            return results

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def generate_summary(self, val_results=None):
        duration = self.training_end_time - self.training_start_time if self.training_start_time else None

        summary = []
        summary.append("=" * 80)
        summary.append("TRAINING SUMMARY")
        summary.append("=" * 80)
        summary.append(f"Start Time: {self.training_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"End Time: {self.training_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Duration: {duration}")
        summary.append(f"Model: {self.model_name}")
        summary.append(f"Device: {self.device}")
        summary.append(f"Epochs: 300 (with patience=20 early stopping)")
        summary.append(f"Batch Size: 16")
        summary.append(f"Image Size: 640x640")
        summary.append(f"Optimizer: auto")
        summary.append("")
        summary.append("Augmentation Settings:")
        summary.append("  - HSV: h=0.025, s=0.8, v=0.5")
        summary.append("  - Geometric: degrees=15, translate=0.2, scale=0.7, shear=5")
        summary.append("  - Flip: horizontal=0.5, vertical=0.0")
        summary.append("  - Mosaic: 1.0")
        summary.append("  - Mixup: 0.15")
        summary.append("  - Copy-Paste: 0.1")
        summary.append("  - Dropout: 0.2")
        summary.append("")

        if val_results:
            summary.append("Final Validation Results (Test Set):")
            summary.append(f"  mAP@50: {val_results.box.map50:.4f}")
            summary.append(f"  mAP@50-95: {val_results.box.map:.4f}")
            summary.append(f"  Precision: {val_results.box.mp:.4f}")
            summary.append(f"  Recall: {val_results.box.mr:.4f}")

        summary.append("")
        summary.append("Model Location:")
        summary.append("  models/speed_limit_recog/weights/best.pt")
        summary.append("  models/speed_limit_recog/weights/last.pt")
        summary.append("")
        summary.append("Plots and Logs:")
        summary.append("  models/speed_limit_recog/")
        summary.append("=" * 80)

        return "\n".join(summary)


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    detailed_log_path = log_dir / f"training_detailed_{timestamp}.log"
    summary_log_path = log_dir / f"training_summary_{timestamp}.txt"

    dual_logger = DualLogger(str(detailed_log_path))
    sys.stdout = dual_logger
    sys.stderr = dual_logger

    try:
        data_path = Path("datasets/yolo_detection/data.yaml")

        if not data_path.exists():
            logger.error(f"Dataset configuration not found: {data_path}")
            raise FileNotFoundError(f"Missing dataset: {data_path}")

        trainer = SimpleYOLOTrainer(model_name="yolov8m.pt")

        trainer.train_model(epochs=300)

        best_model_path = Path("models/speed_limit_recog/weights/best.pt")
        val_results = None
        if best_model_path.exists():
            val_results = trainer.validate_model(str(best_model_path))

        summary = trainer.generate_summary(val_results)
        print("\n")
        print(summary)

        with open(summary_log_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"\nDetailed log saved to: {detailed_log_path}")
        print(f"Summary saved to: {summary_log_path}")

    finally:
        dual_logger.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


if __name__ == "__main__":
    main()
