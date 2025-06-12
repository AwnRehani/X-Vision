# backend/models/llm_groq.py


import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Optional

load_dotenv()  # ensures .env is read from project root

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_fracture_report(
    label: str,
    confidence: float,
    box: Optional[List[float]]
) -> str:
    """
    If label=="not fractured", produce a brief 'no fracture' note.
    Otherwise, include the bounding box in the detailed prompt.
    """
    if label == "not fractured":
        # Shorter prompt when no fracture
        prompt = f"""
You are a medical radiology assistant. The X-ray image analysis shows NO fracture with confidence {confidence:.4f}. 
Write a concise statement confirming no fracture detected and advise what a patient should do next (e.g., follow-up if pain persists).
"""
        messages = [
            {"role": "system", "content": "You are a medical report assistant."},
            {"role": "user", "content": prompt}
        ]
    else:
        # Existing detailed prompt when fracture is found
        # Expect that 'box' is [x1, y1, x2, y2]
        prompt = f"""
You are a medical radiology assistant. Based on the following object detection result from an X-ray image, generate a clear, professional diagnostic report:

- Fracture Label: {label}
- Detection Confidence: {confidence:.4f}
- Bounding Box: (x1={box[0]}, y1={box[1]}, x2={box[2]}, y2={box[3]})

Make sure the report includes diagnosis, potential implications, splinting/treatment guidance, and follow-up instructions.
"""
        messages = [
            {"role": "system", "content": "You are a medical report assistant."},
            {"role": "user", "content": prompt}
        ]

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return response.choices[0].message.content