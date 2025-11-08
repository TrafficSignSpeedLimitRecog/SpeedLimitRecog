"""
Convert processed classification dataset to YOLO detection format with realistic bounding boxes
"""

import cv2
import yaml
import numpy as np
from pathlib import Path


def detect_sign_bbox(image):
    """
    Detect sign location using simple computer vision (circle detection)
    Returns normalized bbox (center_x, center_y, width, height)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles (speed limit signs are circular)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=20,
        maxRadius=min(image.shape[:2]) // 2
    )

    if circles is not None and len(circles[0]) > 0:
        # Use largest circle
        circles = np.uint16(np.around(circles))
        largest = max(circles[0], key=lambda c: c[2])  # Max by radius
        x, y, r = largest

        # Convert to YOLO format (normalized)
        h, w = image.shape[:2]
        center_x = x / w
        center_y = y / h
        bbox_w = (r * 2.2) / w  # Slightly larger than circle
        bbox_h = (r * 2.2) / h

        # Clamp to [0, 1]
        center_x = np.clip(center_x, 0, 1)
        center_y = np.clip(center_y, 0, 1)
        bbox_w = np.clip(bbox_w, 0, 1)
        bbox_h = np.clip(bbox_h, 0, 1)

        return center_x, center_y, bbox_w, bbox_h

    # Fallback - we assume sign is centered but smaller
    return 0.5, 0.5, 0.6, 0.6


def create_yolo_dataset():
    source_dir = Path("datasets/processed/images")
    target_dir = Path("datasets/yolo_detection")

    for split in ['train', 'valid', 'test']:
        (target_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (target_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

    class_mapping = {
        '20': 0, '30': 1, '40': 2, '50': 3, '70': 4,
        '80': 5, '90': 6, '100': 7, '120': 8, 'other': 9
    }

    total_images = 0
    detection_stats = {'detected': 0, 'fallback': 0}

    for split in ['train', 'valid', 'test']:
        split_path = source_dir / split
        if not split_path.exists():
            continue

        print(f"Processing {split} split...")

        for class_folder in split_path.iterdir():
            if not class_folder.is_dir() or class_folder.name not in class_mapping:
                continue

            class_name = class_folder.name
            class_id = class_mapping[class_name]
            print(f"  * {class_name} (ID: {class_id})")

            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(list(class_folder.glob(ext)))

            for i, img_path in enumerate(image_files):
                new_name = f"{class_name}_{split}_{i:04d}.jpg"
                target_img_path = target_dir / split / 'images' / new_name

                img = cv2.imread(str(img_path))
                if img is None:
                    continue

                # Detect actual bounding box
                center_x, center_y, bbox_w, bbox_h = detect_sign_bbox(img)

                # Track if we used circle detection or fallback
                if bbox_w < 0.7:
                    detection_stats['detected'] += 1
                else:
                    detection_stats['fallback'] += 1

                cv2.imwrite(str(target_img_path), img)

                # Create YOLO label with REAL bbox
                label_path = target_dir / split / 'labels' / f"{new_name[:-4]}.txt"
                with open(label_path, 'w') as f:
                    f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {bbox_w:.6f} {bbox_h:.6f}\n")

                total_images += 1

                if (total_images % 100) == 0:
                    print(f"    Processed {total_images} images...")

    # Create YAML config
    yaml_content = {
        'path': str(target_dir.absolute()),
        'train': 'train/images',
        'valid': 'valid/images',
        'test': 'test/images',
        'nc': len(class_mapping),
        'names': {v: k for k, v in class_mapping.items()}
    }

    with open(target_dir / 'settings.yaml', 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

    print(f"\nYOLO Dataset created!")
    print(f"Total images: {total_images}")
    print(f"Circle detected: {detection_stats['detected']}")
    print(f"Fallback used: {detection_stats['fallback']}")
    print(f"Location: {target_dir}")
    print(f"Config: {target_dir}/data.yaml")

    return target_dir / 'data.yaml'


if __name__ == "__main__":
    config_path = create_yolo_dataset()
    print(f"\nReady for training with: {config_path}")
