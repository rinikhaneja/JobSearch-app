import openai
import json
from dotenv import load_dotenv
load_dotenv()
import os
import logging
from sqlalchemy.orm import Session
from app.models import UserDetails, Academics, Accolades, WorkExperience, SessionIdTable
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from datetime import datetime, UTC
import uuid
from app.schemas.resume_schema import RESUME_SCHEMA, get_schema_prompt
from jsonschema import validate, ValidationError
import pdfplumber
from docx import Document
from app.constants.messages import ERROR_MESSAGES

logger = logging.getLogger('custom_logger')
api_key = os.getenv("OPENAI_API_KEY")

class ResumeLLMService:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        openai.api_key = api_key
        self.model = model

    def _calculate_total_experience(self, work_experience):
        """
        work_experience: list of dicts with 'start_date' and 'end_date' (strings like 'Jul 2018', 'Present', or None)
        Returns: total experience as 'X.Y' (years.months)
        """
        from datetime import datetime
        def parse_date(date_str):
            if not date_str or str(date_str).strip().lower() == "present":
                return datetime.now()
            try:
                return datetime.strptime(date_str.strip(), "%b %Y")
            except Exception:
                return None
        def merge_periods(periods):
            if not periods:
                return []
            periods.sort(key=lambda x: x[0])
            merged = [periods[0]]
            for current in periods[1:]:
                last = merged[-1]
                if current[0] <= last[1]:
                    merged[-1] = (last[0], max(last[1], current[1]))
                else:
                    merged.append(current)
            return merged
        periods = []
        for exp in work_experience:
            start = exp.get('start_date') or exp.get('start_year')
            end = exp.get('end_date') or exp.get('end_year')
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date and end_date >= start_date:
                periods.append((start_date, end_date))
        merged = merge_periods(periods)
        total_months = sum((p[1].year - p[0].year) * 12 + (p[1].month - p[0].month) + 1 for p in merged)
        years = total_months // 12
        months = total_months % 12
        return float(f"{years}.{months}")

    def extract_resume_data(self, resume_text: str) -> dict:
        prompt = (
            "Extract information from the resume below and return it as a JSON object that strictly follows this schema:\n"
            f"{get_schema_prompt()}\n\n"
            "Rules:\n"
            "1. Email must be a valid email format\n"
            "2. Phone number should be in a standard format\n\n"
            "3. In work experience make sure if end_year is not present or \"Present\" take the current year as end_year\n "
            "4. For years_of_exp pick the duration of work experience from the start_year and end_year and return it in years\n"
            "5. If while reading the resume you find sentences like years of experience directly use it as years_of_exp\n"
            "6. Calculate years_of_experience from code added under validate against schema use the work_experience.start_year and work_experience.end_year from all work experience entries\n"
            "7 education.year and work_experience.start_year/end_year must be integers\n"
            "8. If education degree, school, or year are missing from the resume, you can skip them or use null.\n"
            "9. skills must be an array of strings\n"
            "10. Return only valid JSON, no additional text\n"
            "11. No additional properties should be included\n"
            "12. If the resume is not in English, translate it to English and then extract the data\n"
            "13. Return only valid JSON, with property names and string values in double quotes.\n"
            "14. Do not include any extra text, markdown, or explanations.\n"
            "15. Do not wrap the JSON in triple backticks or any other formatting.\n"
            "16. Do not include trailing commas or comments.\n"
    "17. If a field is missing, use null or an empty array as appropriate.\n"
            f"Resume:\n{resume_text}\n\n"
            "JSON:"
        )
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert resume parser. Always return valid JSON that strictly follows the provided schema."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.1,
        )
        content = response.choices[0].message['content'].strip()
        logger.error(f"Raw LLM output: {content}")
        try:
            # Clean up the response content
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            if content.count('{') > 0 and content.count('}') > 0:
                content = content[content.find('{'):content.rfind('}')+1]
            # Parse JSON
            parsed_json = json.loads(content)
            
            # Validate against schema
            try:
                validate(instance=parsed_json, schema=RESUME_SCHEMA)
            except ValidationError as e:
                logger.error(f"Schema validation error: {str(e)}")
                raise ValueError(f"Invalid resume data format: {str(e)}")

            # Additional validation for specific fields
            if not isinstance(parsed_json["skills"], list) or not all(isinstance(s, str) for s in parsed_json["skills"]):
                raise ValueError("Skills must be an array of strings")

            # Validate education entries
            for edu in parsed_json["education"]:
                year = edu.get("year")
                if year is not None:
                    if not isinstance(year, int):
                        raise ValueError("Education year must be an integer or null")
                    if year < 1900 or year > datetime.now().year:
                        raise ValueError(f"Invalid education year: {year}")

            # Validate work experience entries
            for exp in parsed_json["work_experience"]:
                if not isinstance(exp["start_year"], int):
                    raise ValueError("Work experience start_year must be an integer")
                if exp["start_year"] < 1900 or exp["start_year"] > datetime.now().year:
                    raise ValueError(f"Invalid work experience start year: {exp['start_year']}")
                if "end_year" in exp and exp["end_year"] is not None:
                    if not isinstance(exp["end_year"], int):
                        raise ValueError("Work experience end_year must be an integer or null")
                    if exp["end_year"] < exp["start_year"]:
                        raise ValueError(f"Work experience end year ({exp['end_year']}) cannot be before start year ({exp['start_year']})")
                    if exp["end_year"] > datetime.now().year:
                        raise ValueError(f"Invalid work experience end year: {exp['end_year']}")

            # Calculate years_of_experience
            # Try to use start_date/end_date if present, else start_year/end_year
            durations = []
            for exp in parsed_json["work_experience"]:
                start = exp.get('start_date') or exp.get('start_year')
                end = exp.get('end_date') or exp.get('end_year')
                durations.append((str(start), str(end)))
            parsed_json["years_of_experience"] = self._calculate_total_experience([
                {"start_date": d[0], "end_date": d[1]} for d in durations
            ])
            logger.info("Extracted Resume Data:")
            logger.info(json.dumps(parsed_json, indent=2))
            return parsed_json

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
        except Exception as e:
            logger.error(f"Error processing resume data: {e}\nResponse: {content}")
            raise ValueError(f"Error processing resume data: {e}")

    def save_initial_data(self, data: dict, db: Session, resume_location: str) -> UserDetails:
        """
        Save initial resume data (basic info) during upload.
        Matches the initial save in resume_service.py
        """
        try:
            name = data.get('name')
            email = data.get('email')
            if not name or not email:
                raise ValueError("Name and email are required")
    
            existing_user = db.query(UserDetails).filter(UserDetails.email == email).first()
            if existing_user:
                logger.error("Resume already exists for this email")
                raise ValueError(ERROR_MESSAGES.RESUME_EXISTS)
            user = UserDetails(
                id=uuid.uuid4(),
                name=name,
                email=email,
                resume_location=resume_location,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(user)
            try:
                db.commit()
                logger.info(f"User committed to DB: {user}")
            except IntegrityError as e:
                db.rollback()
                logger.error(f"IntegrityError during user commit: {e}")
            db.refresh(user)
            session = SessionIdTable(
                user_id=user.id,
                session_token=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=1),
                is_valid=True
            )
            db.add(session)
            db.commit()
            logger.info(f"Session committed to DB: {session}")            
            logger.info(f"User committed to DB: {user}")
            print(f"resume location: {user.resume_location}")
            print(f"filename: {resume_location.split('/')[-1]}")
            print(f"user id: {user.id}")
            print(f"session id: {session.session_id}")
            return {
                "filename": resume_location.split("/")[-1],
                "location": resume_location,
                "user_id": str(user.id),
                "session_id": str(session.session_id)
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save initial resume data: {str(e)}")
            raise ValueError(f"Failed to save resume: {str(e)}")

    def save_analysis_data(self, data: dict, db: Session, user_id: uuid.UUID) -> None:
        """
        Save detailed resume data during analysis.
        Matches the analysis step in resume_service.py
        """
        try:
            user = db.query(UserDetails).filter(UserDetails.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            # Update basic user info
            user.contact_no = data.get('phone')
            user.current_job_title = data.get('work_experience', [{}])[0].get('title') if data.get('work_experience') else None
            user.years_of_exp = data.get('years_of_experience')
            user.skills = data.get('skills', [])
            user.parsed_date = datetime.now(UTC)

            # Clear existing related records
            db.query(Academics).filter(Academics.user_id == user.id).delete()
            db.query(Accolades).filter(Accolades.user_id == user.id).delete()
            db.query(WorkExperience).filter(WorkExperience.user_id == user.id).delete()

            # Add education records
            for edu in data.get('education', []):
                academic = Academics(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    school_name=edu.get('school', ''),
                    degree=edu.get('degree', ''),
                    school_year=edu.get('year'),
                    school_type=self._map_degree_type(edu.get('degree', '').lower())
                )
                db.add(academic)

            # Add work experience records
            for exp in data.get('work_experience', []):
                work = WorkExperience(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    company=exp.get('company', ''),
                    position=exp.get('title', ''),
                    joining_year=exp.get('start_year'),
                    end_year=exp.get('end_year'),
                    description=exp.get('description', '')
                )
                db.add(work)

            db.commit()
            logger.info(f"Analysis data saved for user_id: {user_id}")

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save analysis data: {str(e)}")
            raise

    def _map_degree_type(self, degree: str) -> str:
        """Map degree type to database enum values"""
        if any(x in degree for x in ["bachelor", "undergraduate", "bsc", "bachelors"]):
            return "under_grad"
        elif any(x in degree for x in ["master", "graduate", "msc", "masters"]):
            return "grad"
        elif any(x in degree for x in ["post_grad", "postgraduate"]):
            return "post_grad"
        elif any(x in degree for x in ["phd", "doctoral", "doctorate"]):
            return "phd"
        return "under_grad"  # default

    def ask_question(self, resume_text: str, question: str) -> str:
        """
        Ask a question about the resume and get an answer from the LLM.
        :param resume_text: The full text of the resume.
        :param question: The question to ask about the resume.
        :return: The LLM's answer as a string.
        """
        prompt = (
            f"Here is a resume:\n\n{resume_text}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert resume assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=256,
            temperature=0.2,
        )
        return response.choices[0].message['content'].strip()

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif ext in [".docx"]:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:  # fallback for .txt
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

# Example usage:
# llm = ResumeLLMService(api_key=api_key)
# resume_path = "path_to_your_resume.pdf"
# resume_text = extract_text_from_file(resume_path)
# data = llm.extract_resume_data(resume_text)
# # Now, data['name'], data['email'], data['education'], etc. can be stored in your DB 