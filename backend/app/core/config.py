import os

class Settings:
    PROJECT_NAME: str = "Job Search API"
    CORS_ORIGINS = ["http://localhost:3000"]
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/Users/rinikhaneja/Documents/JobSearchResumes")

settings = Settings() 