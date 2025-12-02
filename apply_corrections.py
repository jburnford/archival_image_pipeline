#!/usr/bin/env python3
"""
Apply rotation corrections from the manual review.
Reads rotation_corrections.json and applies rotations to images.
"""
import cv2
import json
import shutil
from pathlib import Path
import argparse


def rotate_image(image, angle):
    """Rotate image by specified angle (90, 180, 270)."""
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image


def main():
    parser = argparse.ArgumentParser(description='Apply rotation corrections')
    parser.add_argument('--corrections', '-c', default='rotation_corrections.json',
                        help='JSON file with corrections')
    parser.add_argument('--input', '-i', default='.', help='Input directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--copy-unchanged', action='store_true',
                        help='Also copy images that need no rotation')
    args = parser.parse_args()

    # Load corrections
    corrections_file = Path(args.corrections)
    if not corrections_file.exists():
        print(f"Error: Corrections file not found: {corrections_file}")
        return

    with open(corrections_file) as f:
        corrections = json.load(f)

    print(f"Loaded {len(corrections)} corrections")

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all images
    images = sorted(
        list(input_dir.glob('*.JPEG')) +
        list(input_dir.glob('*.jpeg')) +
        list(input_dir.glob('*.jpg')) +
        list(input_dir.glob('*.png'))
    )

    stats = {'rotated': 0, 'copied': 0, 'skipped': 0, 'errors': 0}

    for i, img_path in enumerate(images):
        filename = img_path.name
        out_path = output_dir / filename

        if filename in corrections:
            # Apply rotation
            angle = corrections[filename]
            try:
                img = cv2.imread(str(img_path))
                if img is None:
                    print(f"[{i+1}/{len(images)}] {filename}: ERROR - could not read")
                    stats['errors'] += 1
                    continue

                rotated = rotate_image(img, angle)
                cv2.imwrite(str(out_path), rotated)
                print(f"[{i+1}/{len(images)}] {filename}: rotated {angle}°")
                stats['rotated'] += 1

            except Exception as e:
                print(f"[{i+1}/{len(images)}] {filename}: ERROR - {e}")
                stats['errors'] += 1

        elif args.copy_unchanged:
            # Copy unchanged
            shutil.copy2(img_path, out_path)
            stats['copied'] += 1

        else:
            stats['skipped'] += 1

        if (i + 1) % 100 == 0:
            print(f"--- Progress: {i+1}/{len(images)} ---")

    print(f"\n{'='*50}")
    print(f"COMPLETE!")
    print(f"Rotated: {stats['rotated']}")
    print(f"Copied unchanged: {stats['copied']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
