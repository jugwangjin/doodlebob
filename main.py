"""DoodleBob Desktop Pet - Entry point.

Usage:
    python main.py              # Full-screen overlay mode (Windows)
    python main.py --windowed   # Windowed mode (for testing / development)
    python main.py --generate   # Only generate placeholder sprites, then exit
    python main.py --sheet      # Generate sprite sheet from current sprites
    python main.py --split-sheet PATH  # Split a sprite sheet into individual PNGs
"""

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    parser = argparse.ArgumentParser(description="DoodleBob Desktop Pet")
    parser.add_argument(
        "--windowed", action="store_true",
        help="Run in a window instead of full-screen overlay (for testing)",
    )
    parser.add_argument(
        "--generate", action="store_true",
        help="Generate placeholder sprites and exit",
    )
    parser.add_argument(
        "--regenerate", action="store_true",
        help="Force regenerate all sprites (overwrites existing) and exit",
    )
    parser.add_argument(
        "--sheet", action="store_true",
        help="Generate a sprite sheet from current sprites and exit",
    )
    parser.add_argument(
        "--sheet-scale", type=int, default=2,
        help="Scale factor for sprite sheet (default: 2)",
    )
    parser.add_argument(
        "--split-sheet", type=str, default=None, metavar="PATH",
        help="Split a sprite sheet into individual sprite PNGs and exit",
    )
    parser.add_argument(
        "--sheet-cols", type=int, default=None,
        help="Actual columns in the sheet image (e.g. 6 for 9×6 grid). Default: 4",
    )
    parser.add_argument(
        "--skip-cols", type=str, default=None, metavar="LIST",
        help="Comma-separated 0-based column indices to skip. If sprite 1 and 3 are transparent, try 1,4 instead of 2,5.",
    )
    parser.add_argument(
        "--green", action="store_true",
        help="Same as default: remove background (detected from sheet corners). Kept for compatibility.",
    )
    parser.add_argument(
        "--bg", type=str, default=None, metavar="R,G,B",
        help="Use this RGB as background to remove (e.g. 0,255,0 or 192,192,192). Default: auto-detect from corners.",
    )
    parser.add_argument(
        "--chroma-tolerance", type=int, default=40,
        help="Chroma key tolerance 0..255 (default 40). Larger = more pixels removed as background.",
    )
    args = parser.parse_args()

    if args.generate or args.regenerate:
        from sprite_gen import ensure_sprites_exist
        ensure_sprites_exist(force=args.regenerate)
        print("Placeholder sprites generated in assets/sprites/")
        return

    if args.sheet:
        from sprite_gen import ensure_sprites_exist, create_sprite_sheet
        from config import SPRITE_SHEET_LAYOUT
        ensure_sprites_exist()
        path = create_sprite_sheet(scale=args.sheet_scale)
        print(f"Sprite sheet saved to: {path}")
        print(f"\nSprite sheet layout ({len(SPRITE_SHEET_LAYOUT)} rows × 4 cols):")
        print("-" * 55)
        for i, (name, frames) in enumerate(SPRITE_SHEET_LAYOUT):
            print(f"  Row {i}: {name:<14} ({frames} frames)")
        print("-" * 55)
        print("\nRow descriptions:")
        descriptions = {
            "walk": "Normal walking, neutral expression",
            "chase": "Angry chasing toward cursor",
            "erase": "Erasing cursor with pencil eraser",
            "approach": "Approaching window to close (angry)",
            "idle": "Standing still, bobbing",
            "draw": "Drawing/redrawing cursor",
            "pencil_press": "Jabbing pencil to press close button",
            "lurk": "Lurking with glowing eyes (pre-chase)",
        }
        for i, (name, _) in enumerate(SPRITE_SHEET_LAYOUT):
            desc = descriptions.get(name, "")
            print(f"  Row {i} ({name}): {desc}")
        return

    if args.split_sheet:
        from sprite_gen import split_sprite_sheet
        skip_cols = None
        if args.skip_cols is not None:
            skip_cols = tuple(int(s.strip()) for s in args.skip_cols.split(","))
        bg_rgb = None
        if args.bg is not None:
            bg_rgb = tuple(int(s.strip()) for s in args.bg.split(","))
        split_sprite_sheet(
            args.split_sheet,
            sheet_cols=args.sheet_cols,
            skip_columns=skip_cols,
            background_rgb=bg_rgb,
            chroma_tolerance=args.chroma_tolerance,
        )
        print("Sprite sheet split into individual PNGs in assets/sprites/")
        return

    from app import DoodleBobApp
    app = DoodleBobApp(windowed=args.windowed)
    app.run()


if __name__ == "__main__":
    main()
