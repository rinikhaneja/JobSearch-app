from typing import List, Dict, Any
import uuid
import re

class JobLLMService:
    @staticmethod
    def _extract_requirements_list(requirements_text: str) -> List[str]:
        """Extract requirements as a list from text."""
        if not requirements_text:
            return []
        
        # Split on common delimiters and clean up
        requirements = []
        # Split on bullet points, numbers, or newlines
        raw_requirements = re.split(r'[\n•]|\d+\.', requirements_text)
        
        for req in raw_requirements:
            req = req.strip()
            if req and len(req) > 5:  # Only include non-empty requirements with reasonable length
                requirements.append(req)
        
        return requirements

    @staticmethod
    def map_serpapi_to_ui_schema(serpapi_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        mapped_jobs = []
        for job in serpapi_jobs:
            # Compose location string
            city = job.get("city") or ""
            state = job.get("state") or ""
            country = job.get("country") or ""
            location = ", ".join([x for x in [city, state, country] if x])

            # Ensure job_id is present
            job_id = job.get("jobid") or job.get("job_id") or str(uuid.uuid4())

            # Extract requirements as a list
            requirements_text = job.get("qualification_required") or job.get("description") or ""
            requirements = JobLLMService._extract_requirements_list(requirements_text)

            mapped_job = {
                "job_id": job_id,
                "job_title": job.get("job_title") or job.get("title"),
                "company": job.get("cmp_name") or job.get("company_name"),
                "location": location,
                "description": job.get("description"),
                "salary": job.get("salary_offered"),
                "requirements": requirements,  # Now a list
                "posted_date": job.get("posted_date"),
                "application_url": job.get("application_url"),
                "match_score": None,  # Optional field
                "skills_match": job.get("skills_required") if isinstance(job.get("skills_required"), list) else []
            }
            mapped_jobs.append(mapped_job)
        return mapped_jobs
