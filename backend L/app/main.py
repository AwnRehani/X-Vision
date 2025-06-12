# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routers import auth, predict  # removed upload since it's no longer used

app = FastAPI()

# === CORS CONFIGURATION ===
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ===========================

# Create all tables (if they don't already exist)
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "X-Vision backend is running!"}

# === ROUTERS ===
# Auth endpoints: /auth/signup, /auth/login, etc.
app.include_router(auth, prefix="/auth", tags=["Auth"])

# Prediction + LLM endpoints: POST /predict/all, etc.
app.include_router(predict, prefix="/predict", tags=["Prediction"])
# ===============

# Serve raw and annotated images under /uploads
app.mount("/uploads/raw", StaticFiles(directory="uploads/raw"), name="raw")
app.mount("/uploads",       StaticFiles(directory="uploads"),     name="uploads")
