"""
Main script execution - load the dataset / learn classifiers
"""

from simple_dataset_loader import SimpleDatasetLoader
from simple_trainer import SimpleYOLOTrainer

def main():
    print("Speed Limit Recognition - Demo")
    print("=" * 50)

    print("\n Checking dataset...")
    loader = SimpleDatasetLoader()
    stats = loader.get_dataset_stats()

    total_images = sum(stats.values())
    if total_images == 0:
        print("No dataset found! Please run:")
        print("  python convert_to_yolo.py")
        return False

    print(f"Dataset ready: {total_images} total images")

    print("\n Sample images:")
    samples = loader.load_sample_images(count=3)
    for sample in samples:
        print(f"  {sample['path']}: {sample['shape']}")

    print("\n Starting training...")
    trainer = SimpleYOLOTrainer()

    results = trainer.train_model(epochs=2)

    if results:
        print("\nCompleted successfully!")
        return True
    else:
        print("\nFailed!")
        return False

if __name__ == "__main__":
    main()
