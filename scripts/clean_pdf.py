#!/usr/bin/env python3
"""PDF metadata cleaner.

Usage:
    python clean_pdf.py <input.pdf> [output.pdf]

- Strips shell Info dictionary and XMP metadata via exiftool
- Rebuilds with PyMuPDF garbage=4 compression
- Does not re-encode embedded images (avoids rendering corruption)
"""
import sys
import os
import subprocess

import pymupdf


def clean_pdf(src: str, dst: str) -> None:
    # 1. exiftool: clear all metadata (including XMP)
    subprocess.run(
        ["exiftool", "-all=", "-o", dst, src],
        check=True, capture_output=True,
    )

    # 2. PyMuPDF: clear Info dict + garbage=4 rebuild
    doc = pymupdf.open(dst)
    doc.set_metadata({})
    tmp = dst + ".tmp"
    doc.save(tmp, garbage=4, deflate=True)
    doc.close()
    os.replace(tmp, dst)

    # 3. Verify
    result = subprocess.run(
        ["exiftool", "-a", "-G1", "-s", dst],
        capture_output=True, text=True,
    )
    keep_prefixes = (
        "[ExifTool]", "[System]", "[File]",
    )
    remaining = [
        line for line in result.stdout.splitlines()
        if line.strip() and not line.startswith(keep_prefixes)
    ]
    if remaining:
        print("⚠️  Residual metadata:", file=sys.stderr)
        for line in remaining:
            print(f"  {line}", file=sys.stderr)
    else:
        print(f"✅ {os.path.basename(dst)}: metadata clean ({os.path.getsize(dst)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_pdf.py <input.pdf> [output.pdf]")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.getcwd(), os.path.basename(src)
    )
    clean_pdf(src, dst)
