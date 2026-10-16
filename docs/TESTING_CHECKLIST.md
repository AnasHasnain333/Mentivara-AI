# Manual Testing Checklist

Run `streamlit run app.py` and work through each section. Tick items as you go.

## 0. Start-up
- [ ] App opens at http://localhost:8501 with the Mentivara AI header
- [ ] Sidebar shows all six pages and the disclaimer
- [ ] Every page opens without a red error box

## 1. Questionnaire and report
- [ ] Screening → **Start screening** shows question 1 of 28
- [ ] **Back** keeps the answer you chose earlier
- [ ] Finish all 28 questions → results page appears
- [ ] Answer everything "Never": no domain reaches Mild and a green message is shown
- [ ] Answer everything "Almost Always": domains show Severe and a professional-support notice appears
- [ ] Answer "Never" everywhere except the self-harm question (question 9): the safety message appears
- [ ] The summary row, bar chart, per-domain sections and **How the scoring works** are present
- [ ] Wording says results are preliminary and the model uses synthetic data
- [ ] **Download report (.txt)** saves a file with the disclaimer, scores and limitations
- [ ] **Retake screening** returns to the intro
- [ ] (Optional) rename `model/` and reopen results: a clear message and a **Train model now** button appear

## 2. Breathing exercise
- [ ] Page works with no camera permission given
- [ ] Choose 1 / 3 / 5 min: the time-left display changes
- [ ] **Start**: the circle grows on "Breathe in", stays on "Hold gently", shrinks on "Breathe out"
- [ ] Phase countdown, total countdown and progress bar all move
- [ ] **Pause** freezes everything, **Resume** continues from the same point
- [ ] **Stop** returns to the ready state
- [ ] Tick **Skip the hold**: the hold phase disappears
- [ ] Change the pace dropdown: the timings change
- [ ] Let a 1-minute session finish: the completion message appears
- [ ] Switch to another page and back: nothing is broken

## 3. Camera (needs a real webcam)
First run the standalone check, outside Streamlit:
`.\.venv313\Scripts\python.exe scripts\test_webcam.py --show`

- [ ] Every line says PASS (SKIP for the MediaPipe model is fine if you have not downloaded it)
- [ ] The preview window shows a box around your face; closing it with Q ends the script cleanly

Then in the app, **Computer Vision** page:
- [ ] The camera light is **off** when you open the page
- [ ] **Live camera** tab: the controls only appear after you tick the consent box
- [ ] Press **Start camera**: a "Starting camera" spinner appears, then live video
- [ ] A box and the label "Face Detected" appear around your face; the status shows the face count and FPS
- [ ] Cover your face: status changes to "No face detected"
- [ ] Two people in view: the count goes to 2
- [ ] Press **Stop camera**: the camera light goes off and the video stops
- [ ] Start again after stopping: it works without restarting the app
- [ ] Start the camera, then open another page: the camera light goes off
- [ ] Choose "OpenCV boxes only" in the Detector box: boxes still work
- [ ] After `python download_models.py`, choose "MediaPipe landmarks": a contour mesh appears on your face
- [ ] Start with the webcam in use by another app (e.g. Zoom): a clear error message appears and the app stays usable
- [ ] **Snapshot** tab asks you to tick a box first, then analyses one photo
- [ ] **Upload a photo** tab works with no camera
- [ ] No image files are written to the project folder

## 4. Chatbot
- [ ] Welcome message says it is a simple rule-based bot, not generative AI
- [ ] Quick-topic buttons return curated tips
- [ ] "I feel anxious about exams" gets the anxiety tip
- [ ] A message such as "I want to end my life" gets the supportive emergency message (use a test phrase only)
- [ ] **Topics we talked about** and **Clear conversation** work

## 5. Responsive layout and accessibility
- [ ] Narrow the browser window to phone width: nothing overflows horizontally
- [ ] Buttons can be reached with the Tab key and show a focus outline
