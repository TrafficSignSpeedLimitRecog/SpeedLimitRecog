# 🚦 Speed Limit Detection System

Speed limit sign detection using YOLOv8. Detects speed limit signs in images and videos.

![Python](https://img.shields.io/badge/python-3.12-blue) ![PyTorch](https://img.shields.io/badge/pytorch-2.5-red) ![YOLOv8](https://img.shields.io/badge/yolo-v8-orange)

---

## 🛠️ Tech Stack

- YOLOv8m (Ultralytics)
- PyTorch 2.5 + CUDA 12.1
- PySide6 (Qt6)
- OpenCV

## 📊 Dataset Stats

- **Total Images:** 6,304
- **Train:** 4,656 (73.8%)
- **Valid:** 1,086 (17.2%)
- **Test:** 562 (8.9%)
- **Classes:** 10 ['20', '30', '40', '50', '60', '70', '80', '100', '120', 'speed-sign-end']
- **Format:** YOLO v8 PyTorch

## 🎯 Performance (YOLOv8m)

The model was trained on the `yolov8m` architecture with aggressive augmentation to ensure stability on real-world video footage.

| Metric              | Value                | Notes                                   |
|---------------------|----------------------|-----------------------------------------|
| **mAP@50**          | **98.9%**            | Extremely reliable detection            |
| **mAP@50-95**       | **84.4%**            | High precision bounding boxes           |
| **Precision**       | **99.1%**            | Almost zero false positives (Excellent) |
| **Recall**          | **98.1%**            | Misses less than 2% of signs            |
| **Inference Speed** | **3.4ms (~294 FPS)** | Benchmarked on RTX 4090 (Batch=16)      |
| **Training Time**   | **2.0h**             | 300 epochs (Early Stopping at 196)      |

### Per-Class Performance (Test Set)

| Class          | Precision | Recall   | mAP@50 | mAP@50-95 |
|----------------|-----------|----------|--------|-----------|
| 20 km/h        | 98.2%     | 96.7%    | 97.3%  | 82.5%     |
| 30 km/h        | **100%**  | 97.3%    | 99.4%  | 82.3%     |
| 40 km/h        | 98.0%     | **100%** | 99.5%  | 85.6%     |
| 50 km/h        | 99.8%     | 97.2%    | 99.3%  | **88.3%** |
| 60 km/h        | 97.5%     | 97.9%    | 96.2%  | 81.2%     |
| 70 km/h        | 99.7%     | **100%** | 99.5%  | 81.3%     |
| 80 km/h        | 99.6%     | 98.5%    | 99.4%  | 87.4%     |
| 100 km/h       | **100%**  | 94.9%    | 99.5%  | 84.1%     |
| 120 km/h       | 99.9%     | 98.7%    | 99.4%  | 82.3%     |
| speed-sign-end | 98.8%     | **100%** | 99.5%  | **88.6%** |

### 🏆 Model Training Comparison: YOLOv8s vs YOLOv8m

The table below highlights the performance shift from the previous baseline (Small - image optimized) to the current production model (Medium - video & robustness optimized).

| Metric              | YOLOv8s (Previous) | YOLOv8m (Current) |  Change   | Interpretation                                                                                                                                             |
|:--------------------|:------------------:|:-----------------:|:---------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Precision**       |       98.1%        |     **99.1%**     | **+1.0%** | **Major improvement.** The M model produces significantly fewer False Positives (e.g., mistaking billboards for signs).                                    |
| **mAP@50**          |       99.0%        |       98.9%       |   -0.1%   | Negligible difference. Detection capability remains near-perfect.                                                                                          |
| **mAP@50-95**       |       85.9%        |       84.4%       |   -1.5%   | Expected drop due to heavy augmentation. The model traded pixel-perfect box alignment on static images for better generalization in rain/night conditions. |
| **Recall**          |       98.2%        |       98.1%       |   -0.1%   | Stable. The model still detects almost every visible sign.                                                                                                 |
| **Inference Speed** |       0.7 ms       |      3.4 ms       |  +2.7 ms  | While slower, ~290 FPS on RTX 4090 is still well above real-time requirements.                                                                             |

**Conclusion:**
Switching to the **Medium** model with aggressive augmentation successfully solved the "detection flickering" issue on video footage. The increase in Precision to 99.1% ensures a much more reliable system in real-world driving scenarios.

### 🏆 Model Training Comparison: YOLOv8m vs YOLOv8l

To ensure optimal performance, we conducted a comparative analysis between the **Medium** and **Large** YOLOv8 architectures. Despite the theoretical advantage of the Large model (more parameters), our empirical tests on real-world video data and validation metrics demonstrated that **YOLOv8m is superior** for this specific use case.

| Feature / Metric               | YOLOv8m (Medium) | YOLOv8l (Large) |   Winner   | Analysis                                                                                                 |
|:-------------------------------|:----------------:|:---------------:|:----------:|:---------------------------------------------------------------------------------------------------------|
| **Parameters**                 |      25.9 M      |     43.7 M      | **Medium** | The smaller model generalizes better on our ~6k dataset, showing less tendency to overfit[cite: 4, 5].   |
| **mAP@50-95** (Accuracy)       |    **84.4%**     |      83.4%      | **Medium** | Model M provides more precise bounding box localization[cite: 4, 5].                                     |
| **Precision** (Confidence)     |    **99.1%**     |      98.8%      | **Medium** | Fewer False Positives observed with the Medium model[cite: 4, 5].                                        |
| **Inference Speed** (RTX 4090) |   **~3.4 ms**    |     ~5.4 ms     | **Medium** | Model M is approx. **37% faster**, leaving more resources for the video processing pipeline[cite: 4, 5]. |
| **Weight Decay**               |      0.0005      |     0.0005      |     -      | Identical regularization settings used[cite: 4, 5].                                                      |
| **Training Outcome**           | Best Epoch: 176  | Best Epoch: 166 |     -      | Both models converged similarly, but M maintained better stability[cite: 4, 5].                          |

**Conclusion:**
We selected **YOLOv8m** as the production model. It offers a superior balance between speed and precision. Its higher **mAP@50-95** score ensures more stable detections on video footage (e.g., dashcam recordings), eliminating the bounding box flickering often observed in over-parameterized models.

### 📈 Data Augmentation Pipeline

To bridge the "reality gap" between static training images and dynamic video footage, we implemented an aggressive online augmentation strategy. The following transformations are applied dynamically during training (Hyperparameters for YOLOv8m):

| Category           | Method             |    Value     | Purpose                                                                          |
|:-------------------|:-------------------|:------------:|:---------------------------------------------------------------------------------|
| **Photometric**    | **HSV Saturation** |    `0.8`     | Simulates high-contrast sunny days and dull rainy weather.                       |
|                    | **HSV Value**      |    `0.5`     | Simulates driving in shadows, tunnels, or bright sunlight (brightness variance). |
|                    | **HSV Hue**        |   `0.025`    | Minor color shifts to account for different camera sensors.                      |
| **Geometric**      | **Rotation**       |    `±15°`    | Handles tilted signs or banking vehicles.                                        |
|                    | **Translation**    |    `±20%`    | Ensures the model detects signs that are not centered.                           |
|                    | **Scale**          |    `±70%`    | Critical for detecting signs at varying distances (highway vs city).             |
|                    | **Shear**          |    `±5°`     | Simulates perspective distortion.                                                |
| **Regularization** | **Mosaic**         |    `1.0`     | Stitches 4 images into one; forces the model to learn context and small objects. |
|                    | **MixUp**          |    `0.15`    | Blends two images (15% probability) to smooth decision boundaries.               |
|                    | **Copy-Paste**     |    `0.1`     | Randomly pastes sign instances onto other images to increase object density.     |
|                    | **Flip**           | `Horizontal` | Mirrors images (left/right) to double dataset diversity.                         |

> **Note:** These aggressive settings (especially MixUp and high Scale variance) were key to achieving stable detection on unseen video data.

## 🚀 High-Performance Video Pipeline (RTX 4090 Optimized)

To fully utilize the massive parallel computing power of the **NVIDIA RTX 4090**, we moved away from standard frame-by-frame processing. Instead, we implemented a **Threaded Batch Processing** architecture.

### How it works:
1.  **Producer-Consumer Pattern:** The system uses separate threads for reading video frames (I/O bound) and processing them (GPU bound).
2.  **Dynamic Batching:** Instead of sending a single image to the GPU, the detector accumulates a batch of frames (e.g., 4, 8, or 16) from the queue.
3.  **Parallel Inference:** This batch is sent to the GPU in a single call. The RTX 4090 processes all images in the batch simultaneously across its thousands of CUDA cores.

**Benefit:** Drastically reduces CPU-GPU communication overhead. While single-frame inference might take ~6ms per frame (due to overhead), batch processing can achieve **~3ms per frame** equivalent throughput, enabling high-FPS analysis even on high-resolution footage.

## 🚀 Quick Start

### Clone repository
`git clone https://github.com/TrafficSignSpeedLimitRecog/SpeedLimitRecog.git`

`cd SpeedLimitRecog`

### Create virtual environment
`python -m venv .venv`

`.venv\Scripts\activate`  # Windows

### Install dependencies
`pip install -r requirements.txt`

- Python 3.12
- PyTorch 2.5
- CUDA 12.1

### Download Dataset

Visit [Roboflow](https://universe.roboflow.com/speedlimitrecog-qazyk/speedlimitrecog-xgxlz/dataset/3) and download **YOLO v8 PyTorch** format.

Extract to `datasets/yolo_detection/`

### Train Model
`python src/simple_trainer.py`

Training time: ~1.5-2h (RTX 4090, 300 epochs)

### Run GUI
`python src/main.py --gui`

## 📁 Project Structure

```
SpeedLimitRecog/
├── src/
│   ├── main.py              # Entry point
│   ├── simple_trainer.py    # Training script
│   ├── core/
│   │   ├── detector.py      # YOLO detector
│   │   └── video_processor.py
│   └── gui/
│       ├── main_window.py   # Main GUI
│       ├── components.py    # UI components
│       └── styles.py        # Dark theme
├── datasets/
│   ├── yolo_detection/      # Training dataset
│   ├── test_images/         # Test images
│   └── test_videos/         # Test videos
├── models/
│   └── speed_limit_recog/
│       └── weights/
│           └── best.pt      # Trained model
├── config/
│   └── settings.yaml        # Configuration
└── requirements.txt
```

## ⚙️ Configuration

Edit `config/settings.yaml`:

```
model:
  confidence_threshold: 0.5
  iou_threshold: 0.45

processing:
  fps_target: 60
  use_gpu: true
```

## 🎨 Features

**Image Detection:**
- Load folder of images
- Navigate with A/D or arrows
- Detect with Space
- Adjustable confidence slider

**Video Processing:**
- Drag & drop video
- Process with detection overlay
- Real-time playback
- Progress tracking

## 📝 Commands

### Train model
`python src/simple_trainer.py`

### Run GUI
`python src/main.py --gui`

### Validate model
`python -c "from ultralytics import YOLO; m = YOLO('models/speed_limit_recog/weights/best.pt'); m.val(data='datasets/yolo_detection/data.yaml')"`

### Validate dataset
In `SpeedLimitRecog\datasets\yolo_detection`:
```
Get-ChildItem -Directory | ForEach-Object {
    $split = $_.Name
    $img_count = (Get-ChildItem "$split\images" -File).Count
    $lbl_count = (Get-ChildItem "$split\labels" -File).Count
    $match = if ($img_count -eq $lbl_count) {"✓"} else {"✗ MISMATCH!"}
    
    Write-Host "$split : Images=$img_count | Labels=$lbl_count | $match"
}
```
OUTPUT:
```
test : Images=562 | Labels=562 | ✓
train : Images=4656 | Labels=4656 | ✓
valid : Images=1086 | Labels=1086 | ✓
```

### Validate class split
```
python -c "
import yaml
from pathlib import Path
from collections import Counter

splits = ['train', 'valid', 'test']
base = Path('.')

for split in splits:
    labels_dir = base / split / 'labels'
    class_counts = Counter()
    
    for label_file in labels_dir.glob('*.txt'):
        with open(label_file, 'r') as f:
            for line in f:
                cls = int(line.split()[0])
                class_counts[cls] += 1
    
    print(f'\n{split.upper()}:')
    for cls in sorted(class_counts.keys()):
        print(f'  Class {cls}: {class_counts[cls]}')
"
```
OUTPUT:
```
TRAIN:
  Class 0: 574
  Class 1: 616
  Class 2: 483
  Class 3: 586
  Class 4: 148
  Class 5: 644
  Class 6: 442
  Class 7: 515
  Class 8: 608
  Class 9: 3
  Class 10: 125

VALID:
  Class 0: 120
  Class 1: 147
  Class 2: 123
  Class 3: 147
  Class 4: 38
  Class 5: 153
  Class 6: 92
  Class 7: 103
  Class 8: 135
  Class 10: 35

TEST:
  Class 0: 64
  Class 1: 77
  Class 2: 61
  Class 3: 80
  Class 4: 28
  Class 5: 72
  Class 6: 48
  Class 7: 50
  Class 8: 68
  Class 10: 21
```

## 🔧 Troubleshooting

**CUDA Out of Memory:**

In `simple_trainer.py`, reduce batch size:
```
batch=8  # instead of 16
```

**Model Not Found:**

Download dataset and train first:
`python src/simple_trainer.py`


## 📄 License

MIT License

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Roboflow](https://roboflow.com/)

---
