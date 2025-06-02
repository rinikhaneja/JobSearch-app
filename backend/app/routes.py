from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database
from .database import get_db
from .resume_parser import ResumeParser
import os
from datetime import datetime, timedelta
import uuid
from typing import Optional
from pydantic import BaseModel
import logging
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    filename='my_log.log', 
                    filemode='w',
                    encoding='utf-8',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('custom_logger')

app = APIRouter()

# Define upload directory
UPLOAD_DIR = '/Users/rinikhaneja/Documents/JobSearchResumes'

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Request and Response Models
class UploadResponse(BaseModel):
    filename: str
    location: str
    user_id: str
    session_id: str

class AnalyzeRequest(BaseModel):
    user_id: str
    session_id: str

class AnalyzeResponse(BaseModel):
    message: str
    user_id: str
    session_id: str
    extracted_info: dict

class ErrorResponse(BaseModel):
    detail: str

@app.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Starting file upload for: {file.filename}")
        
        # Save file to uploads directory
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        logger.info(f"File saved at: {file_location}")

        # Parse resume to get name and email
        parser = ResumeParser()
        extracted_info = parser.parse_resume(file_location)
        logger.info(f"Extracted info from resume: {extracted_info}")

        # Validate required fields
        name = extracted_info.get('name')
        email = extracted_info.get('email')
        logger.info(f"Name and email : ")

        if not name:
            raise HTTPException(status_code=400, detail="Could not extract name from resume")
        if not email:
            raise HTTPException(status_code=400, detail="Could not extract email from resume")

        # Check for duplicate email
        existing_user = db.query(models.UserDetails).filter(models.UserDetails.email == email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Resume Already Exists")

        # Create new user details with resume location, name and email
        user = models.UserDetails(
            resume_location=file_location,
            name=name,
            email=email,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        logger.info(f"User added : ")

        try:
            db.commit()
            logger.info(f"commit: ")

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Resume Already Exists")
        db.refresh(user)
        logger.info(f"after refresh user: ")
        logger.info(f"Created user with ID: {user.id}")

        # Create session for the user
        session = models.SessionIdTable(
            user_id=user.id,
            session_token=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_valid=True
        )
        db.add(session)
        db.commit()
        logger.info(f"Created session with ID: {session.session_id}")
        
        return {
            "filename": file.filename,
            "location": file_location,
            "user_id": str(user.id),
            "session_id": str(session.session_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-resume", response_model=AnalyzeResponse)
async def analyze_resume(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Starting resume analysis for user_id: {request.user_id}")
        
        # Validate session
        session = db.query(models.SessionIdTable).filter(
            models.SessionIdTable.user_id == request.user_id,
            models.SessionIdTable.session_token == request.session_id,
            models.SessionIdTable.is_valid == True,
            models.SessionIdTable.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        # Get user details
        user = db.query(models.UserDetails).filter(models.UserDetails.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Process resume and extract information
        resume_path = user.resume_location
        logger.info(f"Processing resume at: {resume_path}")
        
        # Extract information from resume
        parser = ResumeParser()
        extracted_info = parser.parse_resume(resume_path)
        logger.info(f"Extracted info from resume: {extracted_info}")
        
        # Update user details with extracted information
        user.contact_no = extracted_info.get('contact_no')
        user.current_job_title = extracted_info.get('current_job_title')
        user.years_of_exp = extracted_info.get('years_of_exp')
        user.skills = extracted_info.get('skills')
        user.parsed_date = datetime.utcnow()
        
        # Remove old related records
        db.query(models.Academics).filter(models.Academics.user_id == user.id).delete()
        db.query(models.Accolades).filter(models.Accolades.user_id == user.id).delete()
        db.query(models.WorkExperience).filter(models.WorkExperience.user_id == user.id).delete()

        # Add new Academics
        for edu in extracted_info.get('education', []):
            db.add(models.Academics(
                user_id=user.id,
                school_name=edu.get('institution'),
                degree=edu.get('degree'),
                school_year=edu.get('year'),
                school_gpa=None,  # If GPA is not parsed, set to None
                school_type=edu.get('degree_type')
            ))

        # Add new Accolades
        for acc in extracted_info.get('accolades', []):
            db.add(models.Accolades(
                user_id=user.id,
                acco_url=acc.get('url'),
                acco_start_year=acc.get('start_year'),
                acco_end_year=acc.get('end_year')
            ))

        # Add new WorkExperience
        for exp in extracted_info.get('work_experience', []):
            db.add(models.WorkExperience(
                user_id=user.id,
                company=exp.get('company'),
                position=exp.get('position'),
                joining_year=exp.get('joining_year'),
                end_year=exp.get('end_year'),
                description=exp.get('description')
            ))

        db.commit()
        logger.info(f"Updated user details for user_id: {user.id}")

        return {
            "message": "Resume analyzed successfully",
            "name": extracted_info.get('name'),
            "email": extracted_info.get('email'),
            "contact_no": extracted_info.get('contact_no'),
            "current_job_title": extracted_info.get('current_job_title'),
            "years_of_exp": extracted_info.get('years_of_exp'),
            "skills": extracted_info.get('skills'),
            "extracted_info": extracted_info
        }
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 