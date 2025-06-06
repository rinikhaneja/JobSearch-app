import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.job_search_service import JobSearchService
from app.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_job_search():
    try:
        # Initialize service
        job_search = JobSearchService()
        logger.info("JobSearchService initialized successfully")

        # Test search
        test_job_title = "Software Engineer"
        test_session_id = "test-session-123"
        test_location = "United States"

        logger.info(f"Searching for jobs with title: {test_job_title}")
        jobs = job_search.search_jobs(
            job_title=test_job_title,
            session_id=test_session_id,
            location=test_location,
            num_pages=1  # Just test with 1 page first
        )

        # Print results
        logger.info(f"Found {len(jobs)} jobs")
        for job in jobs:
            logger.info("\nJob Details:")
            logger.info(f"Title: {job['job_title']}")
            logger.info(f"Company: {job['cmp_name']}")
            logger.info(f"Location: {job['city']}, {job['state']}, {job['country']}")
            logger.info(f"Description: {job['description'][:200]}...")  # First 200 chars
            logger.info(f"Skills Required: {job['skills_required']}")
            logger.info("-" * 50)

        # Test database save
        logger.info("\nTesting database save...")
        db = SessionLocal()
        try:
            job_search.save_jobs_to_db(jobs, db)
            logger.info("Successfully saved jobs to database")
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_job_search() 