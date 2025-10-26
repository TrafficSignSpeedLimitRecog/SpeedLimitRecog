"""
Prototype of trainer YOLO for SpeedLimitRecognition
"""

import torch

from ultralytics import YOLO
from pathlib import Path


class SimpleYOLOTrainer:
    """Simple trainer YOLO model"""

    def __init__(self, model_name="yolov8n.pt"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

    def train_model(self, data_config="datasets/yolo_detection/data.yaml", epochs=5):
        """Demonstration of training YOLO model for SpeedLimitRecognition"""
        print(f"Starting YOLO training...")
        print(f"Data config: {data_config}")
        print(f"Epochs: {epochs}")

        try:
            model = YOLO(self.model_name)
            print(f"Model {self.model_name} loaded")

            # Model training
            results = model.train(
                data=data_config,
                epochs=epochs,
                imgsz=640,
                batch=16,  # Smaller batch for demo
                patience=3,
                save=True,
                plots=True,
                name='speed_limit_recog',
                project='models',
                exist_ok=True
            )

            print("Training completed!")
            print(f"Results saved in: models/speed_limit_recog/")
            print(f"Best weights: models/speed_limit_recog/weights/best.pt")

            return results

        except Exception as e:
            print(f"Training error: {e}")
            return None

    @staticmethod
    def validate_model(model_path, data_config="datasets/yolo_detection/data.yaml"):
        """Validation of the trained model"""
        try:
            model = YOLO(model_path)
            results = model.val(data=data_config)

            print("\nValidation Results:")
            print(f"  mAP@50: {results.box.map50:.3f}")
            print(f"  mAP@50-95: {results.box.map:.3f}")

            return results

        except Exception as e:
            print(f"Validation error: {e}")
            return None


if __name__ == "__main__":
    trainer = SimpleYOLOTrainer()

    data_path = Path("datasets/yolo_detection/data.yaml")
    if data_path.exists():
        print("Dataset found, starting training...")
        results = trainer.train_model(epochs=2)
    else:
        print("Dataset not found. Run convert_to_yolo.py first!")
