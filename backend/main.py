import os
import threading

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from predict import Predictor

predictor: Predictor | None = None
model_ready = threading.Event()


def _load_model():
    global predictor
    predictor = Predictor()
    model_ready.set()


app = FastAPI(title="Satellite Image Geolocation Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    thread = threading.Thread(target=_load_model, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_ready.is_set()}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not model_ready.is_set():
        raise HTTPException(status_code=503, detail="Model is still loading, please try again shortly")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    result = predictor.predict(image)
    return result
