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

    def __init__(self, model_name="yolov8s.pt"):
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
                data=data_config,
                epochs=epochs,
                imgsz=640,
                batch=16,
                patience=20,
                save=True,
                plots=True,
                name='speed_limit_recog',
                project='models',
                exist_ok=True,
                device=self.device,
                workers=8,
                amp=True,
                cache=False,
                optimizer='auto',
                weight_decay=0.0005,
                warmup_epochs=3.0,
                hsv_h=0.025,
                hsv_s=0.8,
                hsv_v=0.5,
                degrees=15.0,
                translate=0.2,
                scale=0.7,
                shear=5.0,
                perspective=0.001,
                flipud=0.0,
                fliplr=0.5,
                mosaic=1.0,
                mixup=0.15,
                copy_paste=0.1,
                box=7.5,
                cls=0.5,
                dfl=1.5,
                close_mosaic=15,
                dropout=0.2,
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
