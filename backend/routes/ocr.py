# routes/ocr.py
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from PIL import Image
import pytesseract

ocr_router = APIRouter()

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@ocr_router.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Real OCR using pytesseract
    try:
        image = Image.open(file_path)
        ocr_text = pytesseract.image_to_string(image)
    except Exception as e:
        ocr_text = f"OCR error: {str(e)}"
    return JSONResponse({"filename": file.filename, "ocr_text": ocr_text})
