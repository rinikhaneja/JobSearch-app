from app.models import JobsOffered
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.constants.messages import ERROR_MESSAGES
import logging

logger = logging.getLogger('custom_logger')

# --- Pydantic Model for Mock/Example Purposes ---
class Job(BaseModel):
    """Pydantic model representing a job posting."""
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None

# Mock database (for demonstration; replace with real DB logic as needed)
jobs_db = []

def get_jobs_service(db: Session = None):
    """Retrieve all jobs from the database or mock DB."""
    logger.info("get_jobs_service called")
    try:
        # If you want to use the real DB, uncomment the next line and remove the mock logic
        # jobs = db.query(JobsOffered).all()
        # return jobs
        logger.debug(f"Returning jobs_db: {jobs_db}")
        return jobs_db
    except Exception as e:
        logger.error(f"Exception in get_jobs_service: {e}", exc_info=True)
        raise

def get_job_service(job_id: int, db: Session = None):
    """Retrieve a single job by its ID from the database or mock DB."""
    logger.info(f"get_job_service called with job_id: {job_id}")
    try:
        job = next((job for job in jobs_db if job["id"] == job_id), None)
        logger.debug(f"Job found: {job}")
        if job is None:
            logger.error("Job not found")
            raise ValueError(ERROR_MESSAGES.JOB_NOT_FOUND)
        return job
    except Exception as e:
        logger.error(f"Exception in get_job_service: {e}", exc_info=True)
        raise

def create_job_service(job: Job, db: Session = None):
    """Create a new job entry in the database or mock DB."""
    logger.info(f"create_job_service called with job: {job}")
    try:
        jobs_db.append(job.model_dump())
        logger.debug(f"Job appended to jobs_db: {job}")
        return job
    except Exception as e:
        logger.error(f"Exception in create_job_service: {e}", exc_info=True)
        raise

def get_jobs_service(db: Session):
    # Placeholder: return all jobs
    jobs = db.query(JobsOffered).all()
    return [
        {
            "jobid": str(job.jobid),
            "job_title": job.job_title,
            "cmp_name": job.cmp_name,
            "city": job.city,
            "state": job.state,
            "country": job.country,
            "description": job.description,
            "qualification_required": job.qualification_required,
            "skills_required": job.skills_required,
            "salary_offered": job.salary_offered,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "is_active": job.is_active
        }
        for job in jobs
    ] 