# Bootcamp Demo Plan: Mentivara AI

**Format:** about 7 minutes plus questions. Practise once with a timer.

## Before you present
- Run the app on your own laptop and open it once beforehand (the first camera start takes a moment).
- Run `python download_models.py` once (optional, adds the landmark mesh) and `python train_model.py` so the model exists, and keep the app open on the **Home** page.
- Check the webcam works. Prepare a photo of a face in your Downloads folder as a backup for the Upload tab.
- Close apps that use the camera (Zoom, Teams). Plug in the charger.
- Have the GitHub repo open in another tab.

## Script

| Time | Show | Say |
|------|------|-----|
| 0:00-0:45 | Home page | The problem: wellness tools are scattered, and many overclaim. Mentivara AI combines four things in one app and is honest about what it can and cannot do. Point at the disclaimer. |
| 0:45-2:30 | Screening | Run it live, answering quickly (consider pre-agreeing a pattern). On results: show the two readings side by side. Explain that the rule-based score is transparent and the RandomForest is trained per domain on 28 answers. Open **How the scoring works** and state clearly that the training data is synthetic. |
| 2:30-4:00 | Computer Vision | Read the consent text, tick the box, press **Start camera**. Show the face box, the "Face Detected" label, the face count and FPS. If you downloaded the model, switch the detector to MediaPipe to show the landmark mesh. Say what it is (face detection with OpenCV and MediaPipe) and what it is not (no recognition, emotion or health inference). Press **Stop camera**. Mention frames are not saved. |
| 4:00-5:15 | Breathing | Choose 1 minute and Start. Let one breath play, then Pause and Resume. Mention it works without a camera and is not a treatment. |
| 5:15-6:15 | Chatbot | Tap **Grounding exercise**. Say it is rule-based on purpose and show that crisis wording triggers a safety message (use a test phrase and explain you are testing the safeguard). |
| 6:15-7:00 | GitHub / README | Show the README, the structure, `python -m pytest` (57 tests) and the roadmap. Close with what you learned. |

## Key talking points
- **Responsible AI:** synthetic-data disclosure, no emotion inference, no diagnosis claims, opt-in camera, crisis safeguards.
- **Engineering:** modular pages and utilities, graceful fallbacks (missing model, missing camera), automated tests, pinned dependencies.
- **Technologies:** Streamlit, scikit-learn, OpenCV, MediaPipe, Plotly, a small JS component for the animation.

## Likely questions and honest answers
- **How accurate is the model?** On synthetic data it reproduces the rule-based labels at the accuracy shown in `model/training_report.txt` (quote your own number; mine were roughly 92-95%). That says nothing about real people, because it was never validated clinically.
- **Why also keep a rule-based scorer?** It is transparent and checkable by hand, and the model's labels come from it.
- **Can the camera detect depression or emotions?** No. Facial landmarks cannot diagnose a condition, so the app only shows tracking.
- **Where does the data go?** Nowhere. No database, no analytics. Frames are processed in memory.
- **What would you do next?** Use a licensed clinical dataset, validate with professionals, add explainability (SHAP).
- **Why not an LLM chatbot?** It adds safety risks and complexity. A curated, rule-based bot is predictable for a wellness demo.

## If something goes wrong
- **Webcam fails:** run `scripts/test_webcam.py` to see why, or switch to the **Upload a photo** tab and use the backup photo.
- **Model missing:** open results and press **Train model now**.
- **Camera busy:** close Zoom, Teams and the Windows Camera app, then press Start camera again.
