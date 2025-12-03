# Archival Image Pipeline

A workflow for processing archival photograph collections into organized, OCR-ready PDFs.

## Overview

This pipeline helps prepare historical document photographs for transcription by:
1. Reviewing images for rotation corrections
2. Marking section breaks (folder/document boundaries)
3. Flagging images to discard
4. Generating PDFs organized by archival sections

## Quick Start

### Option A: Direct Folder Selection (Recommended)

```bash
# 1. Open the HTML file directly in your browser
# (or start a local server: python3 -m http.server 8080)

# 2. Click "Select Image Folder" and choose your images directory

# 3. Review images, mark rotations/sections/discards

# 4. Export corrections (Ctrl+S or "Export File" button)

# 5. Generate PDFs
python3 create_pdfs.py -r image_review.json -i /path/to/your/images -o pdfs
```

### Option B: Server Mode (Legacy)

```bash
# 1. Generate image list
ls final_preprocessed/*.JPEG > image_list.txt

# 2. Start the review server
python3 -m http.server 8080

# 3. Open the review tool and click "Use Server Mode"
# http://localhost:8080/rotation_review.html

# 4-6. Same as above
```

## Workflow

### Step 1: Prepare Images

Place your source images in a directory (e.g., `final_preprocessed/`). Supported formats:
- JPEG (.jpeg, .jpg, .JPEG, .JPG)
- PNG (.png, .PNG)

Generate the image list:
```bash
ls final_preprocessed/*.JPEG | xargs -n1 basename > image_list.txt
```

### Step 2: Review Images

Open the review tool:
- **Direct method**: Open `rotation_review.html` in your browser and select your image folder
- **Server method**: Start `python3 -m http.server 8080` and open http://localhost:8080/rotation_review.html

The tool supports two modes:
1. **Folder Mode**: Select any local folder directly - no server needed
2. **Server Mode**: Uses `image_list.txt` and serves from `final_preprocessed/`

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Mark OK and advance to next |
| `1` | Rotate 90° clockwise |
| `2` | Rotate 180° |
| `3` | Rotate 270° (90° counter-clockwise) |
| `S` | Toggle section break (new PDF starts here) |
| `D` | Toggle discard (exclude from output) |
| `←` / `→` | Navigate previous/next |
| `Ctrl+S` | Export corrections file |

#### Features

- **Live rotation preview**: See how the image will look after rotation
- **Auto-save**: All changes saved to browser localStorage automatically
- **Session restore**: Prompts to restore previous session on page load
- **Filters**: Show only marked/unmarked images for focused review

### Step 3: Export Corrections

Click "Export File" or press `Ctrl+S` to download `image_review.json`.

The JSON format:
```json
{
  "corrections": {
    "IMG_1234.JPEG": 90,
    "IMG_1235.JPEG": 180
  },
  "sectionBreaks": [
    "IMG_1240.JPEG",
    "IMG_1280.JPEG"
  ],
  "discards": [
    "IMG_1250.JPEG"
  ]
}
```

### Step 4: Generate PDFs

```bash
python3 create_pdfs.py -r image_review.json -i final_preprocessed -o pdfs
```

Options:
- `-r, --review`: Path to review JSON file (default: `image_review.json`)
- `-i, --input`: Input directory with images (default: `final_preprocessed`)
- `-o, --output`: Output directory for PDFs (default: `pdfs`)
- `-p, --prefix`: PDF filename prefix (default: `banks_archive`)
- `-q, --quality`: JPEG quality for PDF (default: 85)
- `-m, --max-size`: Max PDF size in MB if no sections defined (default: 200)

## File Structure

```
project/
├── rotation_review.html    # Browser-based review tool
├── create_pdfs.py          # PDF generation script
├── apply_corrections.py    # Apply rotations to image files
├── image_list.txt          # List of images to review
├── image_review.json       # Exported corrections (after review)
├── final_preprocessed/     # Source images
└── pdfs/                   # Generated PDFs
```

## Technical Notes

### iPhone MPO Format

iPhone photos are stored in MPO (Multi-Picture Object) format containing multiple frames:
- Frame 0: Full resolution image
- Frame 1: Smaller secondary image (depth data)

The pipeline automatically extracts only the main frame to avoid duplicate pages in PDFs.

### Auto-Save

The review tool saves to browser localStorage after every action:
- Rotation changes
- Section break toggles
- Discard toggles
- Navigation (position tracking)

Data persists until you:
- Click "Clear Auto-Save"
- Clear browser data
- Use a different browser/URL

### Section Breaks

Mark section breaks at the **first image** of each new section (folder, document, etc.). The PDF will start a new file at each marked image.

## Requirements

- Python 3.7+
- Pillow (`pip install Pillow`)
- Modern web browser (for review tool)

## License

MIT
