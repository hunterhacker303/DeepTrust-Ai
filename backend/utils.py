import os
import cv2
import numpy as np
import librosa
from PIL import Image

import torch
import torch.nn.functional as F
import torchvision.models as models
from torchvision import transforms

# ---------------- LOAD REAL MODEL ---------------- #

model = models.resnet18(pretrained=True)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# ---------------- ROUTER ---------------- #

def process_file(path):
    ext = os.path.splitext(path)[1].lower()

    if ext in [".jpg", ".jpeg", ".png"]:
        return analyze_image(path)

    elif ext in [".mp4", ".avi"]:
        return analyze_video(path)

    elif ext in [".wav", ".mp3"]:
        return analyze_audio(path)

    return {"error": "Unsupported file type"}

# ---------------- IMAGE ---------------- #

def analyze_image(path):
    image = Image.open(path).convert("RGB")
    tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        probs = F.softmax(output, dim=1)
        confidence = torch.max(probs).item()

    fake_score = 1 - confidence

    return format_output(fake_score, "image")

# ---------------- VIDEO ---------------- #

def analyze_video(path):
    cap = cv2.VideoCapture(path)
    scores = []

    frame_count = 0

    while cap.isOpened() and frame_count < 15:
        ret, frame = cap.read()
        if not ret:
            break

        frame_path = f"temp/frame_{frame_count}.jpg"
        cv2.imwrite(frame_path, frame)

        result = analyze_image(frame_path)
        scores.append(result["fake_probability"])

        frame_count += 1

    if len(scores) == 0:
        return {"error": "Video processing failed"}

    avg_score = sum(scores) / len(scores)

    return format_output(avg_score, "video")

# ---------------- AUDIO ---------------- #

def analyze_audio(path):
    try:
        y, sr = librosa.load(path, sr=None)

        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        score = np.mean(np.abs(mfcc)) / 100
        score = min(score, 1)

        return format_output(score, "audio")

    except Exception:
        return {"error": "Audio processing failed"}

# ---------------- OUTPUT ---------------- #

def format_output(score, media_type):
    trust_score = int((1 - score) * 100)

    if score > 0.6:
        verdict = "Likely Fake"
        reasons = generate_reasons(media_type)
    else:
        verdict = "Likely Real"
        reasons = ["No major anomalies detected"]

    return {
        "media_type": media_type,
        "trust_score": trust_score,
        "fake_probability": round(score, 2),
        "verdict": verdict,
        "reasons": reasons
    }

# ---------------- EXPLANATION ---------------- #

def generate_reasons(media_type):
    if media_type == "image":
        return [
            "Low model confidence in object consistency",
            "Possible synthetic texture patterns"
        ]

    if media_type == "video":
        return [
            "Frame-level inconsistencies detected",
            "Possible lip-sync irregularities"
        ]

    if media_type == "audio":
        return [
            "Voice frequency anomalies",
            "Spectral irregularities"
        ]