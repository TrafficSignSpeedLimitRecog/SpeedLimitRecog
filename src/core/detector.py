"""
Speed Sign Detector using YOLO
"""

import cv2
import yaml
import logging
import numpy as np

from pathlib import Path
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class SpeedSignDetector:
    """Detection class using trained YOLO model"""

    def __init__(self, model_path=None, config_path='config/settings.yaml'):
        self.model = None
        self.class_names = {}

        project_root = Path(__file__).resolve().parent.parent.parent
        config_full_path = project_root / config_path

        self.config = self._load_config(config_full_path)

        if model_path is None:
            model_path_str = self.config.get('model', {}).get('yolo_model', 'models/speed_limit_recog/weights/best.pt')
            model_path = project_root / model_path_str
        else:
            model_path = Path(model_path)
            if not model_path.is_absolute():
                model_path = project_root / model_path

        self.model_path = model_path
        self._load_model()

    @staticmethod
    def _load_config(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Config load failed: {e}, using defaults")
            return {
                'model': {
                    'confidence_threshold': 0.5,
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
                logger.error(f"Looking in: {self.model_path.absolute()}")
                logger.error(f"Current working directory: {Path.cwd()}")
                self.model = None
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            self.model = None

    @staticmethod
    def _preprocess_frame(image):
        enhanced = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)

        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

        return enhanced

    def _merge_detections(self, detections_list):
        if not detections_list:
            return []

        all_detections = []
        for dets in detections_list:
            all_detections.extend(dets)

        if not all_detections:
            return []

        merged = []
        used = set()

        for i, det1 in enumerate(all_detections):
            if i in used:
                continue

            similar = [det1]
            bbox1 = det1['bbox']

            for j, det2 in enumerate(all_detections[i+1:], i+1):
                if j in used:
                    continue

                bbox2 = det2['bbox']
                iou = self._calculate_iou_boxes(bbox1, bbox2)

                if iou > 0.5 and det1['class_name'] == det2['class_name']:
                    similar.append(det2)
                    used.add(j)

            avg_conf = sum(d['confidence'] for d in similar) / len(similar)

            x1 = int(np.mean([d['bbox'][0] for d in similar]))
            y1 = int(np.mean([d['bbox'][1] for d in similar]))
            x2 = int(np.mean([d['bbox'][2] for d in similar]))
            y2 = int(np.mean([d['bbox'][3] for d in similar]))

            merged_det = {
                'bbox': (x1, y1, x2, y2),
                'confidence': avg_conf,
                'class_id': det1['class_id'],
                'class_name': det1['class_name'],
                'speed_limit': det1['speed_limit']
            }
            merged.append(merged_det)
            used.add(i)

        return merged

    @staticmethod
    def _calculate_iou_boxes(box1, box2):
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2

        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)

        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)

        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area > 0 else 0

    def detect(self, image, conf_override=None, iou_override=None, multi_scale=False, enhance=False, tta=False):
        if self.model is None:
            logger.warning("Model not loaded, cannot detect")
            return image, []

        try:
            conf = conf_override if conf_override is not None else self.config.get('model', {}).get(
                'confidence_threshold', 0.5)
            iou = iou_override if iou_override is not None else self.config.get('model', {}).get('iou_threshold', 0.45)

            input_image = self._preprocess_frame(image) if enhance else image

            detections_list = []

            if multi_scale:
                for img_size in [640, 800, 1024]:
                    results = self.model(input_image, conf=conf*0.9, iou=iou, verbose=False, imgsz=img_size, augment=True)
                    dets = self._extract_detections(results)
                    detections_list.append(dets)
            else:
                results = self.model(input_image, conf=conf, iou=iou, verbose=False, imgsz=640)
                dets = self._extract_detections(results)
                detections_list.append(dets)

            if tta:
                flipped = cv2.flip(input_image, 1)
                results_flip = self.model(flipped, conf=conf*0.9, iou=iou, verbose=False, imgsz=640)
                dets_flip = self._extract_detections(results_flip)

                h, w = image.shape[:2]
                for det in dets_flip:
                    x1, y1, x2, y2 = det['bbox']
                    det['bbox'] = (w - x2, y1, w - x1, y2)

                detections_list.append(dets_flip)

            detections = self._merge_detections(detections_list)

            annotated = image.copy()
            for det in detections:
                annotated = self._draw_detection(annotated, det)

            return annotated, detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return image, []

    def _extract_detections(self, results):
        detections = []

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

        return detections

    def detect_batch(self, images, conf_override=None, iou_override=None, multi_scale=False, enhance=False):
        if self.model is None:
            logger.warning("Model not loaded, cannot detect")
            return [[] for _ in images]

        try:
            conf = conf_override if conf_override is not None else self.config.get('model', {}).get(
                'confidence_threshold', 0.5)
            iou = iou_override if iou_override is not None else self.config.get('model', {}).get('iou_threshold', 0.45)

            input_images = [self._preprocess_frame(img) for img in images] if enhance else images

            if multi_scale:
                results = self.model(input_images, conf=conf, iou=iou, verbose=False, imgsz=800, augment=True, stream=False)
            else:
                results = self.model(input_images, conf=conf, iou=iou, verbose=False, imgsz=640, stream=False)

            batch_results = []

            for idx, result in enumerate(results):
                detections = []

                if result.boxes is not None:
                    boxes = result.boxes

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

                batch_results.append(detections)

            return batch_results

        except Exception as e:
            logger.error(f"Batch detection failed: {e}")
            return [[] for _ in images]

    @staticmethod
    def _extract_speed_limit(class_name):
        try:
            return int(class_name)
        except:
            return None

    def update_parameters(self, conf=None, iou=None):
        if conf is not None:
            self.config['model']['confidence_threshold'] = conf
        if iou is not None:
            self.config['model']['iou_threshold'] = iou

    @staticmethod
    def _draw_detection(image, detection):
        x1, y1, x2, y2 = detection['bbox']
        conf = detection['confidence']
        speed = detection['speed_limit']

        if conf >= 0.8:
            color = (0, 255, 0)
        elif conf >= 0.6:
            color = (0, 165, 255)
        else:
            color = (0, 100, 255)

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
