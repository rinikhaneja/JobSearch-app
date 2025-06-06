/**
 * Centralized error messages for consistent error handling and display.
 */
export class ERROR_MESSAGES {
  static NAME_NOT_FOUND = "Could not extract name from resume";
  static EMAIL_NOT_FOUND = "Could not extract email from resume";
  static RESUME_EXISTS = "Resume Already Exists";
  static INVALID_OR_EXPIRED_SESSION = "Invalid or expired session";
  static USER_NOT_FOUND = "User not found";
  static JOB_NOT_FOUND = "Job not found";
  static FAILED_TO_ANALYZE_RESUME = "Failed to analyze resume";
  static FAILED_TO_UPLOAD_FILE = "Failed to upload file";
  static UPLOAD_FIRST = "Please upload a resume first.";
  static UPLOAD_ERROR = "Failed to upload resume.";
  static ANALYSIS_ERROR = "Failed to analyze resume.";
  static JOB_SEARCH_ERROR = "Failed to search jobs.";
  static JOB_MATCH_ERROR = "Failed to match jobs.";
}

/**
 * Centralized success messages for consistent user feedback.
 */
export class SUCCESS_MESSAGES {
  static UPLOAD_SUCCESS = (filename: string): string => `Resume ${filename} uploaded successfully!`;
  static ANALYSIS_SUCCESS = "Resume analyzed successfully!";
  static JOB_SEARCH_SUCCESS = "Jobs found successfully!";
  static JOB_MATCH_SUCCESS = "Jobs matched successfully!";
}

// UI labels and other static strings
export const UPLOAD_LABEL = "Upload Resume";
export const ANALYZE_LABEL = "Analyze Resume";
export const JOB_SEARCH_LABEL = "Job Search";
export const MATCH_JOBS_LABEL = "Match Jobs";
export const SUPPORTED_FORMATS = "Supported formats: PDF (.pdf), Word (.doc, .docx)"; 