"""
Preparing a dataset based on the current structure
"""

import cv2
import random

from pathlib import Path


def organize_current_data():
    """Organizes data structure"""

    class_mapping = {
        '20': '20',
        '30': '30',
        '40': '40',
        '50': '50',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
        '120': '120'
    }

    raw_positive = Path("datasets/raw/images/positive")
    raw_negative = Path("datasets/raw/images/negative")
    processed_dir = Path("datasets/processed/images")

    for split in ['train', 'valid', 'test']:
        for class_name in list(class_mapping.values()) + ['other']:
            (processed_dir / split / class_name).mkdir(parents=True, exist_ok=True)

    for speed_dir in raw_positive.iterdir():
        if speed_dir.is_dir() and speed_dir.name in class_mapping:
            speed_value = speed_dir.name
            new_class_name = class_mapping[speed_value]

            print(f" Processing class {speed_value} -> {new_class_name}")

            image_files = []
            for ext in ['.png', '.jpg', '.jpeg']:
                image_files.extend(speed_dir.glob(f'*{ext}'))

            if not image_files:
                print(f"[!] There are no images in {speed_dir}")
                continue

            # Split into train/valid/test (70/20/10)
            random.shuffle(image_files)
            n_total = len(image_files)
            n_train = int(n_total * 0.7)
            n_val = int(n_total * 0.2)

            train_files = image_files[:n_train]
            val_files = image_files[n_train:n_train + n_val]
            test_files = image_files[n_train + n_val:]

            # Process and copy files
            for split_name, files in [('train', train_files), ('valid', val_files), ('test', test_files)]:
                if not files:
                    continue

                target_dir = processed_dir / split_name / new_class_name

                for i, img_path in enumerate(files):
                    try:
                        img = cv2.imread(str(img_path))
                        if img is None:
                            continue

                        img_resized = cv2.resize(img, (128, 128))

                        new_name = f"{new_class_name}_{split_name}_{i:04d}.png"
                        output_path = target_dir / new_name
                        cv2.imwrite(str(output_path), img_resized)

                    except Exception as e:
                        print(f" Processing error {img_path}: {e}")
                        continue

            print(f" {new_class_name}: {len(train_files)} train, {len(val_files)} valid, {len(test_files)} test")

    if raw_negative.exists():
        print(" Negative images processing...")

        negative_files = []
        for ext in ['.png', '.jpg', '.jpeg']:
            negative_files.extend(raw_negative.rglob(f'*{ext}'))

        if negative_files:
            random.shuffle(negative_files)
            n_total = len(negative_files)
            n_train = int(n_total * 0.7)
            n_val = int(n_total * 0.2)

            train_neg = negative_files[:n_train]
            val_neg = negative_files[n_train:n_train + n_val]
            test_neg = negative_files[n_train + n_val:]

            for split_name, files in [('train', train_neg), ('valid', val_neg), ('test', test_neg)]:
                if not files:
                    continue

                target_dir = processed_dir / split_name / 'other'

                for i, img_path in enumerate(files):
                    try:
                        img = cv2.imread(str(img_path))
                        if img is None:
                            continue

                        img_resized = cv2.resize(img, (128, 128))

                        new_name = f"other_signs_{split_name}_{i:04d}.png"
                        output_path = target_dir / new_name
                        cv2.imwrite(str(output_path), img_resized)

                    except Exception as e:
                        continue

            print(f" other: {len(train_neg)} train, {len(val_neg)} valid, {len(test_neg)} test")

    print("\n DATA ORGANIZATION SUMMARY:")
    for split in ['train', 'valid', 'test']:
        split_dir = processed_dir / split
        if split_dir.exists():
            for class_dir in split_dir.iterdir():
                if class_dir.is_dir():
                    count = len(list(class_dir.glob('*.png')))
                    print(f"   {split}/{class_dir.name}: {count} images")

    print("\n Data organization completed!")
    return True

if __name__ == "__main__":
    random.seed(42)
    success = organize_current_data()
    if success:
        print("\n Dataset ready for training!")
