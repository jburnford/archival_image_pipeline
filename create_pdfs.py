#!/usr/bin/env python3
"""
Create PDFs from images using review data (sections, discards, rotations).
"""
import os
import json
from pathlib import Path
from PIL import Image
import argparse


def get_image_files(input_dir):
    """Get sorted list of image files."""
    extensions = {'.jpeg', '.jpg', '.png', '.JPEG', '.JPG', '.PNG'}
    files = []
    for f in Path(input_dir).iterdir():
        if f.suffix in extensions:
            files.append(f)
    return sorted(files, key=lambda x: x.name)


def rotate_image(img, degrees):
    """Rotate PIL image by degrees (90, 180, 270)."""
    if degrees == 90:
        return img.transpose(Image.Transpose.ROTATE_90)
    elif degrees == 180:
        return img.transpose(Image.Transpose.ROTATE_180)
    elif degrees == 270:
        return img.transpose(Image.Transpose.ROTATE_270)
    return img


def create_pdf(image_data, output_path, quality=85):
    """Create a PDF from a list of (path, rotation) tuples."""
    if not image_data:
        return 0

    images = []
    first_image = None

    for img_path, rotation in image_data:
        try:
            img = Image.open(img_path)

            # FIX: For MPO files (iPhone), ensure we only get the first frame
            # and strip multi-frame data by converting to RGB immediately
            img.seek(0)
            img = img.convert('RGB')

            # Apply rotation if needed
            if rotation:
                img = rotate_image(img, rotation)

            if first_image is None:
                first_image = img
            else:
                images.append(img)

        except Exception as e:
            print(f"  Warning: Could not load {img_path.name}: {e}")

    if first_image:
        first_image.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=images,
            quality=quality,
            optimize=True
        )

        # Close images
        first_image.close()
        for img in images:
            img.close()

        return len(images) + 1
    return 0


def main():
    parser = argparse.ArgumentParser(description='Create PDFs from reviewed images')
    parser.add_argument('--review', '-r', default='image_review.json',
                        help='Review JSON file with corrections/sections/discards')
    parser.add_argument('--input', '-i', default='final_preprocessed',
                        help='Input directory with images')
    parser.add_argument('--output', '-o', default='pdfs',
                        help='Output directory for PDFs')
    parser.add_argument('--prefix', '-p', default='banks_archive',
                        help='PDF filename prefix')
    parser.add_argument('--quality', '-q', type=int, default=85,
                        help='JPEG quality for PDF (default: 85)')
    parser.add_argument('--max-size', '-m', type=int, default=200,
                        help='Max PDF size in MB (used if no sections defined)')
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load review data
    review_file = Path(args.review)
    corrections = {}
    section_breaks = set()
    discards = set()

    if review_file.exists():
        with open(review_file) as f:
            data = json.load(f)
            if isinstance(data, dict) and 'corrections' in data:
                corrections = data.get('corrections', {})
                section_breaks = set(data.get('sectionBreaks', []))
                discards = set(data.get('discards', []))
            else:
                # Old format - just corrections
                corrections = data
        print(f"Loaded review: {len(corrections)} rotations, {len(section_breaks)} sections, {len(discards)} discards")
    else:
        print(f"No review file found ({review_file}), using defaults")

    # Get all images
    all_images = get_image_files(input_dir)
    print(f"Found {len(all_images)} images in {input_dir}")

    # Filter out discards and prepare image data
    images = []
    for img_path in all_images:
        filename = img_path.name
        if filename not in discards:
            rotation = corrections.get(filename, 0)
            images.append((img_path, rotation))

    print(f"After removing discards: {len(images)} images")

    if not images:
        print("No images to process!")
        return

    # Split into sections
    if section_breaks:
        # Use manual section breaks
        sections = []
        current_section = []

        for img_path, rotation in images:
            if img_path.name in section_breaks and current_section:
                sections.append(current_section)
                current_section = []
            current_section.append((img_path, rotation))

        if current_section:
            sections.append(current_section)

        print(f"\nUsing {len(sections)} manual sections")
    else:
        # Auto-split by size
        max_bytes = args.max_size * 1024 * 1024
        sections = []
        current_section = []
        current_size = 0

        for img_path, rotation in images:
            img_size = img_path.stat().st_size * 0.85

            if current_size + img_size > max_bytes and current_section:
                sections.append(current_section)
                current_section = []
                current_size = 0

            current_section.append((img_path, rotation))
            current_size += img_size

        if current_section:
            sections.append(current_section)

        print(f"\nAuto-split into {len(sections)} sections (max {args.max_size}MB each)")

    # Show section info
    for i, section in enumerate(sections):
        print(f"  Part {i+1}: {len(section)} images ({section[0][0].name} - {section[-1][0].name})")

    # Create PDFs
    print("\nCreating PDFs...")
    for i, section in enumerate(sections):
        part_num = i + 1
        output_path = output_dir / f"{args.prefix}_part{part_num}.pdf"
        print(f"\n[{part_num}/{len(sections)}] Creating {output_path.name} ({len(section)} images)...")

        count = create_pdf(section, output_path, quality=args.quality)

        if output_path.exists():
            actual_size = output_path.stat().st_size / (1024 * 1024)
            print(f"  Created: {actual_size:.1f} MB ({count} pages)")

    print("\nDone!")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
