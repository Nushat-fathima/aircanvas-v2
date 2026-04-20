# ✋ Air Canvas V2

> Draw in the air using just your hand gestures — no mouse, no stylus, just your fingers and a webcam.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=flat-square&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## 🎥 Demo

> Point your index finger at the screen and pinch with your thumb to start drawing!

---

## ✨ Features

### 🖌️ Brush Types
| Brush | Description |
|-------|-------------|
| **Pen** | Smooth anti-aliased strokes |
| **Spray** | Scattered particle spray effect |
| **Dotted** | Evenly spaced dot trail |
| **Calligraphy** | Angled thick stroke — responds to direction |
| **Eraser** | Circle eraser — erase without clearing canvas |

### 🎨 Color System
- **8-color arc palette** at the top of the screen
- Hover your finger over a color and pinch to select
- Colors: Red, Orange, Yellow, Green, Cyan, Purple, White, Pink

### 🧰 On-Screen Toolbar
- Left-side toolbar with labeled buttons
- Switch brushes, Undo, Redo, Save, and Clear — all with a pinch gesture

### ⏪ Undo / Redo
- Up to **20 levels** of undo
- Works via toolbar pinch or keyboard (`Z` / `Y`)

### 💾 Save Drawing
- Save your canvas as a timestamped PNG anytime
- Via toolbar pinch or `S` key

### ✨ Particle Effects
- Sparks burst from your fingertip while drawing
- Physics-based gravity and fade

### 🔭 Sci-Fi HUD
- Hand skeleton overlay with cyan joint lines
- Pinch indicator bar on index fingertip
- Live status bar at bottom of screen

### ⚡ Performance
- Optimised MediaPipe (`model_complexity=0`)
- Pinch debounce to prevent accidental triggers
- Smooth cursor interpolation

---

## 🚀 Getting Started

### Prerequisites
- Python **3.8 – 3.11** (recommended)
- A working **webcam**

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/aircanvas-v2.git
cd aircanvas-v2
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python aircanvas_v2.py
```

---

## 🎮 Controls

| Action | How |
|--------|-----|
| **Draw** | Pinch index + thumb, move hand |
| **Select color** | Hover over arc palette → Pinch |
| **Switch brush** | Pinch toolbar button on left |
| **Undo** | Pinch UNDO button or press `Z` |
| **Redo** | Pinch REDO button or press `Y` |
| **Save canvas** | Pinch SAVE button or press `S` |
| **Clear canvas** | Pinch CLEAR button |
| **Quit** | Press `Q` |

---

## 🗂️ Project Structure

```
aircanvas-v2/
│
├── aircanvas_v2.py        # Main application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
│
└── screenshots/           # Add your demo screenshots here
    └── .gitkeep
```

---

## 🔧 Configuration

Open `aircanvas_v2.py` and edit the `Config` class to tweak settings:

```python
class Config:
    WIDTH, HEIGHT = 1280, 720     # Resolution
    PINCH_THRESHOLD = 40          # Pinch sensitivity (lower = harder to trigger)
    SMOOTHING = 0.5               # Cursor smoothing (0.1 = smooth, 0.9 = instant)
    BRUSH_SIZE = 8                # Default brush size
    ERASER_SIZE = 30              # Eraser radius
    MAX_UNDO = 20                 # Undo history depth
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| Camera not opening | Change `cv2.VideoCapture(0)` → `cv2.VideoCapture(1)` |
| `mediapipe` install fails | Try `pip install mediapipe==0.10.9` |
| DLL error on Windows | Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) |
| Hand not detected | Ensure good lighting, plain background preferred |
| Laggy drawing | Lower resolution in Config or reduce `BRUSH_SIZE` |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `opencv-python` | ≥ 4.8.0 | Camera feed, drawing, display |
| `mediapipe` | ≥ 0.10.9 | Hand landmark detection |
| `numpy` | ≥ 1.24.0 | Canvas array operations |

---

## 🔄 Changelog

### V2.0 (Latest)
- ✅ Added Spray, Dotted, Calligraphy brush types
- ✅ Added Eraser tool
- ✅ Undo / Redo (20 levels)
- ✅ Save drawing to PNG
- ✅ On-screen toolbar with pinch interaction
- ✅ Particle effects while drawing
- ✅ Faster hand detection (`model_complexity=0`)
- ✅ Pinch debounce for accuracy
- ✅ Cross-platform sound support
- ✅ Live status bar

### V1.0 (Original by [samee0102](https://github.com/samee0102/aircanvas))
- Basic pinch-to-draw
- Arc color palette
- Sci-fi HUD overlay
- Neon glow effect
- Windows sound engine

---

## 🙏 Credits

- Original project by **[samee0102](https://github.com/samee0102/aircanvas)**
- Hand tracking powered by **[MediaPipe](https://mediapipe.dev/)** by Google
- V2 enhancements built on top of the original

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify and share.

---

## ⭐ Support

If you found this project cool, give it a **star** ⭐ on GitHub — it means a lot!
