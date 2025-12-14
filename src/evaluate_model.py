from pathlib import Path
from ultralytics import YOLO
import cv2
import json


def load_ground_truth_labels(json_path):
    if not Path(json_path).exists():
        return {}

    with open(json_path, 'r', encoding='utf-8') as f:
        labels = json.load(f)

    normalized_labels = {}
    for filename, label in labels.items():
        if label is None:
            continue

        if isinstance(label, list):
            filtered_labels = [l for l in label if l is not None]
            if filtered_labels:
                normalized_labels[filename] = filtered_labels
        else:
            normalized_labels[filename] = [label]

    return normalized_labels


def test_on_unseen_images(model_path, test_dir, confidence=0.5, iou=0.45, ground_truth_labels=None):
    model = YOLO(model_path)
    test_images = list(Path(test_dir).glob("*.jpg")) + list(Path(test_dir).glob("*.png")) + list(
        Path(test_dir).glob("*.jpeg"))

    if not test_images:
        print(f"WARNING: No images found in {test_dir}")
        return None

    detected = 0
    total_detections = 0
    correct_predictions = 0
    images_with_ground_truth = 0
    partially_correct = 0

    class_names = ['20', '30', '40', '50', '60', '70', '80', '100', '120', 'speed-sign-end']

    detailed_results = []

    for img_path in test_images:
        img = cv2.imread(str(img_path))

        if img is None:
            continue

        results = model(img, conf=confidence, iou=iou, verbose=False)[0]
        has_detection = len(results.boxes) > 0

        ground_truths = ground_truth_labels.get(img_path.name, []) if ground_truth_labels else []

        predicted_classes = []

        if has_detection:
            detected += 1
            total_detections += len(results.boxes)

            for box in results.boxes:
                cls_id = int(box.cls[0])
                predicted_class = class_names[cls_id]
                conf_score = float(box.conf[0])
                predicted_classes.append((predicted_class, conf_score))

        if ground_truths:
            images_with_ground_truth += 1

            predicted_set = set([p[0] for p in predicted_classes])
            gt_set = set(ground_truths)

            matches = predicted_set.intersection(gt_set)

            is_fully_correct = (len(matches) == len(gt_set) and len(predicted_set) == len(gt_set))
            is_partially_correct = len(matches) > 0

            if is_fully_correct:
                correct_predictions += 1
            elif is_partially_correct:
                partially_correct += 1

            detailed_results.append({
                'file': img_path.name,
                'ground_truth': ground_truths,
                'predicted': predicted_classes,
                'matches': list(matches),
                'missing': list(gt_set - predicted_set),
                'extra': list(predicted_set - gt_set),
                'fully_correct': is_fully_correct,
                'partially_correct': is_partially_correct
            })

    detection_rate = (detected / len(test_images)) * 100 if len(test_images) > 0 else 0
    full_accuracy = (correct_predictions / images_with_ground_truth * 100) if images_with_ground_truth > 0 else 0
    partial_accuracy = ((
                                correct_predictions + partially_correct) / images_with_ground_truth * 100) if images_with_ground_truth > 0 else 0

    return {
        'detection_rate': detection_rate,
        'full_accuracy': full_accuracy,
        'partial_accuracy': partial_accuracy,
        'detected': detected,
        'correct': correct_predictions,
        'partially_correct': partially_correct,
        'total': len(test_images),
        'with_gt': images_with_ground_truth,
        'total_detections': total_detections,
        'detailed': detailed_results
    }


def run_detailed_test(model_path, test_dir, confidence=0.5, iou=0.45, ground_truth_labels=None):
    print(f"DETAILED TEST - conf={confidence}, iou={iou}")

    result = test_on_unseen_images(model_path, test_dir, confidence=confidence, iou=iou,
                                   ground_truth_labels=ground_truth_labels)

    if not result:
        return

    print(f"Total images: {result['total']}")
    print(f"Images with detections: {result['detected']}")
    print(f"Total detections: {result['total_detections']}")
    print(f"Detection rate: {result['detection_rate']:.1f}%")
    print(f"\nImages with ground truth: {result['with_gt']}")
    print(f"Fully correct predictions: {result['correct']}")
    print(f"Partially correct predictions: {result['partially_correct']}")
    print(f"Full accuracy rate: {result['full_accuracy']:.1f}%")
    print(f"Partial accuracy rate: {result['partial_accuracy']:.1f}%")

    if result['detailed']:
        print(f"DETAILED RESULTS:")
        print(f"{'Filename':<40} | {'Ground Truth':<15} | {'Predicted':<20} | {'Status':<10}")

        for detail in result['detailed']:
            if detail['fully_correct']:
                status = "FULL"
            elif detail['partially_correct']:
                status = "PARTIAL"
            else:
                status = "WRONG"

            gt_str = ','.join(detail['ground_truth'])
            pred_str = ','.join([f"{p[0]}({p[1]:.2f})" for p in detail['predicted']]) if detail['predicted'] else 'NONE'
            pred_str = pred_str[:20]

            print(f"{detail['file'][:40]:<40} | {gt_str:<15} | {pred_str:<20} | {status:<10}")

            if detail['missing']:
                print(f"{'':>40} | Missing: {','.join(detail['missing'])}")
            if detail['extra']:
                print(f"{'':>40} | Extra: {','.join(detail['extra'])}")


if __name__ == "__main__":
    model_path = "models/speed_limit_recog/weights/best.pt"
    test_dir = "datasets/test_images"
    labels_path = "datasets/test_images_labels.json"

    if not Path(test_dir).exists():
        print(f"ERROR: Directory not found: {test_dir}")
        exit(1)

    ground_truth_labels = load_ground_truth_labels(labels_path)

    if not ground_truth_labels:
        print(f"WARNING: No ground truth labels found at {labels_path}")
        print(f"Please create {labels_path} with manual labels")
        print(f"Format: {{'image.jpg': ['50', '60'], 'image2.jpg': ['30'], ...}}\n")
    else:
        print(f"Loaded {len(ground_truth_labels)} ground truth labels from {labels_path}\n")

    run_detailed_test(model_path, test_dir, confidence=0.5, iou=0.45, ground_truth_labels=ground_truth_labels)
