#!/bin/bash
#
# render_writeup.sh
# Renders writeup/results_v1.0.md to PDF using pandoc + xelatex.
#
# Outputs:
#   writeup/results_v1.0.pdf
#
# Required system packages on Ubuntu/Debian:
#   pandoc, texlive-xetex, texlive-fonts-recommended, texlive-latex-extra
#
# Run from the repository root.

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

SOURCE="writeup/results_v1.0.md"
OUTPUT="writeup/results_v1.0.pdf"
METADATA="writeup/pandoc_metadata.yaml"

if [ ! -f "$SOURCE" ]; then
    echo "ERROR: source file not found at $SOURCE" >&2
    exit 1
fi

if [ ! -f "$METADATA" ]; then
    echo "ERROR: metadata file not found at $METADATA" >&2
    exit 1
fi

echo "Rendering $SOURCE -> $OUTPUT"
echo

pandoc \
    --from markdown+pipe_tables+raw_tex \
    --to pdf \
    --pdf-engine=xelatex \
    --metadata-file="$METADATA" \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --highlight-style=tango \
    --output="$OUTPUT" \
    "$SOURCE"

echo "Render complete: $OUTPUT"
echo
echo "File size: $(du -h "$OUTPUT" | cut -f1)"
echo "SHA-256:   $(sha256sum "$OUTPUT" | cut -d' ' -f1)"
