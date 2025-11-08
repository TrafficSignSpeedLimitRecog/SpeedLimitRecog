# Remapping Roboflow alphabetically class_id -> numerical class_id

from pathlib import Path
from tqdm import tqdm

# ROBOFLOW DATASET LABELS
REMAP = {
    0: 0,  # 'Speed Limit -10-'  → 10  (class_id=0)
    1: 9,  # 'Speed Limit -100-' → 100 (class_id=9)
    2: 10,  # 'Speed Limit -110-' → 110 (class_id=10)
    3: 11,  # 'Speed Limit -120-' → 120 (class_id=11)
    4: 1,  # 'Speed Limit -20-'  → 20  (class_id=1)
    5: 2,  # 'Speed Limit -30-'  → 30  (class_id=2)
    6: 3,  # 'Speed Limit -40-'  → 40  (class_id=3)
    7: 4,  # 'Speed Limit -50-'  → 50  (class_id=4)
    8: 5,  # 'Speed Limit -60-'  → 60  (class_id=5)
    9: 6,  # 'Speed Limit -70-'  → 70  (class_id=6)
    10: 7,  # 'Speed Limit -80-'  → 80  (class_id=7)
    11: 8,  # 'Speed Limit -90-'  → 90  (class_id=8)
}

dataset_dir = Path('.')
stats = {'total': 0, 'remapped': 0, 'unchanged': 0, 'skipped': 0}

print("=" * 60)
print("REMAPPING ROBOFLOW LABELS TO NUMERICAL")
print("=" * 60)

for split in ['train', 'valid', 'test']:
    lbl_dir = dataset_dir / split / 'labels'

    if not lbl_dir.exists():
        print(f"[!]  {split}/labels not found, skipping...")
        continue

    print(f"\nProcessing {split}...")

    label_files = list(lbl_dir.glob('*.txt'))

    for label_file in tqdm(label_files, desc=f"  {split}"):
        stats['total'] += 1

        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()

            new_lines = []
            file_remapped = False

            for line in lines:
                parts = line.strip().split()

                # Skip empty or invalid lines
                if len(parts) < 5:
                    stats['skipped'] += 1
                    continue

                old_class = int(parts[0])
                new_class = REMAP.get(old_class, old_class)

                if old_class != new_class:
                    file_remapped = True

                new_line = f"{new_class} {' '.join(parts[1:])}\n"
                new_lines.append(new_line)

            # Write back
            with open(label_file, 'w') as f:
                f.writelines(new_lines)

            if file_remapped:
                stats['remapped'] += 1
            else:
                stats['unchanged'] += 1

        except Exception as e:
            print(f"\n[X] Error processing {label_file.name}: {e}")
            stats['skipped'] += 1

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total files:      {stats['total']}")
print(f"Remapped:         {stats['remapped']}")
print(f"Unchanged:        {stats['unchanged']}")
print(f"Skipped/Errors:   {stats['skipped']}")
print("=" * 60)
print("    Remapping complete!")
