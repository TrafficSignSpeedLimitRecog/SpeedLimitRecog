# 🚦 Speed Limit Detection System

Speed limit sign detection using YOLOv8. Detects speed limit signs in images and videos.

![Python](https://img.shields.io/badge/python-3.12-blue) ![PyTorch](https://img.shields.io/badge/pytorch-2.5-red) ![YOLOv8](https://img.shields.io/badge/yolo-v8-orange)

---

## 🛠️ Tech Stack

- YOLOv8s (Ultralytics)
- PyTorch 2.5 + CUDA 12.1
- PySide6 (Qt6)
- OpenCV

## 📊 Dataset Stats

- **mAP@50:** 99.0%
- **mAP@50-95:** 85.3%
- **Speed:** 60 FPS (RTX 4090)
- **Classes:** 10 ['20', '30', '40', '50', '60', '70', '80', '100', '120', 'speed-sign-end']

## 🎯 Performance

- **Total:** 6,301 images
- **Train:** 4,653 (73.8%)
- **Valid:** 1,086 (17.2%)
- **Test:** 562 (8.9%)
- **Format:** YOLO v8 PyTorch

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
