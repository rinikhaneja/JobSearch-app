from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.models import UserDetails, Academics, Accolades, WorkExperience, SessionIdTable
from app.database import get_db
from app.resume_parser import ResumeParser
from app.schemas import UploadResponse, AnalyzeRequest, AnalyzeResponse, ErrorResponse
from typing import List
import os
from datetime import datetime, timedelta, UTC
import uuid
import logging
from sqlalchemy.exc import IntegrityError
from app.services.resume_service import upload_resume_service, analyze_resume_service
from fastapi.responses import JSONResponse
from app.constants.messages import ERROR_MESSAGES
from dotenv import load_dotenv

logger = logging.getLogger('custom_logger')
load_dotenv()

router = APIRouter()

UPLOAD_DIR = '/Users/rinikhaneja/Documents/JobSearchResumes'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_use_llm_flag():
    return os.getenv('USE_LLM', 'False').lower() == 'true'

@router.post("/upload-resume", response_model=UploadResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    use_llm = get_use_llm_flag()
    try:
        result = upload_resume_service(file, db, use_llm)
        print(f"AAAAAResult: {result}")
        return result
    except ValueError as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return JSONResponse(status_code=400, content=ErrorResponse(detail=str(e)).model_dump())
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        db.rollback()
        return JSONResponse(status_code=500, content=ErrorResponse(detail=ERROR_MESSAGES.FAILED_TO_UPLOAD_FILE).model_dump())

@router.post("/analyze-resume", response_model=AnalyzeResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_resume(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    use_llm = get_use_llm_flag()
    try:
        result = analyze_resume_service(request, db, use_llm)
        return result
    except ValueError as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        return JSONResponse(status_code=400, content=ErrorResponse(detail=str(e)).model_dump())
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        db.rollback()
        return JSONResponse(status_code=500, content=ErrorResponse(detail=ERROR_MESSAGES.FAILED_TO_ANALYZE_RESUME).model_dump())

@router.get("/user-details/{user_id}", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_user_details(
    user_id: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    try:
        # Validate session
        session = db.query(SessionIdTable).filter(
            SessionIdTable.user_id == uuid.UUID(user_id),
            SessionIdTable.session_id == uuid.UUID(session_id),
            SessionIdTable.is_valid == True,
            SessionIdTable.expires_at > datetime.now(UTC)
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail=ERROR_MESSAGES.INVALID_OR_EXPIRED_SESSION)

        # Get user details
        user = db.query(UserDetails).filter(UserDetails.id == uuid.UUID(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail=ERROR_MESSAGES.USER_NOT_FOUND)

        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "current_job_title": user.current_job_title,
            "years_of_exp": user.years_of_exp,
            "skills": user.skills,
            "contact_no": user.contact_no
        }
    except ValueError as e:
        logger.error(f"Error fetching user details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching user details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ERROR_MESSAGES.INTERNAL_SERVER_ERROR) 