"""
Computer vision core: webcam access + face detection (OpenCV and MediaPipe).

Works on Python 3.13. Two detector back-ends, chosen automatically:

  1. MediaPipe Face Landmarker (Tasks API): face boxes + facial landmark mesh.
     Needs a model file at  models/face_landmarker.task  (about 4 MB, downloaded
     once with `python download_models.py`). Newer MediaPipe releases no longer
     bundle models inside the package, so this file cannot ship with pip.
  2. OpenCV Haar cascade: face boxes only. The cascade XML ships inside OpenCV
     (cv2.data.haarcascades), so it needs no download and always works if
     OpenCV imports.

This is face DETECTION only. It does not recognise people, read emotions or
assess health. Frames are processed in memory and never saved.
"""

import os
import sys
import time
import urllib.request
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "face_landmarker.task")
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/"
             "face_landmarker/float16/1/face_landmarker.task")
MIN_MODEL_BYTES = 1_000_000  # the real file is about 3.7 MB; anything smaller is broken

# ----------------------------------------------------------------- imports
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
    CV2_ERROR = ""
except Exception as exc:  # cv2 missing or broken
    cv2 = np = None
    CV2_AVAILABLE = False
    CV2_ERROR = f"{type(exc).__name__}: {exc}"

try:
    import mediapipe as mp
    from mediapipe.tasks.python import vision as _mp_vision
    from mediapipe.tasks.python import BaseOptions as _MPBaseOptions
    _ = _mp_vision.FaceLandmarker  # make sure the Tasks API really exists
    MEDIAPIPE_AVAILABLE = CV2_AVAILABLE
    MEDIAPIPE_ERROR = "" if CV2_AVAILABLE else "OpenCV is not available"
except Exception as exc:
    mp = _mp_vision = _MPBaseOptions = None
    MEDIAPIPE_AVAILABLE = False
    MEDIAPIPE_ERROR = f"{type(exc).__name__}: {exc}"

# Backward-compatible flag used by older code
CV_AVAILABLE = CV2_AVAILABLE
CV_ERROR = CV2_ERROR

TEAL_BGR = (110, 118, 15)      # #0F766E in BGR
WHITE = (255, 255, 255)
MESH_BGR = (200, 190, 150)


# ----------------------------------------------------------------- diagnostics
def model_present():
    return os.path.isfile(MODEL_PATH) and os.path.getsize(MODEL_PATH) >= MIN_MODEL_BYTES


def haar_path():
    return os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml") if CV2_AVAILABLE else ""


def environment_report():
    """List of (check name, ok, detail) rows describing what works on this machine."""
    rows = [("Python", True, f"{sys.version.split()[0]}  ({sys.executable})")]
    if CV2_AVAILABLE:
        rows.append(("OpenCV", True, f"cv2 {cv2.__version__}"))
        rows.append(("NumPy", True, np.__version__))
        haar_ok = os.path.isfile(haar_path())
        rows.append(("Haar cascade file", haar_ok, haar_path() if haar_ok else "file not found"))
    else:
        rows.append(("OpenCV", False, CV2_ERROR))
    if MEDIAPIPE_AVAILABLE:
        rows.append(("MediaPipe (Tasks API)", True, f"mediapipe {mp.__version__}"))
    else:
        rows.append(("MediaPipe (Tasks API)", False, MEDIAPIPE_ERROR or "not installed"))
    rows.append(("Face landmarker model", model_present(),
                 MODEL_PATH if model_present() else "not downloaded (run: python download_models.py)"))
    return rows


def download_model(url=MODEL_URL, dest=MODEL_PATH, timeout=30):
    """Download the face landmarker model once. Returns (ok, message). Never raises."""
    tmp = dest + ".part"
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with urllib.request.urlopen(url, timeout=timeout) as response, open(tmp, "wb") as out:
            while True:
                chunk = response.read(1 << 16)
                if not chunk:
                    break
                out.write(chunk)
        size = os.path.getsize(tmp)
        with open(tmp, "rb") as f:
            is_zip = f.read(2) == b"PK"  # .task files are zip bundles
        if size < MIN_MODEL_BYTES or not is_zip:
            os.remove(tmp)
            return False, f"Downloaded file looks invalid ({size} bytes). Please try again."
        os.replace(tmp, dest)
        return True, f"Model saved to {dest} ({size / 1e6:.1f} MB)."
    except Exception as exc:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        return False, (f"Could not download the model ({type(exc).__name__}: {exc}). "
                       f"Check your internet connection, or download it manually from {url} "
                       f"and save it as {dest}")


# ----------------------------------------------------------------- camera
def _open_source(source):
    """Open one camera index (or video file) and confirm a frame can be read."""
    backends = [None]
    if isinstance(source, int) and sys.platform.startswith("win"):
        backends = [cv2.CAP_DSHOW, None]  # DirectShow opens faster and more reliably on Windows
    for backend in backends:
        cap = cv2.VideoCapture(source) if backend is None else cv2.VideoCapture(source, backend)
        if cap.isOpened():
            for _ in range(5):  # first frames can be empty while the camera warms up
                ok, frame = cap.read()
                if ok and frame is not None:
                    return cap
                time.sleep(0.05)
        cap.release()  # never leave a failed capture open
    return None


def open_camera(source=None, max_index=3):
    """
    Open a webcam. source=None tries indices 0..max_index-1 and keeps the first that works.
    source can also be an int index or a video file path (used by tests).
    Returns (capture, source_used, error_message). Exactly one of capture / error_message is None.
    """
    if not CV2_AVAILABLE:
        return None, None, f"OpenCV is not installed ({CV2_ERROR})."
    candidates = list(range(max_index)) if source is None else [source]
    for candidate in candidates:
        cap = _open_source(candidate)
        if cap is not None:
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            except Exception:
                pass  # some cameras refuse a resolution change; keep their default
            return cap, candidate, None
    tried = ", ".join(str(c) for c in candidates)
    return None, None, (
        f"Could not open a camera (tried: {tried}). Close other apps that use the webcam "
        "(Zoom, Teams, browser tabs), check Windows Settings > Privacy & security > Camera "
        "(allow desktop apps), and make sure a webcam is connected. No webcam? Use the "
        "Upload tab."
    )


# ----------------------------------------------------------------- detectors
@dataclass
class Face:
    box: tuple                      # (x, y, w, h) in pixels
    landmarks: object = None        # (N, 2) array of normalised points, or None


class HaarDetector:
    name = "OpenCV Haar cascade"
    has_landmarks = False

    def __init__(self):
        path = haar_path()
        if not os.path.isfile(path):
            raise RuntimeError(f"Haar cascade file not found: {path}")
        self.cascade = cv2.CascadeClassifier(path)
        if self.cascade.empty():
            raise RuntimeError(f"Haar cascade could not be loaded: {path}")

    def detect(self, bgr, timestamp_ms=None):
        h, w = bgr.shape[:2]
        scale = min(1.0, 480 / w)
        small = cv2.resize(bgr, (int(w * scale), int(h * scale))) if scale < 1 else bgr
        gray = cv2.equalizeHist(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
        boxes = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        return [Face(box=tuple(int(v / scale) for v in b)) for b in boxes]

    def close(self):
        pass


class MediaPipeDetector:
    name = "MediaPipe Face Landmarker"
    has_landmarks = True

    def __init__(self, video_mode=True, max_faces=3):
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError(f"MediaPipe is not available: {MEDIAPIPE_ERROR}")
        if not model_present():
            raise RuntimeError("Face landmarker model not found. Run: python download_models.py")
        self.video_mode = video_mode
        mode = _mp_vision.RunningMode.VIDEO if video_mode else _mp_vision.RunningMode.IMAGE
        options = _mp_vision.FaceLandmarkerOptions(
            base_options=_MPBaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mode, num_faces=max_faces,
        )
        self.landmarker = _mp_vision.FaceLandmarker.create_from_options(options)
        self._last_ts = -1
        conns = _mp_vision.FaceLandmarksConnections
        self.contours = self._pairs(conns.FACE_LANDMARKS_CONTOURS)
        self.tesselation = self._pairs(conns.FACE_LANDMARKS_TESSELATION)

    @staticmethod
    def _pairs(connections):
        return np.array([[c.start, c.end] for c in connections], dtype=np.int32)

    def detect(self, bgr, timestamp_ms=None):
        h, w = bgr.shape[:2]
        rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        if self.video_mode:
            ts = int(timestamp_ms if timestamp_ms is not None else time.monotonic() * 1000)
            ts = max(ts, self._last_ts + 1)  # MediaPipe needs strictly increasing timestamps
            self._last_ts = ts
            result = self.landmarker.detect_for_video(image, ts)
        else:
            result = self.landmarker.detect(image)
        faces = []
        for lms in result.face_landmarks:
            pts = np.array([[p.x, p.y] for p in lms], dtype=np.float32)
            x0, y0 = pts.min(axis=0) * (w, h)
            x1, y1 = pts.max(axis=0) * (w, h)
            pad_x, pad_y = 0.08 * (x1 - x0), 0.08 * (y1 - y0)
            x0, y0 = max(0, int(x0 - pad_x)), max(0, int(y0 - pad_y))
            x1, y1 = min(w - 1, int(x1 + pad_x)), min(h - 1, int(y1 + pad_y))
            faces.append(Face(box=(x0, y0, x1 - x0, y1 - y0), landmarks=pts))
        return faces

    def close(self):
        try:
            self.landmarker.close()
        except Exception:
            pass


@dataclass
class FaceEngine:
    """Runs a detector and draws boxes, labels and (if available) the landmark mesh."""
    detector: object
    notes: list = field(default_factory=list)
    show_mesh: bool = False

    @property
    def backend(self):
        return self.detector.name

    def process(self, bgr, timestamp_ms=None):
        """Return (annotated_bgr, info). The input frame is not modified."""
        faces = self.detector.detect(bgr, timestamp_ms)
        out = bgr.copy()
        h, w = out.shape[:2]
        for face in faces:
            if face.landmarks is not None:
                pts = (face.landmarks * (w, h)).astype(np.int32)
                segs = pts[self.detector.contours]
                cv2.polylines(out, list(segs), False, TEAL_BGR, 1, cv2.LINE_AA)
                if self.show_mesh:
                    cv2.polylines(out, list(pts[self.detector.tesselation]), False, MESH_BGR, 1, cv2.LINE_AA)
        for face in faces:
            x, y, bw, bh = face.box
            cv2.rectangle(out, (x, y), (x + bw, y + bh), TEAL_BGR, 2)
            label = "Face Detected"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            top = max(0, y - th - 8)
            cv2.rectangle(out, (x, top), (x + tw + 8, top + th + 8), TEAL_BGR, -1)
            cv2.putText(out, label, (x + 4, top + th + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 1, cv2.LINE_AA)
        info = {
            "backend": self.backend,
            "face_count": len(faces),
            "boxes": [f.box for f in faces],
            "has_landmarks": self.detector.has_landmarks,
        }
        return out, info

    def close(self):
        self.detector.close()


def create_engine(prefer="auto", video_mode=True, show_mesh=False):
    """
    Build a FaceEngine. prefer: "auto" | "mediapipe" | "opencv".
    Falls back to OpenCV Haar when MediaPipe is unavailable. Raises RuntimeError only if
    nothing at all can run. Returns (engine, notes) where notes explain any fallback.
    """
    if not CV2_AVAILABLE:
        raise RuntimeError(f"OpenCV is not installed ({CV2_ERROR}). Run: pip install -r requirements313.txt")
    notes = []
    detector = None
    if prefer in ("auto", "mediapipe"):
        try:
            detector = MediaPipeDetector(video_mode=video_mode)
        except Exception as exc:
            notes.append(f"MediaPipe is not being used: {exc} Using the OpenCV Haar detector instead "
                         "(face boxes only, no landmark mesh).")
    if detector is None:
        detector = HaarDetector()  # raises a clear RuntimeError if the cascade is missing
    engine = FaceEngine(detector=detector, notes=notes, show_mesh=show_mesh)
    return engine, notes


def decode_image(data):
    """Decode image bytes (jpg/png) to a BGR array, or None if unreadable."""
    if not CV2_AVAILABLE:
        return None
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)
