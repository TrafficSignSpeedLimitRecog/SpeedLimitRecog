from pathlib import Path

LABEL_DIRS = [
    Path("datasets/yolo_detection/train/labels"),
    Path("datasets/yolo_detection/valid/labels"),
    Path("datasets/yolo_detection/test/labels"),
]

def to_float_list(parts):
    out = []
    for p in parts:
        out.append(float(p))
    return out

def clamp01(x):
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x

def convert_line(line):
    line = line.strip()
    if not line:
        return None

    parts = line.split()
    if len(parts) < 5:
        return None

    cls = parts[0]
    nums = to_float_list(parts[1:])

    if len(nums) == 4:
        xc, yc, w, h = nums
        xc, yc, w, h = clamp01(xc), clamp01(yc), clamp01(w), clamp01(h)
        return f"{cls} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"

    if len(nums) >= 6 and len(nums) % 2 == 0:
        xs = nums[0::2]
        ys = nums[1::2]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        xc = (minx + maxx) / 2.0
        yc = (miny + maxy) / 2.0
        w = maxx - minx
        h = maxy - miny
        xc, yc, w, h = clamp01(xc), clamp01(yc), clamp01(w), clamp01(h)
        return f"{cls} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"

    return None

def process_file(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out_lines = []
    for ln in lines:
        conv = convert_line(ln)
        if conv is not None:
            out_lines.append(conv)
    path.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")

def main():
    for d in LABEL_DIRS:
        if not d.exists():
            continue
        for p in d.glob("*.txt"):
            process_file(p)

if __name__ == "__main__":
    main()
