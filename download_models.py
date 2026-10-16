"""
Download the MediaPipe face landmarker model (about 4 MB, one time).

Run:  python download_models.py

Without this file the app still works: it falls back to OpenCV's built-in Haar
face detector (face boxes only, no landmark mesh).
"""

import sys

from utils import cv_utils

if cv_utils.model_present():
    print(f"Model already present: {cv_utils.MODEL_PATH}")
    sys.exit(0)

print("Downloading face landmarker model...")
ok, message = cv_utils.download_model()
print(message)
sys.exit(0 if ok else 1)
