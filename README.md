# 🧠 Mentivara AI

**AI-Based Mental Health Screening and Wellness Support System**

**Developed by: Anas Hasnain**
**Degree Program: BS Artificial Intelligence**
**Project: AI Bootcamp Final Project**

**Introduction**

**Mental health is an important part of our lives. Many people experience problems such as anxiety, depression, stress, and difficulty concentrating. However, some people do not understand their symptoms or do not receive help at the right time.**

**Mentivara AI is an AI-based project designed to support doctors and patients in understanding possible mental health concerns. It uses a series of questions to collect information about how a patient feels and behaves. A machine-learning model then analyzes the answers and provides an initial screening result that may help a doctor decide whether further assessment is needed.**

The application also includes a webcam-based face-detection feature using OpenCV and MediaPipe, a guided breathing exercise to help users relax, and a wellness chatbot that provides general information and supportive suggestions.

The main goal of Mentivara AI is to bring these features together in one easy-to-use platform. It aims to support early screening, improve mental health awareness, encourage relaxation, and help doctors explore digital tools that may assist them during patient assessments.

In the future, Mentivara AI could be improved through medically reviewed questionnaires, better-tested machine-learning models, and collaboration with qualified mental health professionals.




> ⚠️ **Not a medical product.** Mentivara AI is an educational demonstration. It is not a diagnostic tool, not a medical device and not an emergency service.
---

## ✨ Features

| Page | What it does |
|------|--------------|
| 🏠 **Home** | Overview and quick links. |

| 📋 **Screening** | 28 questions in the style of PHQ-9, GAD-7, ASRS and ISI (depression, anxiety, ADHD, insomnia). Shows a **rule-based** reading and a **RandomForest** prediction side by side, a summary of your answers, wellness suggestions, a scoring explanation and a downloadable `.txt` report. |

| 📷 **Computer Vision** | Opt-in live webcam demo with **Start / Stop camera** buttons: face bounding boxes, a "Face Detected" label, a face count and FPS. MediaPipe adds a facial landmark mesh. Also has a snapshot mode and a **no-webcam photo-upload mode**. |

| 🌬️ **Breathing Exercise** | Animated circle, phase instructions, countdown, progress bar, Start / Pause / Resume / Stop, 1 / 3 / 5 minute sessions, a choice of gentle paces and an option to skip the hold. Works without a camera. |
| 💬 **Chatbot** | Rule-based assistant with curated tips on stress, anxiety, low mood, sleep, focus, grounding, breathing and when to seek help. Includes crisis-language safeguards. |

| ℹ️ **About** | Technologies, limitations and privacy. |


## 🚀 How to Run Mentivara AI

Follow these steps to download and run Mentivara AI on your computer.

### 1. Requirements

Before starting, make sure you have installed:

- **Python:** A compatible Python version (Python 3.12 is recommended for testing the project's dependencies).
- **Git:** To clone the repository, or download the project as a ZIP file.
- **A web browser:** Such as Google Chrome, Microsoft Edge, or Firefox.
- **VS Code (optional):** For editing and running the project.

### 2. Clone the Repository

Open your terminal or PowerShell and run:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual URL of this repository.

Move into the project folder:

```bash
cd mentivara-ai
```

Alternatively, download the repository as a ZIP file from GitHub, extract it, and open the extracted folder in your terminal.

### 3. Create a Virtual Environment

Create an isolated Python environment to install the project's dependencies.

**Windows:**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

**macOS or Linux:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

If Python 3.12 is not installed, install a compatible version before continuing.

### 4. Install Dependencies

Make sure the repository contains a `requirements.txt` file listing all the Python packages needed by the project.

Install the dependencies with:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails, check the Python version and the compatibility of the required packages, particularly OpenCV and MediaPipe.

### 5. Run the Application

From the main project folder, where `app.py` is located, run:

```bash
python -m streamlit run app.py
```

Streamlit will start the application and display a local address in the terminal, usually:

```text
http://localhost:8501
```

Open this address in your web browser to access Mentivara AI.

### 6. Explore the Features

Once the application opens, you can explore the available sections:

- **Home:** Introduction to Mentivara AI and its purpose.
- **Screening:** Answer the questionnaire and review the generated screening result.
- **Computer Vision:** Test the supported webcam and face-detection features.
- **Breathing Exercise:** Follow the guided breathing activity.
- **Chatbot:** Explore general wellness information and supportive suggestions.
- **About:** Learn more about the project and its development.

**Camera access:** Allow camera permission in your browser when prompted. Webcam functionality may depend on your operating system, browser, installed dependencies, and camera configuration.

### 7. Stop the Application

To stop the Streamlit server, return to the terminal and press:

```text
Ctrl + C
```

## 🗂️ Project structure

```
mentivara-ai/
├── app.py                      # Entry point: page config, shared state, navigation
├── train_model.py              # Trains and saves the ML model bundle
├── download_models.py          # One-time download of the MediaPipe face model
├── requirements313.txt         # Dependencies for Python 3.13 (requirements.txt points here)
├── requirements-dev.txt        # + pytest
├── scripts/
│   └── test_webcam.py          # Standalone webcam + face-detection check
├── models/                     # face_landmarker.task lives here after download_models.py
├── pages/
│   ├── home.py
│   ├── screening.py            # Questionnaire, results, report download
│   ├── computer_vision.py      # Consent, Start/Stop camera, live detection, snapshot, upload
│   ├── breathing_exercise.py
│   ├── chatbot.py
│   └── about.py
├── utils/
│   ├── questions.py            # Question bank, weights, thresholds, rule-based scoring
│   ├── predictor.py            # Loads the model and runs inference
│   ├── model_utils.py          # Safe prediction wrapper, in-app training, answer summary
│   ├── report_utils.py         # Builds the downloadable report
│   ├── safety_utils.py         # Crisis-language detection and urgent-help text
│   ├── chatbot_utils.py        # Chatbot topics and routing
│   ├── cv_utils.py             # Webcam access + OpenCV/MediaPipe face detection
│   ├── breathing_component.py  # HTML/CSS/JS breathing widget
│   ├── treatment_plans.py      # Psychoeducational content
│   └── ui.py                   # Shared styling helpers
├── data/generate_dataset.py    # Synthetic training-data generator
├── model/                      # Created by train_model.py (model + training report)
├── tests/                      # pytest suite
├── docs/
│   ├── DEMO_PLAN.md            # Bootcamp presentation plan
│   └── TESTING_CHECKLIST.md    # Manual test checklist
└── .streamlit/config.toml      # Theme
```

## 🤖 How it works

### Screening: two readings of the same answers
1. **Rule-based scorer (transparent).** Each answer is 0-3. It is multiplied by an item weight and summed per domain. The total is compared with fixed thresholds (share of the maximum score) in `utils/questions.py`.
2. **Machine-learning model.** One `RandomForestClassifier` per domain is trained on the 28 raw answers and predicts None / Mild / Moderate / Severe.

Wellness suggestions appear when **either** reading reaches Mild or above.

### ⚠️ About the model: synthetic data
There is no public, ethically sourced dataset of item-level questionnaire answers, so `data/generate_dataset.py` **simulates** respondents and labels them with the same rule-based scorer. The model therefore learns to reproduce that rule.

- Its test accuracy (see `model/training_report.txt` after training) measures agreement with the synthetic labels. It is **not** evidence of clinical accuracy.
- The "vote share" per class is the model's relative score. It is **not** the probability that a person has a condition, and the app says so.

### Computer vision
- **Camera:** OpenCV (`cv2.VideoCapture`) opens the webcam only when you press **Start camera**. It tries cameras 0, 1 and 2, keeps one capture open across Streamlit reruns, and releases it on **Stop camera**, on any page change, or if the feed fails.
- **Detector, chosen automatically:**
  1. **MediaPipe Face Landmarker** (Tasks API): face boxes plus a landmark mesh. Needs the model file in `models/` (`python download_models.py`). Newer MediaPipe releases no longer bundle models, and the older `mp.solutions` API is not available on Python 3.13.
  2. **OpenCV Haar cascade**: face boxes only. The XML ships inside OpenCV, so it needs no download and is the guaranteed fallback.
- **Display:** the annotated frames are shown about 25 times per second.

This is face **detection** only. It does **not** recognise people, read emotions or assess mental health. Facial landmarks cannot diagnose any condition.

### Breathing
The animation and timer run entirely in the browser (`utils/breathing_component.py`), so Streamlit reruns cannot reset them. Sessions are rounded to whole breaths so they never end mid-breath.

### Chatbot
Keyword matching against a small set of curated answers. It is **not** generative AI and **not** an agent. Messages that look like crisis language get a supportive message that points to emergency services and local helplines. Keyword detection cannot guarantee that every crisis is recognised, so every page also carries an urgent-help notice.


## 🧰 Technologies

Python · Streamlit · scikit-learn (RandomForest) · pandas / NumPy · Plotly · OpenCV · MediaPipe (Tasks API) · vanilla HTML/CSS/JS (breathing widget) · pytest

## 🧪 Testing

```powershell
.\.venv313\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv313\Scripts\python.exe -m pytest
```

The suite (57 tests) covers scoring, the model interface, chatbot routing, crisis detection, report contents, every page loading, the full screening flow, face-detector fallback, camera open/close and error handling (using a video file as a stand-in webcam), model-download validation, and the camera-consent and cleanup behaviour.

A physical webcam cannot be automated, so use `scripts\test_webcam.py` and the manual checklist in [`docs/TESTING_CHECKLIST.md`](docs/TESTING_CHECKLIST.md).


## 👤 Author

**Anas Hasnain**, BS Artificial Intelligence · 
[GitHub](https://github.com/AnasHasnain333) · [LinkedIn](https://linkedin.com/in/anas-hasnain-a28277323)

## 📄 License

MIT. See [LICENSE](LICENSE).
