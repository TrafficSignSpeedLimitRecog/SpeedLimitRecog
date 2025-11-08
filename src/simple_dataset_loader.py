"""
Simple YOLO dataset loader for SpeedLimitRecognition
"""

import cv2
import yaml

from pathlib import Path


class SimpleDatasetLoader:
    """First version of loading dataset in YOLO format"""

    def __init__(self, dataset_path="datasets/yolo_detection"):
        self.config = None
        self.dataset_path = Path(dataset_path)
        self.config_path = self.dataset_path / "data.yaml"
        self.load_config()

    def load_config(self):
        """Loading the dataset configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"Dataset config loaded: {self.config['nc']} classes")
            print(f"Classes: {list(self.config['names'].values())}")
        except Exception as e:
            print(f"Error loading config: {e}")

    def get_dataset_stats(self):
        """Get dataset statistics"""
        stats = {}

        for split in ['train', 'valid', 'test']:
            split_path = self.dataset_path / split / 'images'
            if split_path.exists():
                image_count = len(list(split_path.glob('*.jpg'))) + len(list(split_path.glob('*.png')))
                stats[split] = image_count
            else:
                stats[split] = 0

        return stats

    def load_sample_images(self, split='train', count=5):
        """Load sample images"""
        images_path = self.dataset_path / split / 'images'
        image_files = list(images_path.glob('*.jpg'))[:count]

        samples = []
        for img_path in image_files:
            img = cv2.imread(str(img_path))
            if img is not None:
                samples.append({
                    'path': img_path.name,
                    'shape': img.shape,
                    'size_kb': img_path.stat().st_size // 1024
                })

        return samples


if __name__ == "__main__":
    loader = SimpleDatasetLoader()

    stats = loader.get_dataset_stats()
    print("\nDataset Statistics:")
    for split, count in stats.items():
        print(f"  {split}: {count} images")

    samples = loader.load_sample_images(count=3)
    print("\n Sample Images:")
    for sample in samples:
        print(f"  {sample['path']}: {sample['shape']} ({sample['size_kb']} KB)")
