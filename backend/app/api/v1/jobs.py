from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.job_service import get_jobs_service, get_job_service, create_job_service, Job
from app.schemas import ErrorResponse
from fastapi.responses import JSONResponse
from app.constants.messages import ERROR_MESSAGES
from app.services.job_search_service import JobSearchService
from app.models import SessionIdTable, UserDetails
from datetime import datetime, UTC
import uuid
import logging
from app.schemas.resume import JobSearchRequest, JobResponse, JobSearchResponse
from app.services.job_llm_service import JobLLMService
logger = logging.getLogger('custom_logger')
router = APIRouter()

# --- Pydantic Model for Mock/Example Purposes ---
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None

# Mock database (for demonstration; replace with real DB logic as needed)
jobs_db = []

@router.get("/jobs", response_model=List[Job], responses={500: {"model": ErrorResponse}})
def get_jobs(db: Session = Depends(get_db)):
    try:
        return get_jobs_service(db)
    except Exception as e:
        return JSONResponse(status_code=500, content=ErrorResponse(detail=str(e)).model_dump())

@router.get("/jobs/{job_id}", response_model=Job, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def get_job(job_id: int, db: Session = Depends(get_db)):
    try:
        return get_job_service(job_id, db)
    except ValueError as e:
        return JSONResponse(status_code=404, content=ErrorResponse(detail=str(e)).model_dump())
    except Exception as e:
        return JSONResponse(status_code=500, content=ErrorResponse(detail=str(e)).model_dump())

@router.post("/jobs", response_model=Job, responses={500: {"model": ErrorResponse}})
def create_job(job: Job, db: Session = Depends(get_db)):
    try:
        return create_job_service(job, db)
    except Exception as e:
        return JSONResponse(status_code=500, content=ErrorResponse(detail=str(e)).model_dump())

@router.post("/search-jobs", response_model=List[JobSearchResponse], responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def search_jobs(
    request: JobSearchRequest,
    db: Session = Depends(get_db)
):
    try:
        # Validate session and get user details
        session = db.query(SessionIdTable).filter(
            SessionIdTable.user_id == uuid.UUID(request.user_id),
            SessionIdTable.session_id == uuid.UUID(request.session_id),
            SessionIdTable.is_valid == True,
            SessionIdTable.expires_at > datetime.now(UTC)
        ).first()
        
        if not session:
            raise HTTPException(status_code=400, detail="Invalid or expired session")

        # Get user details to check current job title
        user = db.query(UserDetails).filter(UserDetails.id == uuid.UUID(request.user_id)).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # Use user's current job title if available, otherwise use the job title from request
        job_title = user.current_job_title if user.current_job_title else request.job_title
        if not job_title:
            raise HTTPException(status_code=400, detail="No job title available. Please enter a job title to search.")

        logger.info(f"Job title: {job_title}")
        logger.info(f"Session ID: {request.session_id}")
        logger.info(f"Location: {request.location}")
        logger.info(f"Number of pages: {request.num_pages}")

        # Initialize job search service
        job_search = JobSearchService()
        
        # Search for jobs
        jobs_results = job_search.search_jobs(
            request.session_id,
            job_title,
            request.location,
            request.num_pages
        )

        job_search.save_jobs_to_db(jobs_results, db, request.session_id) 

        for job in jobs_results:
            logger.info(f"Job ID: {job.get('job_id')}")
        ui_jobs = JobLLMService.map_serpapi_to_ui_schema(jobs_results)

        return ui_jobs

    except ValueError as e:
        logger.error(f"Error searching jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to search jobs") 