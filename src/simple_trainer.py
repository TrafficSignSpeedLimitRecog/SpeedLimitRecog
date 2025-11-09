"""
YOLO Trainer for Speed Limit Recognition
"""

import torch
import shutil
import logging
from ultralytics import YOLO
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleYOLOTrainer:
    """YOLO model trainer"""

    def __init__(self, model_name="yolov8s.pt"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Trainer initialized: model={self.model_name}, device={self.device}")

    def train_model(self, data_config="datasets/yolo_detection/data.yaml", epochs=100):
        """Train YOLO model"""
        logger.info(f"Starting training: config={data_config}, epochs={epochs}")

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
                cache=True,
                optimizer='AdamW',
                lr0=0.001,
                lrf=0.01,
                momentum=0.937,
                weight_decay=0.0005,
                warmup_epochs=3,
                hsv_h=0.015,
                hsv_s=0.7,
                hsv_v=0.4,
                degrees=10.0,
                translate=0.1,
                scale=0.5,
                flipud=0.0,
                fliplr=0.5,
                mosaic=1.0,
                mixup=0.1
            )

            logger.info("Training completed successfully")
            return results

        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    @staticmethod
    def validate_model(model_path, data_config="datasets/yolo_detection/data.yaml"):
        """Validate trained model"""
        try:
            logger.info(f"Validating model: {model_path}")
            model = YOLO(model_path)
            results = model.val(data=data_config)

            logger.info(f"Validation results: mAP@50={results.box.map50:.3f}, "
                       f"mAP@50-95={results.box.map:.3f}")
            return results

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    @staticmethod
    def clear_cache(dataset_path="datasets/yolo_detection"):
        """Clear YOLO cache files"""
        dataset_dir = Path(dataset_path)
        cache_files = list(dataset_dir.glob("*/labels.cache"))

        for cache_file in cache_files:
            try:
                cache_file.unlink()
                logger.info(f"Removed cache: {cache_file}")
            except Exception as e:
                logger.warning(f"Failed to remove {cache_file}: {e}")

    @staticmethod
    def clear_old_model(model_dir="models/speed_limit_recog"):
        """Remove old model directory"""
        model_path = Path(model_dir)
        if model_path.exists():
            try:
                shutil.rmtree(model_path)
                logger.info(f"Removed old model: {model_path}")
            except Exception as e:
                logger.warning(f"Failed to remove {model_path}: {e}")


def main():
    data_path = Path("datasets/yolo_detection/data.yaml")

    if not data_path.exists():
        logger.error(f"Dataset configuration not found: {data_path}")
        raise FileNotFoundError(f"Missing dataset: {data_path}")

    trainer = SimpleYOLOTrainer(model_name="yolov8s.pt")

    # Clear old cache and model
    trainer.clear_cache()
    trainer.clear_old_model()

    # Train
    results = trainer.train_model(epochs=100)

    best_model_path = Path("models/speed_limit_recog/weights/best.pt")
    if best_model_path.exists():
        trainer.validate_model(str(best_model_path))


if __name__ == "__main__":
    main()
