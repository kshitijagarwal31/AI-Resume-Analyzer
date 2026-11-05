from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Resume, User
from app.schemas import ResumeOut

from app.services.parser import extract_text_from_pdf


router = APIRouter(prefix="/resumes", tags=["resumes"])

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf"}
MAX_SIZE = 5 * 1024 * 1024


@router.post("/upload", response_model=ResumeOut, status_code=201)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    original_name = (file.filename or "resume")[:255]
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = file.file.read(MAX_SIZE + 1)
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB)")

    UPLOAD_DIR.mkdir(exist_ok=True)
    file_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    file_path.write_bytes(content)
    try:
        text = extract_text_from_pdf(str(file_path))
    except Exception:
        text = ""

    resume = Resume(
        user_id = current_user.id,
        filename =  original_name,
        file_path = str(file_path),
        extracted_text =  text or None,
        status = "text_extracted" if text else "failed"
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume