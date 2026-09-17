"""
Food-11 data preparation script.

Reads raw images from ./data/food11_raw/{training,evaluation,validation}
(filenames like "3_105.jpg" where the leading number is the category index)
and produces two processed copies:

  - ./data/food11_processed        : all images, resized to 128x128,
                                      sorted into per-category subfolders
  - ./data/food11_processed_mini   : same structure, capped at 100 images
                                      per category per split (for dev/testing)

Run with:
    uv run python ./src/food11/data.py
"""

from pathlib import Path
from PIL import Image

# Category index -> category name, per the lab spec
CATEGORIES = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

SPLITS = ["training", "evaluation", "validation"]
TARGET_SIZE = (128, 128)
MINI_LIMIT_PER_CATEGORY = 100

# Paths are relative to the repo root (where you run `uv run python ...` from)
RAW_ROOT = Path("data/food11_raw")
PROCESSED_ROOT = Path("data/food11_processed")
MINI_ROOT = Path("data/food11_processed_mini")


def category_from_filename(filename: str) -> int | None:
    """Extract the category index from a filename like '3_105.jpg'."""
    prefix = filename.split("_", 1)[0]
    try:
        idx = int(prefix)
    except ValueError:
        return None
    return idx if idx in CATEGORIES else None


def ensure_dirs(root: Path, split: str) -> None:
    for category_name in CATEGORIES.values():
        (root / split / category_name).mkdir(parents=True, exist_ok=True)


def process_split(split: str) -> None:
    split_dir = RAW_ROOT / split
    if not split_dir.exists():
        print(f"  [skip] {split_dir} does not exist")
        return

    ensure_dirs(PROCESSED_ROOT, split)
    ensure_dirs(MINI_ROOT, split)

    mini_counts = {idx: 0 for idx in CATEGORIES}

    image_files = sorted(
        p for p in split_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    total = len(image_files)
    print(f"  {split}: {total} raw images found")

    for i, img_path in enumerate(image_files, start=1):
        cat_idx = category_from_filename(img_path.name)
        if cat_idx is None:
            continue
        cat_name = CATEGORIES[cat_idx]

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                resized = img.resize(TARGET_SIZE, Image.LANCZOS)

                # Full processed dataset
                out_path = PROCESSED_ROOT / split / cat_name / img_path.name
                resized.save(out_path)

                # Mini dataset, capped per category
                if mini_counts[cat_idx] < MINI_LIMIT_PER_CATEGORY:
                    mini_path = MINI_ROOT / split / cat_name / img_path.name
                    resized.save(mini_path)
                    mini_counts[cat_idx] += 1
        except Exception as e:
            print(f"    [error] {img_path.name}: {e}")

        if i % 1000 == 0 or i == total:
            print(f"    processed {i}/{total}")

    print(f"  {split} mini counts: {mini_counts}")


def main() -> None:
    print("Building food11_processed and food11_processed_mini...")
    for split in SPLITS:
        print(f"Processing split: {split}")
        process_split(split)
    print("Done.")


if __name__ == "__main__":
    main()
