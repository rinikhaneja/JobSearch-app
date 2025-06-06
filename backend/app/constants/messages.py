from types import SimpleNamespace

# Error messages
class ERROR_MESSAGES:
    NAME_NOT_FOUND = "Could not extract name from resume"
    EMAIL_NOT_FOUND = "Could not extract email from resume"
    RESUME_EXISTS = "Resume Already Exists"
    INVALID_OR_EXPIRED_SESSION = "Invalid or expired session"
    USER_NOT_FOUND = "User not found"
    JOB_NOT_FOUND = "Job not found"
    FAILED_TO_ANALYZE_RESUME = "Failed to analyze resume"
    FAILED_TO_UPLOAD_FILE = "Failed to upload file"

# Success messages
class SUCCESS_MESSAGES:
    RESUME_UPLOADED = "Resume uploaded successfully"
    RESUME_ANALYZED = "Resume analyzed successfully"

# Other static strings
UPLOAD_DIR_DEFAULT = "/Users/rinikhaneja/Documents/JobSearchResumes" 