# Job Search Platform

A modern web application that leverages AI (LLM/NLP) to revolutionize the job search process. The platform parses resumes, analyzes job descriptions, and intelligently matches candidates to jobs using advanced AI and NLP techniques.

## Features
- **Resume Parsing & Analysis:** Uses OpenAI GPT-3.5 for extracting structured data from resumes (PDF, DOCX, TXT)
- **Job Search Integration:** Fetches job listings from SerpApi (Google Jobs)
- **Intelligent Matching:** Matches users to jobs based on skills, requirements, and experience
- **Session Management:** Secure user sessions for resume uploads and job search
- **Comprehensive Database:** Stores users, resumes, jobs, and matches in PostgreSQL
- **Modern Stack:** FastAPI backend, React frontend, SQLAlchemy ORM

## Architecture
- **Backend:** Python FastAPI
- **Frontend:** React
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **AI/ML:** OpenAI GPT-3.5
- **Job Search:** SerpApi

## Database Schema (ER Diagram)

```mermaid
erDiagram
    UserDetails ||--o{ Academics : has
    UserDetails ||--o{ WorkExperience : has
    UserDetails ||--o{ Accolades : has
    UserDetails ||--o{ SessionIdTable : has
    UserDetails ||--o{ MatchedJobs : has
    JobsOffered ||--o{ MatchedJobs : has
    SessionIdTable ||--o{ JobsOffered : has
```

## LLM & NLP Usage
- **Resume Parsing:** Extracts name, email, skills, education, and work experience using GPT-3.5
- **Job Parsing:** Extracts requirements, skills, and other fields from job descriptions
- **Matching:** Compares parsed resume data to job requirements for intelligent recommendations

## Example JSON Objects

**Resume Example:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "skills": ["Python", "JavaScript", "SQL"],
  "work_experience": [
    {
      "company": "Google",
      "title": "Software Engineer",
      "start_year": 2018,
      "end_year": 2022
    }
  ]
}
```

**Job Example:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_title": "Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA, USA",
  "description": "Develop and maintain software applications...",
  "requirements": ["Python", "Machine Learning", "5+ years experience"]
}
```

## Best Practices
- Comprehensive error handling and logging
- Strict schema validation for LLM outputs
- Clear code organization and type hints
- Detailed documentation and comments

## Future Improvements
- Enhanced job matching algorithms
- Multi-language support
- Skill normalization and taxonomy
- Real-time job market analysis
- Personalized AI-powered recommendations

## Full Documentation
For a detailed explanation of the project, architecture, code examples, and diagrams, please see the [GitHub Wiki](./wiki/Home).

---

## References
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [SerpApi Documentation](https://serpapi.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/rinikhaneja/JobSearch-app.git
   cd JobSearch-app
   ```

2. **Set Up the Backend:**
   - Create a virtual environment and activate it:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
     ```
   - Install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Create a `.env` file in the backend directory with your database credentials:
     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/database_name
     ```
   - Run the backend server:
     ```bash
     uvicorn main:app --reload
     ```

3. **Set Up the Frontend:**
   - Navigate to the frontend directory:
     ```bash
     cd frontend
     ```
   - Install the required dependencies:
     ```bash
     npm install
     ```
   - Start the frontend development server:
     ```bash
     npm start
     ```

## Usage

- Open your browser and go to `http://localhost:3000` to access the application.
- Use the buttons on the UI to upload your resume, analyze it, search for jobs, and match jobs.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. 