"""
Convert processed classification dataset to YOLO detection format
"""

import cv2
import yaml

from pathlib import Path


def create_yolo_dataset():
    """Convert classification dataset to YOLO detection format"""

    # Paths
    source_dir = Path("datasets/processed/speed_signs")
    target_dir = Path("datasets/yolo_detection")

    # Create YOLO structure
    for split in ['train', 'val', 'test']:
        (target_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (target_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

    # Class mapping
    class_mapping = {
        'speed_20': 0,
        'speed_30': 1,
        'speed_40': 2,
        'speed_50': 3,
        'speed_70': 4,
        'speed_80': 5,
        'speed_90': 6,
        'speed_100': 7,
        'speed_120': 8,
        'other_signs': 9
    }

    total_images = 0

    # Process each split (train/val/test)
    for split in ['train', 'val', 'test']:
        split_path = source_dir / split

        if not split_path.exists():
            continue

        print(f" Processing {split} split...")

        # Process each class folder
        for class_folder in split_path.iterdir():
            if not class_folder.is_dir() or class_folder.name not in class_mapping:
                continue

            class_name = class_folder.name
            class_id = class_mapping[class_name]

            print(f"   * Processing {class_name} (ID: {class_id})")

            # Get all images
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(list(class_folder.glob(ext)))

            for i, img_path in enumerate(image_files):
                new_name = f"{class_name}_{split}_{i:04d}.jpg"

                # Copy image to YOLO structure
                target_img_path = target_dir / split / 'images' / new_name

                img = cv2.imread(str(img_path))
                if img is not None:
                    cv2.imwrite(str(target_img_path), img)

                    # Create YOLO label
                    label_path = target_dir / split / 'labels' / f"{new_name[:-4]}.txt"

                    # YOLO format: class_id center_x center_y width height (all normalized 0-1)
                    # Assume sign takes 80% of image, centered
                    with open(label_path, 'w') as f:
                        f.write(f"{class_id} 0.5 0.5 0.8 0.8\n")

                    total_images += 1

                    if (total_images % 100) == 0:
                        print(f"      Processed {total_images} images...")

    # Create YAML config for YOLO
    yaml_content = {
        'path': str(target_dir.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'nc': len(class_mapping),
        'names': {v: k for k, v in class_mapping.items()}
    }

    with open(target_dir / 'data.yaml', 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

    print(f"\n YOLO Dataset created!")
    print(f" Total images: {total_images}")
    print(f" Location: {target_dir}")
    print(f" Config: {target_dir}/data.yaml")

    return target_dir / 'data.yaml'


if __name__ == "__main__":
    config_path = create_yolo_dataset()
    print(f"\n Ready for training with: {config_path}")
