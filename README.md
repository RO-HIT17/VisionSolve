# Vision Solve

---

> **Built by Team Code Crusaders for HackIT - ITRIX '25**  

---

## 🚀 About VisionSolve

**VisionSolve** is an **AI-powered web application** that converts **handwritten, typed, and natural language math & science expressions** into **LaTeX representations** and generates **animated visual explanations with audio narration**. Designed to bridge the gap between static content and dynamic learning, VisionSolve aims to revolutionize how math and science are taught, learned, and shared.

---

## 🎯 Key Highlights

- ✍️ **Handwritten to LaTeX** using state-of-the-art Pix2Tex model.
- 📄 **Typed and natural language input** support for versatile use cases.
- 🎥 **Animated videos** created via **Manim** for enhanced visual understanding.
- 🔊 **Audio narration** for step-by-step explanations.
- 🌐 **Web app interface** for easy accessibility.
- 📚 **Support for math, physics, chemistry, and general science concepts.**

---

## 📊 Dataset and Training

- **Dataset Used**: [CROHME Dataset](https://www.isical.ac.in/~crohme/) (Competition on Recognition of Online Handwritten Mathematical Expressions).
- **Model**: Custom-trained **Pix2Tex** model optimized for diverse mathematical and scientific symbols.

---

## 🛠️ Tech Stack

| Technology                   | Purpose                                             |
|-----------------------------|-----------------------------------------------------|
| **Pix2Tex**                 | Handwritten/typed math to LaTeX conversion           |
| **CROHME Dataset**          | Dataset for model training                          |
| **Manim**                   | Mathematical and scientific animations engine       |
| **Python, FastAPI**         | Backend API and processing                         |
| **React.js**                | Frontend web interface                              |
| **PyTorch**                 | Model training and inference                        |
| **FFmpeg**                  | Video and audio processing                          |
| **Google Text-to-Speech**  | Audio narration generation                          |


---

## 💻 Features

- 📷 **Image-to-Equation** conversion.
- ⌨️ **Typed Equation and Formula** recognition.
- 💬 **Natural Language Processing** for conceptual queries.
- 🎬 **Animated step-by-step visual explanations**.
- 🔊 **Audio narration** to explain each step.
- 🌐 **Web application** for user-friendly access.

---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/RO-HIT17/vision-solve.git
cd vision-solve
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Manim
```bash
pip install manim
```

### 4. Setup Pix2Tex and Deep Learning Tools
```bash
pip install torch torchvision torchaudio
```

### 5. Install FFmpeg (Video/Audio Processing)
- [FFmpeg Downloads](https://ffmpeg.org/download.html)

---

## 📈 Example Use Cases

| Input Type                                        | Output                                          |
|--------------------------------------------------|-------------------------------------------------|
| Handwritten math/physics expression (image)      | LaTeX + animated visualization + audio guide    |
| Typed complex formula (e.g., integral, reaction) | Animated breakdown with audio explanation       |
| Natural language (e.g., "Explain this equation")| Dynamic animation with narration and LaTeX code |

---



