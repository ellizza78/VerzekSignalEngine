#!/bin/bash
# VerzekAutoTrader - Backend File Manifest Generator
# Generates complete MD5 hash manifest for all backend files
# Usage: ./tools/generate_manifest.sh

set -e

BACKEND_DIR="backend"
OUTPUT_FILE="backend/FILE_MANIFEST_HASHES.txt"

echo "🔍 Scanning backend directory for all files..."

# Count files
FILE_COUNT=$(cd "$BACKEND_DIR" && find . -type f \
    ! -path "*/__pycache__/*" \
    ! -name "*.pyc" \
    ! -path "*/.git/*" \
    ! -path "*/instance/*" \
    ! -path "*/verzek_*.db*" \
    ! -path "*/logs/*" \
    | wc -l)

echo "📦 Found $FILE_COUNT files to track"

# Generate manifest header
cat > "$OUTPUT_FILE" << EOF
# VerzekAutoTrader Backend - COMPLETE File Manifest with Hashes
# Generated: $(date +%Y-%m-%d)
# Total Files: $FILE_COUNT

# MD5 Hash Format: filepath:hash
# Excludes: __pycache__, *.pyc, .git/, instance/, *.db, logs/

EOF

# Generate hashes
cd "$BACKEND_DIR"
find . -type f \
    ! -path "*/__pycache__/*" \
    ! -name "*.pyc" \
    ! -path "*/.git/*" \
    ! -path "*/instance/*" \
    ! -path "*/verzek_*.db*" \
    ! -path "*/logs/*" \
    -exec md5sum {} \; | \
    awk '{print $2":"$1}' | \
    sort >> "../$OUTPUT_FILE"

cd ..

echo "" >> "$OUTPUT_FILE"
echo "# ✅ ALL $FILE_COUNT BACKEND FILES TRACKED" >> "$OUTPUT_FILE"
echo "# Use this manifest to detect file drift or unauthorized changes" >> "$OUTPUT_FILE"

echo "✅ Manifest generated: $OUTPUT_FILE"
echo "📊 Total files tracked: $FILE_COUNT"
