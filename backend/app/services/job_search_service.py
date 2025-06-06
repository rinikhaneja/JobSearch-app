import os
import json
import uuid
from datetime import datetime, UTC
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv
from serpapi import GoogleSearch
from sqlalchemy.orm import Session
from app.models.job import JobsOffered
import re
import logging

logger = logging.getLogger('custom_logger')
load_dotenv()

class JobSearchService:
  
    def __init__(self):
        """Initialize the JobSearchService with API key from environment variables."""
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables")
        
    def search_jobs(self, session_id: str, job_title: str, 
                   location: str = "United States",
                   num_pages: int = 3) -> List[Dict]:
        """
        Search for jobs using SerpApi's Google Jobs API.
        
        Args:
            job_title (str): The job title to search for
            session_id (str): The session ID from the application context
            location (str): Location to search in (default: "United States")
            num_pages (int): Number of pages to fetch (default: 3)
            
        Returns:
            List[Dict]: List of job listings with standardized fields
        """
        try:
            all_jobs = []
            
            params = {
                "engine": "google_jobs",
                "q": job_title,
                "location": location,
                "api_key": self.api_key,
            }
            next_page_token = None
            
            for _ in range(num_pages):
                if next_page_token:
                    params["next_page_token"] = next_page_token
                search = GoogleSearch(params)
                results = search.get_dict()
                if "error" in results:
                    logger.error(f"SerpApi error: {results['error']}")
                    break
                
                jobs_results = results.get("jobs_results", [])
                logger.info(f"Found {len(jobs_results)} jobs in this page")
                for job in jobs_results:
                    # Extract and standardize job data
                    standardized_job = {
                        "job_id": str(uuid.uuid4()),
                        "session_id": session_id,
                        "job_title": job.get("title"),
                        "cmp_name": job.get("company_name"),
                        "city": self._extract_location(job.get("location"), "city"),
                        "state": self._extract_location(job.get("location"), "state"),
                        "country": self._extract_location(job.get("location"), "country"),
                        "description": job.get("description"),
                        "qualification_required": self._extract_qualifications(job),
                        "skills_required": self._extract_skills(job),
                        "salary_offered": job.get("salary"),
                        "posted_date": self._parse_date(job.get("posted_at")),
                        "is_active": True
                    }
                    all_jobs.append(standardized_job)
                
                next_page_token = results.get("next_page_token")
                if not next_page_token:
                    break  # No more pages
            
            return all_jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            raise ValueError(f"Failed to search jobs: {str(e)}")
    
    def _extract_location(self, location: str, part: str) -> Optional[str]:
        """Extract city, state, or country from location string."""
        if not location:
            return None
            
        parts = location.split(", ")
        if part == "city" and len(parts) > 0:
            return parts[0]
        elif part == "state" and len(parts) > 1:
            return parts[1]
        elif part == "country" and len(parts) > 2:
            return parts[2]
        return None
    
    def _extract_qualifications(self, job: Dict) -> Optional[str]:
        """Extract qualifications from job description or requirements."""
        description = job.get("description", "")
        requirements = job.get("requirements", [])
        
        if requirements:
            return "\n".join(requirements)
        return description
    
    def _extract_skills(self, job: Dict) -> list:
        """Extract skills from job description or requirements. Always returns a list."""
        description = job.get("description", "")
        requirements = job.get("requirements", [])

        # If requirements is a list of skills, return it directly
        if requirements and isinstance(requirements, list):
            return requirements

        # Try to extract skills from description using indicators
        skill_indicators = ["skills:", "required skills:", "technical skills:", "proficiency in"]
        for indicator in skill_indicators:
            if indicator in description.lower():
                parts = description.lower().split(indicator)
                if len(parts) > 1:
                    skills_text = parts[1].strip()
                    # Split on comma, semicolon, or newline
                    skills = [s.strip() for s in re.split(r'[\,\n;]', skills_text) if s.strip()]
                    return skills

        return []  # Always return a list, never None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
            
        try:
            # Handle common date formats
            formats = [
                "%Y-%m-%d",
                "%d %b %Y",
                "%b %d, %Y",
                "%d %B %Y",
                "%B %d, %Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).replace(tzinfo=UTC)
                except ValueError:
                    continue
                    
            return None
        except Exception:
            return None
    
    def save_jobs_to_db(self, jobs: List[Dict], db: Session, session_id: str) -> None:
        """
        Save job listings to the database.
        
        Args:
            jobs (List[Dict]): List of job listings
            db (Session): Database session
        """
        try:
            for job in jobs:
                db_job = JobsOffered(
                    jobid=str(uuid.uuid4()),
                    session_id=session_id,
                    job_title=job["job_title"],
                    cmp_name=job["cmp_name"],
                    city=job["city"],
                    state=job["state"],
                    country=job["country"],
                    description=job["description"],
                    qualification_required=job["qualification_required"],
                    skills_required=job["skills_required"],
                    salary_offered=job["salary_offered"],
                    posted_date=job["posted_date"],
                    is_active=job["is_active"]
                )
                db.add(db_job)
            
            db.commit()
            logger.info(f"Successfully saved {len(jobs)} jobs to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving jobs to database: {str(e)}")
            raise ValueError(f"Failed to save jobs to database: {str(e)}")


# Example usage:
# job_search = JobSearchService()
# jobs = job_search.search_jobs(
#     job_title="Software Engineer",
#     session_id="your-session-id-here"
# )
# job_search.save_jobs_to_db(jobs, db_session) 