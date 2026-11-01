---
name: pdf-metadata-cleaner
description: Clean PDF metadata (EXIF/XMP/DocInfo/author/device/scanner info) and remove page watermarks. Use when user asks to "clean", "remove EXIF", "remove watermark", "strip metadata", or "remove scanner info" from a PDF. Supports Konica Minolta copiers, CamScanner, WPS, iText watermarks, Adobe InDesign, and other common sources.
---

# PDF Metadata & Watermark Cleaner

## Standard Workflow

1. **Inspect**: Use exiftool to read shell metadata and XMP; use PyMuPDF to check page count and watermark text.
2. **Strip metadata**: `exiftool -all= -o <output> <input>` to clear all shell and XMP metadata.
3. **Rebuild**: PyMuPDF `set_metadata({})` + `garbage=4, deflate=True` save.
4. **Remove watermarks** (if any): PyMuPDF `search_for` + `add_redact_annot` + `apply_redactions`.
5. **Verify**: Re-run exiftool to confirm no residual metadata; render first/last pages to confirm non-blank.

## Tool Paths

- **exiftool**: Must be installed and available in `PATH`. If not, download from [exiftool.org](https://exiftool.org/).
- **PyMuPDF**: `pip install pymupdf`
- **Cleaning script**: `scripts/clean_pdf.py <input> [output]`

## Critical Pitfalls (verified lessons)

- **Never** re-encode embedded JPEGs with Pillow and replace streams via PyMuPDF `update_stream` — this causes object dictionary mismatch and renders pages as white screens with black bars.
- **Never** rely on PyMuPDF `set_metadata({})` alone — it only clears the Info dictionary, not the XMP metadata stream. Always run exiftool `-all=` first, then rebuild with `garbage=4`.
- **Do not re-encode embedded image streams**. Leave them untouched.

## Common Watermark Patterns

| Source | Watermark特征 | Approach |
|---|---|---|
| CamScanner | "扫描全能王 创建" at page bottom | `search_for("扫描全能王")` then redact |
| iText account watermark | Repeating grid of "Department:username" with truncated variants | Search for a short stable substring (e.g. the pinyin/username fragment) to catch all variants |
| Konica Minolta copiers | JPEG Comment field containing `KM_<model>` | `exiftool -Comment=` to strip losslessly (skip if empty) |
| WPS Office | Author field containing real name | exiftool `-all=` clears automatically |

## Output Naming

- Output with the original filename unless the user specifies a different name.
