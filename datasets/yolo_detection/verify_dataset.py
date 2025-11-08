"""Short Verify dataset labels script."""

from pathlib import Path

class_names = {
    0: '10', 1: '20', 2: '30', 3: '40', 4: '50', 5: '60',
    6: '70', 7: '80', 8: '90', 9: '100', 10: '110', 11: '120'
}

dataset_dir = Path('.')

# Here to use specific images for testing
test_cases = [
    "test/images/50-1-_PNG.rf.a51282ff77f1ad68c336ee2109075e69.jpg",
    "test/images/60_PNG.rf.77a4983c20599fea31b1f579e513d9a9.jpg",
    "test/images/100-1-_PNG.rf.62736fe99f5d4b5cad4a835e7b30ea48.jpg"
]

print("=" * 60)
print("DATASET VERIFICATION")
print("=" * 60)

for img_rel_path in test_cases:
    img_path = dataset_dir / img_rel_path
    label_path = dataset_dir / img_rel_path.replace('images', 'labels').replace('.jpg', '.txt')

    if not label_path.exists():
        print(f"\n[X] Label not found: {label_path}")
        continue

    with open(label_path, 'r') as f:
        line = f.read().strip().split()
        class_id = int(line[0])
        class_name = class_names.get(class_id, f"UNKNOWN_{class_id}")

    filename = img_path.name
    if '50-1' in filename:
        expected = '50'
    elif '60_' in filename:
        expected = '60'
    elif '100-1' in filename:
        expected = '100'
    else:
        expected = "?"

    status = "~ OK" if class_name == expected else "[X] BŁĄD"

    print(f"\nFile: {filename}")
    print(f"  Expected: {expected} km/h")
    print(f"  Label:    class_id={class_id} → {class_name} km/h")
    print(f"  {status}")

print("\n" + "=" * 60)
