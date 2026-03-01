"""DoodleBob Desktop Pet - Entry point.

Usage:
    python main.py              # Full-screen overlay mode (Windows)
    python main.py --windowed   # Windowed mode (for testing / development)
    python main.py --generate   # Only generate placeholder sprites, then exit
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
    args = parser.parse_args()

    if args.generate:
        from sprite_gen import ensure_sprites_exist
        ensure_sprites_exist()
        print("Placeholder sprites generated in assets/sprites/")
        return

    from app import DoodleBobApp
    app = DoodleBobApp(windowed=args.windowed)
    app.run()


if __name__ == "__main__":
    main()
