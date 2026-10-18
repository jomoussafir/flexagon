"""Copy the shared brand assets, or verify the platform copies with --check."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "logo.png": [
        "ios/Flexagon/Assets.xcassets/AppIcon.appiconset/AppIcon.png",
        "ios/Flexagon/Assets.xcassets/BrandIcon.imageset/BrandIcon.png",
        "wordpress/themes/flexagon/assets/logo.png",
    ],
    "logo.svg": ["wordpress/themes/flexagon/assets/logo.svg"],
    "favicon.png": ["wordpress/themes/flexagon/assets/favicon.png"],
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failures = []
    for name, destinations in TARGETS.items():
        source = ROOT / "shared/branding" / name
        for destination in destinations:
            target = ROOT / destination
            if args.check:
                if not target.is_file() or target.read_bytes() != source.read_bytes():
                    failures.append(destination)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    if failures:
        raise SystemExit("Brand assets differ: " + ", ".join(failures))
    print("Brand assets match." if args.check else "Brand assets synchronised.")

if __name__ == "__main__":
    main()
