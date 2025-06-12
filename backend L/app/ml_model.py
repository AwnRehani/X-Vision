# app/ml_model.py
# app/ml_model.py

import os
import uuid
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.models import load_model
from ultralytics import YOLO

# ————————————————
# Model 1: Fracture classifier
# ————————————————
# Load your TensorFlow/Keras classifier once
model = load_model("models/efficientnetv2_fracture_final_best.keras")

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Convert raw image bytes into a normalized tensor for the classifier.
    """
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0
    return np.expand_dims(image_array, axis=0)

def predict_fracture(image_bytes: bytes) -> float:
    """
    Run the classifier on raw bytes and return P(fracture).
    The saved model outputs P(no‐fracture) at index [0][0], so we invert it.
    """
    input_tensor = preprocess_image(image_bytes)
    raw = model.predict(input_tensor)[0][0]  # P(no‐fracture)
    prediction = 1.0 - raw                   # P(fracture)
    print(f"🔍 raw={raw:.4f}, prediction={prediction:.4f}")
    return float(prediction)


# ————————————————
# Model 2: Bounding‐box detector (YOLO)
# ————————————————
# Load your YOLO model once
bbox_model = YOLO("models/model2.pt")

def predict_bboxes(image_bytes: bytes) -> list[list[float]]:
    """
    Given raw image bytes, save to a temp file, run YOLO detection,
    and return a list of bounding boxes [x1, y1, x2, y2] as floats.
    """
    # 1) Ensure temporary directory and write bytes
    os.makedirs("temp", exist_ok=True)
    temp_path = f"temp/{uuid.uuid4()}.png"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    # 2) Run YOLO on the temp file (confidence threshold 0.25)
    results = bbox_model(temp_path, conf=0.25)

    # 3) Extract the raw tensor of shape (N, 4)
    raw = results[0].boxes.xyxy  # torch.Tensor

    # 4) Convert to NumPy and build list of boxes
    arr = raw.cpu().numpy()  # shape: (N, 4)
    boxes = [[float(x1), float(y1), float(x2), float(y2)] for x1, y1, x2, y2 in arr]

    # 5) Delete temp file and return
    os.remove(temp_path)
    return boxes
