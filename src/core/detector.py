import cv2
import yaml
import logging

from pathlib import Path
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class SpeedSignDetector:
    """Detection class using trained YOLO model"""

    def __init__(self, model_path=None, config_path='config/settings.yaml'):
        self.model = None
        self.class_names = {}
        self.config = self._load_config(config_path)

        if model_path is None:
            model_path = self.config.get('model', {}).get('yolo_model', 'models/speed_limit_recog/weights/best.pt')
        self.model_path = Path(model_path)
        self._load_model()

    @staticmethod
    def _load_config(config_path):
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Config load failed: {e}, using defaults")
            return {
                'model': {
                    'confidence_threshold': 0.25,
                    'iou_threshold': 0.45
                }
            }

    def _load_model(self):
        try:
            if self.model_path.exists():
                self.model = YOLO(str(self.model_path))
                self.class_names = self.model.names
                logger.info(f"Model loaded: {self.model_path}")
            else:
                logger.error(f"Model not found: {self.model_path}")
                self.model = None
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            self.model = None

    def detect(self, image):
        if self.model is None:
            return image, []

        try:
            conf = self.config.get('model', {}).get('confidence_threshold', 0.25)
            iou = self.config.get('model', {}).get('iou_threshold', 0.45)

            results = self.model(image, conf=conf, iou=iou, verbose=False)

            detections = []
            annotated = image.copy()

            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes

                for box in boxes:
                    confidence = float(box.conf[0])
                    cls = int(box.cls[0])
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, xyxy)

                    class_name = self.class_names.get(cls, f'class_{cls}')
                    speed_limit = self._extract_speed_limit(class_name)

                    detection = {
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence,
                        'class_id': cls,
                        'class_name': class_name,
                        'speed_limit': speed_limit
                    }
                    detections.append(detection)
                    annotated = self._draw_detection(annotated, detection)

            return annotated, detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return image, []

    @staticmethod
    def _extract_speed_limit(class_name):
        try:
            return int(class_name)
        except:
            return None

    @staticmethod
    def _draw_detection(image, detection):
        x1, y1, x2, y2 = detection['bbox']
        conf = detection['confidence']
        speed = detection['speed_limit']

        color = (0, 255, 0) if speed else (255, 0, 0)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)

        label = f"{speed} km/h ({conf:.2f})" if speed else f"{detection['class_name']} ({conf:.2f})"

        font_scale = 0.8
        thickness = 2
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

        cv2.rectangle(image, (x1, y1 - h - 10), (x1 + w, y1), color, -1)
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, (255, 255, 255), thickness)

        return image

    def is_model_loaded(self):
        return self.model is not None
