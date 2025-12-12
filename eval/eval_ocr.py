# ocr_benchmark.py
from __future__ import annotations

import argparse
import json
import os
import time
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

import psutil
from jiwer import cer


IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


@dataclass
class EngineResult:
    engine: str
    n_images: int
    char_accuracy_pct: float
    avg_time_ms: float
    peak_rss_mb: float
    errors: int


def load_pairs(images_dir: Path, gt_dir: Path) -> List[Tuple[Path, Path]]:
    pairs: List[Tuple[Path, Path]] = []
    for img in sorted(images_dir.iterdir()):
        if img.suffix.lower() not in IMG_EXTS:
            continue
        gt = gt_dir / (img.stem + ".txt")
        if gt.exists():
            pairs.append((img, gt))
    return pairs


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore").strip()


def normalize_text(s: str) -> str:
    # light normalization; keep it simple and consistent across engines
    return " ".join(s.replace("\n", " ").split()).strip()


# -----------------------------
# OCR backends
# -----------------------------
def run_tesseract(image_path: str) -> str:
    import pytesseract
    from PIL import Image
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def run_easyocr(image_path: str) -> str:
    import easyocr
    # Create reader once per process; CPU by default
    reader = easyocr.Reader(["en"], gpu=False)
    # detail=0 returns list of strings
    out = reader.readtext(image_path, detail=0)
    return "\n".join(out)

def run_paddleocr(image_path: str) -> str:
    from paddleocr import PaddleOCR
    # Create once per process; enable angle classifier for prescriptions
    ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    res = ocr.ocr(image_path, cls=True)
    # res: list of lines; each line: [box, (text, conf)]
    texts = []
    for page in res:
        for line in page:
            texts.append(line[1][0])
    return "\n".join(texts)


ENGINE_FUNCS = {
    "tesseract": run_tesseract,
    "easyocr": run_easyocr,
    "paddleocr": run_paddleocr,
}


# -----------------------------
# Worker executed in-process (but called in subprocess wrapper)
# -----------------------------
def benchmark_engine(engine: str, pairs: List[Tuple[str, str]]) -> Dict:
    proc = psutil.Process(os.getpid())
    peak_rss = proc.memory_info().rss

    total_cer = 0.0
    total_time = 0.0
    n = 0
    errors = 0

    fn = ENGINE_FUNCS[engine]

    for img_path, gt_path in pairs:
        gt = normalize_text(read_text(Path(gt_path)))
        t0 = time.perf_counter()
        try:
            pred = fn(img_path)
            pred = normalize_text(pred)
        except Exception:
            errors += 1
            pred = ""
        dt = (time.perf_counter() - t0)
        total_time += dt

        total_cer += cer(gt, pred)
        n += 1

        rss = proc.memory_info().rss
        if rss > peak_rss:
            peak_rss = rss

    avg_cer = (total_cer / n) if n else 1.0
    char_acc = max(0.0, 1.0 - avg_cer) * 100.0
    avg_time_ms = (total_time / n) * 1000.0 if n else 0.0
    peak_rss_mb = peak_rss / (1024 * 1024)

    return {
        "engine": engine,
        "n_images": n,
        "char_accuracy_pct": round(char_acc, 2),
        "avg_time_ms": round(avg_time_ms, 1),
        "peak_rss_mb": round(peak_rss_mb, 1),
        "errors": errors,
    }


# -----------------------------
# Subprocess wrapper for clean RAM measurement
# -----------------------------
def run_in_subprocess(engine: str, pairs: List[Tuple[str, str]]) -> Dict:
    import multiprocessing as mp

    def _worker(q):
        try:
            q.put({"ok": True, "data": benchmark_engine(engine, pairs)})
        except Exception as e:
            q.put({"ok": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()})

    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_worker, args=(q,))
    p.start()
    out = q.get()
    p.join()

    if not out.get("ok"):
        return {
            "engine": engine,
            "n_images": 0,
            "char_accuracy_pct": 0.0,
            "avg_time_ms": 0.0,
            "peak_rss_mb": 0.0,
            "errors": 1,
            "error": out.get("error"),
        }
    return out["data"]



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True, help="Path containing images/ and gt/ folders")
    ap.add_argument("--out_json", default="ocr_benchmark_results.json")
    args = ap.parse_args()

    dataset = Path(args.dataset_dir)
    images_dir = dataset / "images"
    gt_dir = dataset / "gt"

    pairs = load_pairs(images_dir, gt_dir)
    if not pairs:
        raise SystemExit("No (image, gt) pairs found. Expected dataset/images and dataset/gt with matching names.")

    pairs_str = [(str(i), str(g)) for i, g in pairs]

    results = []
    for engine in ["paddleocr", "easyocr", "tesseract"]:
        res = run_in_subprocess(engine, pairs_str)
        results.append(res)

    summary = {
        "dataset_dir": str(dataset),
        "n_images": len(pairs),
        "results": results,
        "latex_table_rows": latex_table(results),
    }

    Path(args.out_json).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== OCR BENCHMARK COMPLETE ===")
    print(json.dumps(summary, indent=2))



if __name__ == "__main__":
    main()
