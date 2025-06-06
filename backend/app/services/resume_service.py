import os
import uuid
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import UserDetails, Academics, Accolades, WorkExperience, SessionIdTable
from app.resume_parser import ResumeParser
from app.services.resume_llm_service import ResumeLLMService
from app.constants.messages import ERROR_MESSAGES, SUCCESS_MESSAGES, UPLOAD_DIR_DEFAULT
import logging
from app.models.user import map_degree_type 
from fastapi import UploadFile
from app.services.resume_llm_service import extract_text_from_file


logger = logging.getLogger('custom_logger')

UPLOAD_DIR = UPLOAD_DIR_DEFAULT
os.makedirs(UPLOAD_DIR, exist_ok=True)

def upload_resume_service(file: UploadFile, db: Session, use_llm: bool = True):
    """Handles the logic for uploading a resume, parsing it, and creating a user and session in the database."""
    logger.info(f"upload_resume_service called with file: {getattr(file, 'filename', None)}")
    try:
        # Save the file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        logger.debug(f"File written to {file_location}")

        
        if use_llm:
            # Use LLM service for parsing
            resume_text = extract_text_from_file(file_location)  # <-- Use helper for all file types
            llm_service = ResumeLLMService(api_key=os.getenv("OPENAI_API_KEY"))
            extracted_info = llm_service.extract_resume_data(resume_text)
            logger.info(f"Extracted info: {extracted_info}")
            return llm_service.save_initial_data(extracted_info, db, file_location)
        else:
            # Use traditional parser
            # Read the file content
            with open(file_location, "r", encoding='utf-8') as f:
                resume_text = f.read()
            parser = ResumeParser()
            extracted_info = parser.parse_resume(resume_text)

            # Continue with existing database operations
            logger.debug(f"Extracted info: {extracted_info}")
            name = extracted_info.get('name')
            email = extracted_info.get('email')
            if not name:
                logger.error("Name not found in resume")
                raise ValueError(ERROR_MESSAGES.NAME_NOT_FOUND)
            if not email:
                logger.error("Email not found in resume")
                raise ValueError(ERROR_MESSAGES.EMAIL_NOT_FOUND)
            existing_user = db.query(UserDetails).filter(UserDetails.email == email).first()
            logger.debug(f"Existing user: {existing_user}")
            if existing_user:
                logger.error("Resume already exists for this email")
                raise ValueError(ERROR_MESSAGES.RESUME_EXISTS)
            user = UserDetails(
                resume_location=file_location,
                name=name,
                email=email,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(user)
            try:
                db.commit()
                logger.info(f"User committed to DB: {user}")
            except IntegrityError as e:
                db.rollback()
                logger.error(f"IntegrityError during user commit: {e}")
                raise ValueError(ERROR_MESSAGES.RESUME_EXISTS)
            db.refresh(user)
            session = SessionIdTable(
                user_id=user.id,
                session_token=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=1),
                is_valid=True
            )
            db.add(session)
            db.commit()
            logger.info(f"Session committed to DB: {session}")

            return {
                "filename": file.filename,
                "location": file_location,
                "user_id": str(user.id),
                "session_id": str(session.session_id)
            }

    except Exception as e:
                logger.error(f"Exception in upload_resume_service: {e}", exc_info=True)
                raise

def analyze_resume_service(request, db: Session, use_llm: bool = True):
    logger.info(f"analyze_resume_service called with request: {request}")
    try:
        session = db.query(SessionIdTable).filter(
            SessionIdTable.user_id == uuid.UUID(request.user_id),
            SessionIdTable.session_id == uuid.UUID(request.session_id),
            SessionIdTable.is_valid == True,
            SessionIdTable.expires_at > datetime.now(UTC)
        ).first()
        logger.debug(f"Session found: {session}")
        if not session:
            logger.error("Invalid or expired session")
            raise ValueError(ERROR_MESSAGES.INVALID_OR_EXPIRED_SESSION)
        user = db.query(UserDetails).filter(UserDetails.id == uuid.UUID(request.user_id)).first()
        logger.debug(f"User found: {user}")
        if not user:
            logger.error("User not found")
            raise ValueError(ERROR_MESSAGES.USER_NOT_FOUND)
        resume_path = user.resume_location

        if use_llm:
            # Use LLM service for parsing and saving analysis data
            llm_service = ResumeLLMService(api_key=os.getenv("OPENAI_API_KEY"))
            resume_text = extract_text_from_file(resume_path)
            extracted_info = llm_service.extract_resume_data(resume_text)
            llm_service.save_analysis_data(extracted_info, db, user.id)
        else:
            # Use traditional parser and existing logic
            parser = ResumeParser()
            extracted_info = parser.parse_resume(resume_path)
            user.contact_no = extracted_info.get('phone_number')
            user.current_job_title = extracted_info.get('current_job_title')
            user.years_of_exp = extracted_info.get('years_of_experience')
            user.skills = extracted_info.get('skills')
            user.parsed_date = datetime.now(UTC)
            db.query(Academics).filter(Academics.user_id == user.id).delete()
            db.query(Accolades).filter(Accolades.user_id == user.id).delete()
            db.query(WorkExperience).filter(WorkExperience.user_id == user.id).delete()
            logger.debug("Deleted old Academics, Accolades, and WorkExperience records")
            for edu in extracted_info.get('education', []):
                db.add(Academics(
                    user_id=user.id,
                    school_name=edu.get('institution'),
                    degree=edu.get('degree'),
                    school_year=edu.get('year'),
                    school_gpa=None,
                    school_type=map_degree_type(edu.get('degree_type'))  
                ))
            for acc in extracted_info.get('accolades', []):
                db.add(Accolades(
                    user_id=user.id,
                    acco_url=acc.get('url'),
                    acco_start_year=acc.get('start_year'),
                    acco_end_year=acc.get('end_year')
                ))
            for exp in extracted_info.get('work_experience', []):
                db.add(WorkExperience(
                    user_id=user.id,
                    company=exp.get('company'),
                    position=exp.get('position'),
                    joining_year=exp.get('joining_year'),
                    end_year=exp.get('end_year'),
                    description=exp.get('description')
                ))
            db.commit()
            logger.info(f"User and related info updated and committed for user_id: {user.id}")
        return {
            "message": SUCCESS_MESSAGES.RESUME_ANALYZED,
            "user_id": str(user.id),
            "session_id": str(session.session_id),
            "extracted_info": extracted_info
        }
    except Exception as e:
        logger.error(f"Exception in analyze_resume_service: {e}", exc_info=True)
        raise 