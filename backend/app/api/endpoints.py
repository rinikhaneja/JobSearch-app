from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None

# Mock database
jobs_db = []

@router.get("/jobs", response_model=List[Job])
async def get_jobs():
    return jobs_db

@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int):
    job = next((job for job in jobs_db if job["id"] == job_id), None)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/jobs", response_model=Job)
async def create_job(job: Job):
    jobs_db.append(job.dict())
    return job 