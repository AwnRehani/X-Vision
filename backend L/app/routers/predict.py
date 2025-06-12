# app/routers/predict.py

import os
import uuid
import traceback
import sys
from io import BytesIO
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw

from app.schemas import PredictOutWithReport
from app.ml_model import predict_fracture, predict_bboxes
from models.llm_groq import generate_fracture_report
from app.token import get_current_user
from app import models, database

# Removed the prefix here so that main.py’s prefix="/predict" maps to /predict/all
router = APIRouter(tags=["Prediction"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/all", response_model=PredictOutWithReport)
async def predict_all_route(
    request: Request,
    xray_file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
   
    try:
        # 1) Read raw bytes from the uploaded file
        image_bytes = await xray_file.read()

        # 2) Model 1: fracture classifier returns probability
        prob = predict_fracture(image_bytes)
        fractured = (prob < 0.5)
        label = "fractured" if fractured else "not fractured"

        # 3) Model 2: bounding‐box detection (only if fractured)
        boxes: List[List[float]] = predict_bboxes(image_bytes) if fractured else []

        # 4) Annotate image if boxes are present
        ann_fname: Optional[str] = None
        if fractured and boxes:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            draw = ImageDraw.Draw(img)
            for x1, y1, x2, y2 in boxes:
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

            os.makedirs("uploads/annotated", exist_ok=True)
            ann_fname = f"{uuid.uuid4()}.png"
            img.save(os.path.join("uploads/annotated", ann_fname))

        # 5) Save the raw image under uploads/raw
        os.makedirs("uploads/raw", exist_ok=True)
        raw_fname = f"{uuid.uuid4()}.png"
        raw_path = os.path.join("uploads/raw", raw_fname)
        with open(raw_path, "wb") as f:
            f.write(image_bytes)

        # 6) Persist the prediction record in the database
        record = models.Prediction(
            user_id=user_id,
            image_filename=raw_fname,
            prediction_result=label,
            confidence_score=prob,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # 7) Build the annotated image URL (if an annotation was created)
        annotated_url: Optional[str] = None
        if ann_fname:
            annotated_url = f"{request.base_url}uploads/annotated/{ann_fname}"

        # 8) Model 3: generate a report via LLM (or fallback message)
        if fractured:
            if boxes:
                first_box = boxes[0]
                report_text: str = generate_fracture_report(
                    label=label,
                    confidence=round(prob, 4),
                    box=first_box
                )
            else:
                report_text = "A fracture was detected, but bounding box could not be located."
        else:
            report_text = "No fracture was detected."

        # 9) Return the combined result
        return {
            "label": label,
            "confidence": round(prob, 4),
            "boxes": boxes,
            "annotated_image_url": annotated_url,
            "report": report_text,
        }

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
