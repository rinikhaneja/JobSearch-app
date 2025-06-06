// Shared types/interfaces for the JobSearch project

export interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
  };
  detail?: string;
  message?: string;
}

export interface UploadResponse {
  location: string;
  user_id: string;
  session_id: string;
}

export interface AnalysisResponse {
  message: string;
  extracted_info: {
    name?: string;
    email?: string;
    phone?: string;
    skills?: string[];
    experience?: string[];
    education?: string[];
  };
}

export interface Job {
  job_id: string;
  job_title: string;
  cmp_name: string;
  city: string;
  state: string;
  country: string;
  description: string;
  qualification_required: string;
  skills_required: string[];
  salary_offered?: string;
  posted_date?: string;
}

export interface Match {
  job: string;
  match: string;
}

export interface UploadResults {
  message: string;
  path?: string;
  size?: string;
  type?: string;
  user_id: string;
  session_id: string;
}

export type Results = 
  | UploadResults
  | { message: string; extracted_info: AnalysisResponse['extracted_info'] }
  | Job[]
  | Match[]; 