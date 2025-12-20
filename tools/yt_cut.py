import json
import random
import subprocess
import time
from pathlib import Path

def parse_ts(ts: str) -> int:
    parts = ts.strip().split(":")
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    raise ValueError("Czas musi być w formacie mm:ss albo hh:mm:ss")

def fmt_ts(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def yt_dlp_supports_no_progress() -> bool:
    p = subprocess.run(["python", "-m", "yt_dlp", "--help"], capture_output=True, text=True)
    return "--no-progress" in (p.stdout or "")

def main():
    script_dir = Path(__file__).resolve().parent
    repo_dir = script_dir.parent
    trp_dir = repo_dir.parent
    ffmpeg_exe = trp_dir / "ffmpeg.exe"
    out_dir = repo_dir / "datasets" / "test_videos" / "input"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not ffmpeg_exe.exists():
        print(f"Brak ffmpeg.exe w: {ffmpeg_exe}")
        return

    url = input("URL: ").strip()
    start = input("Start (mm:ss lub hh:mm:ss): ").strip()
    end = input("End   (mm:ss lub hh:mm:ss): ").strip()
    if not url or not start or not end:
        print("Brakuje URL/start/end.")
        return

    start_s = parse_ts(start)
    end_s = parse_ts(end)
    if end_s <= start_s:
        print("End musi być > Start.")
        return

    meta = subprocess.run(["python", "-m", "yt_dlp", "-j", url], capture_output=True, text=True)
    if meta.returncode != 0:
        err = (meta.stderr or "").strip()
        print(err if err else "Nie udało się pobrać metadanych.")
        return

    info = json.loads(meta.stdout.splitlines()[-1])
    formats = info.get("formats") or []

    best_by_height = {}
    for f in formats:
        if f.get("vcodec") in (None, "none"):
            continue
        if f.get("ext") != "mp4":
            continue
        vcodec = (f.get("vcodec") or "").lower()
        if "avc1" not in vcodec:
            continue
        height = f.get("height")
        if not height:
            continue
        tbr = f.get("tbr") or 0
        cur = best_by_height.get(height)
        if cur is None or (cur.get("tbr") or 0) < tbr:
            best_by_height[height] = f

    if not best_by_height:
        print("Nie znaleziono MP4/H.264 (avc1).")
        return

    choices = sorted(best_by_height.items(), key=lambda x: x[0], reverse=True)

    print("\nDostępne rozdzielczości (MP4/H.264):")
    for i, (h, f) in enumerate(choices, 1):
        fps = f.get("fps") or "?"
        note = f.get("format_note") or ""
        print(f"{i}. {h}p, {fps}fps {note}".strip())

    sel = input("\nWybierz numer (Enter = najwyższa): ").strip()
    idx = 1 if sel == "" else int(sel) if sel.isdigit() else None
    if idx is None or not (1 <= idx <= len(choices)):
        print("Zły wybór.")
        return

    height, fmt = choices[idx - 1]
    vid = fmt["format_id"]

    clip_id = f"{int(time.time())}{random.randint(100,999)}"
    outtmpl = str(out_dir / f"wycinek{clip_id}_{height}p.%(ext)s")

    cmd = [
        "python", "-m", "yt_dlp",
        "--ffmpeg-location", str(ffmpeg_exe),
        "--download-sections", f"*{fmt_ts(start_s)}-{fmt_ts(end_s)}",
        "-f", f"{vid}+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", outtmpl,
        "-q",
        "--no-warnings",
        url,
    ]
    if yt_dlp_supports_no_progress():
        cmd.insert(-1, "--no-progress")

    print(f"\nPobieranie: {fmt_ts(start_s)}-{fmt_ts(end_s)} w {height}p -> {out_dir}")
    r = subprocess.run(cmd, check=False)
    if r.returncode == 0:
        print("Gotowe.")
    else:
        print(f"Niepowodzenie (kod={r.returncode}).")

if __name__ == "__main__":
    main()
