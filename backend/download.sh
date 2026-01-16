#!/usr/bin/env bash
set -e

BASE_URL="https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4"

FILES=("yolov4.cfg" "yolov4.weights")

for f in "${FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "[skip] $f already exists"
    else
        echo "[download] $f"
        curl -L -o "$f" "$BASE_URL/$f"
    fi
done

echo "Download complete. Files are now in $(pwd)"
