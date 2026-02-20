from __future__ import annotations

import argparse

from app.pipeline import generate_pptx_for_topic


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a PPTX from a topic")
    parser.add_argument("topic", help="Topic for the deck")
    parser.add_argument("--slides", type=int, default=None,
                        help="Number of slides")
    parser.add_argument("--theme", type=str, default=None,
                        help="Theme preset name (e.g., 'Education Light', 'Dark Tech')")
    args = parser.parse_args()

    path = generate_pptx_for_topic(
        topic=args.topic,
        slide_count=args.slides,
        theme_name=args.theme,
    )
    print(path)


if __name__ == "__main__":
    main()
