from __future__ import annotations
from app.images.unsplash import UnsplashImageSearch
from app.images.cache import ImageCache

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Allow running this script directly (python tools/fetch_unsplash.py ...) by
# adding the project root to sys.path so `import app...` works.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "Fetch a free-to-use image from Unsplash via API. "
            "Uses UNSPLASH_ACCESS_KEY only (do NOT store the secret key in code)."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", dest="photo_id",
                       help="Unsplash photo id (e.g. Dwu85P9SOIk)")
    group.add_argument(
        "--query", help="Search query (e.g. 'photosynthesis diagram')")

    parser.add_argument(
        "--size",
        default="regular",
        choices=["raw", "full", "regular", "small", "thumb"],
        help="Image size variant (default: regular)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output file path (default: output/unsplash_<id or query>.jpg)",
    )
    parser.add_argument(
        "--cache-dir",
        default=os.getenv("CACHE_DIR", "cache"),
        help="Cache directory (default: cache or CACHE_DIR env var)",
    )

    args = parser.parse_args()

    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise SystemExit(
            "UNSPLASH_ACCESS_KEY is not set. Add it to your .env file (Access Key only)."
        )

    cache = ImageCache(base_dir=args.cache_dir)
    client = UnsplashImageSearch(access_key=access_key, cache=cache)

    img_bytes: bytes | None = None
    label: str

    if args.photo_id:
        img_bytes = client.download_by_id(args.photo_id, size=args.size)
        label = args.photo_id
    else:
        url = client.search_image_url(args.query)
        if url:
            img_bytes = client.download(url)
        label = (args.query or "query").strip().replace(" ", "_")[:40]

    if not img_bytes:
        raise SystemExit(
            "No image returned (check id/query or your Unsplash quota/key).")

    out_path = args.out
    if not out_path:
        os.makedirs("output", exist_ok=True)
        out_path = str(Path("output") / f"unsplash_{label}.jpg")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(img_bytes)
    print(str(Path(out_path).resolve()))


if __name__ == "__main__":
    main()
