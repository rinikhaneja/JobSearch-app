from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import uuid

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

class JobSearchRequest(BaseModel):
    user_id: str
    session_id: str
    job_title: Optional[str] = None
    location: str
    num_pages: int = 3

class JobResponse(BaseModel):
    job_id: str
    job_title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    requirements: Optional[List[str]] = None
    posted_date: Optional[datetime] = None
    application_url: Optional[str] = None

class JobSearchResponse(BaseModel):
    job_id: str
    job_title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    requirements: Optional[List[str]] = None
    posted_date: Optional[datetime] = None
    application_url: Optional[str] = None
    match_score: Optional[float] = None
    skills_match: Optional[List[str]] = None 