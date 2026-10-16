"""
Standalone webcam + face-detection check. Does NOT use Streamlit.

Run it with the same Python that runs the app:
    .\\.venv313\\Scripts\\python.exe scripts\\test_webcam.py

Options:
    --show              open a preview window with face boxes (press Q to quit)
    --seconds 5         how long to run the live detection step (default 5)
    --camera 1          use camera index 1 instead of auto-detecting
    --backend opencv    force the OpenCV Haar detector (auto | mediapipe | opencv)
    --image photo.jpg   skip the webcam and test detection on one image
    --source clip.avi   use a video file instead of a webcam (for testing)

Every step prints PASS, FAIL or SKIP. The exit code is 0 only if nothing failed.
"""

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import cv_utils  # noqa: E402

results = []


def report(status, name, detail=""):
    results.append(status)
    print(f"[{status}] {name}" + (f" - {detail}" if detail else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--seconds", type=float, default=5.0)
    parser.add_argument("--camera", type=int, default=None)
    parser.add_argument("--backend", default="auto", choices=["auto", "mediapipe", "opencv"])
    parser.add_argument("--image")
    parser.add_argument("--source", help="video file to use instead of a webcam")
    args = parser.parse_args()

    print(f"Python executable: {sys.executable}")
    print(f"Python version:    {sys.version.split()[0]}\n")

    # 1-3: interpreter and imports
    report("PASS" if sys.version_info >= (3, 9) else "FAIL", "Python version", sys.version.split()[0])
    if not cv_utils.CV2_AVAILABLE:
        report("FAIL", "OpenCV import", cv_utils.CV2_ERROR)
        print("\nInstall into THIS interpreter:  "
              f"{sys.executable} -m pip install -r requirements313.txt")
        return 1
    report("PASS", "OpenCV import", f"cv2 {cv_utils.cv2.__version__}, numpy {cv_utils.np.__version__}")
    if cv_utils.MEDIAPIPE_AVAILABLE:
        report("PASS", "MediaPipe import", f"mediapipe {cv_utils.mp.__version__} (Tasks API)")
    else:
        report("SKIP", "MediaPipe import", f"{cv_utils.MEDIAPIPE_ERROR} (OpenCV fallback will be used)")
    report("PASS" if cv_utils.model_present() else "SKIP", "MediaPipe face model",
           cv_utils.MODEL_PATH if cv_utils.model_present() else "not downloaded: run  python download_models.py")

    # 4: detector
    try:
        engine, notes = cv_utils.create_engine(args.backend, video_mode=not args.image)
        report("PASS", "Face detector initialised", engine.backend)
        for n in notes:
            print(f"       note: {n}")
    except Exception as exc:
        report("FAIL", "Face detector initialised", str(exc))
        return 1

    cv2 = cv_utils.cv2

    # --- image mode
    if args.image:
        img = cv2.imread(args.image)
        if img is None:
            report("FAIL", "Read image", args.image)
            return 1
        _, info = engine.process(img)
        report("PASS" if info["face_count"] else "FAIL", "Face detection on image",
               f"{info['face_count']} face(s)")
        engine.close()
        return 1 if "FAIL" in results else 0

    # 5-6: camera + frames
    cap, used, error = cv_utils.open_camera(args.source if args.source else args.camera)
    if cap is None:
        report("FAIL", "Camera opens", error)
        engine.close()
        return 1
    report("PASS", "Camera opens", f"source {used}")
    ok, frame = cap.read()
    if not ok:
        report("FAIL", "Frame capture")
        cap.release(); engine.close()
        return 1
    report("PASS", "Frame capture", f"{frame.shape[1]}x{frame.shape[0]}")

    # 7: live detection loop
    frames = faces_seen = 0
    start = time.time()
    try:
        while time.time() - start < args.seconds:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            out, info = engine.process(frame)
            frames += 1
            faces_seen += info["face_count"] > 0
            if args.show:
                cv2.putText(out, f"faces: {info['face_count']}  (Q to quit)", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow("Mentivara webcam test", out)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
    finally:
        cap.release()
        engine.close()
        if args.show:
            cv2.destroyAllWindows()
    elapsed = max(time.time() - start, 1e-6)
    report("PASS" if frames else "FAIL", "Live processing", f"{frames} frames, {frames / elapsed:.1f} FPS")
    if faces_seen:
        report("PASS", "Face detected on live video", f"in {faces_seen} of {frames} frames")
    else:
        report("FAIL", "Face detected on live video",
               "no face seen: face the camera with good lighting and re-run (camera itself works)")
    report("PASS", "Camera released")
    print("\nResult:", "ALL PASSED" if "FAIL" not in results else "SOME CHECKS FAILED")
    return 1 if "FAIL" in results else 0


if __name__ == "__main__":
    sys.exit(main())
