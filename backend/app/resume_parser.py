import os
from typing import Dict, List, Optional
import docx
from PyPDF2 import PdfReader
import spacy
import magic
from datetime import datetime
import re
import logging
from dateutil import parser as date_parser

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger('custom_logger')

class ResumeParser:
    """
    Parses resume files (PDF, DOCX) to extract structured information such as name, contact info, skills, experience, education, and accolades.
    Usage: Instantiate and call parse_resume(file_path) to get extracted data as a dictionary.
    """
    def __init__(self):
        logger.info('ResumeParser instantiated')
        self.nlp = spacy.load("en_core_web_sm")
        logger.debug('spaCy model loaded')
        
    def extract_text_from_file(self, file_path: str) -> str:
        logger.info(f'extract_text_from_file called with file_path: {file_path}')
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        logger.debug(f'Detected file type: {file_type}')
        if file_type == "application/pdf":
            text = self._extract_from_pdf(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = self._extract_from_docx(file_path)
        else:
            logger.error(f'Unsupported file type: {file_type}')
            raise ValueError(f"Unsupported file type: {file_type}")
        logger.debug(f'Extracted text (first 500 chars): {text[:500]}')
        return text

    def _extract_from_pdf(self, file_path: str) -> str:
        logger.info(f'_extract_from_pdf called with file_path: {file_path}')
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                logger.debug(f'Extracted page text (first 200 chars): {page_text[:200] if page_text else "None"}')
                text += page_text
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        logger.info(f'_extract_from_docx called with file_path: {file_path}')
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            logger.debug(f'Extracted paragraph: {paragraph.text[:200]}')
            text += paragraph.text + "\n"
        return text

    def parse_resume(self, file_path: str) -> Dict:
        logger.info(f'parse_resume called with file_path: {file_path}')
        text = self.extract_text_from_file(file_path)
        doc = self.nlp(text)
        logger.debug('spaCy doc created')
        result = {
            "name": self._extract_name(doc),
            "phone_number": self._extract_phone(text),
            "email": self._extract_email(text),
            "current_job_title": self._extract_current_job_title(doc),
            "years_of_experience": self._calculate_years_of_experience(doc),
            "skills": self._extract_skills(doc),
            "work_experience": self._extract_experience(doc),
            "education": self._extract_education(doc),
            "accolades": self._extract_accolades(doc)
        }
        logger.info(f'Parsed resume result: {result}')
        return result

    def _extract_name(self, doc) -> Optional[str]:
        """Extract name using NER and additional heuristics."""
        # First try using NER
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Skip if the name is too short (likely not a real name)
                if len(ent.text.split()) >= 2:
                    return ent.text
        
        # If NER fails, try to find name in first few sentences
        # Usually name appears at the top of the resume
        first_sentences = list(doc.sents)[:3]  # Check first 3 sentences
        for sent in first_sentences:
            # Look for patterns like "Name: John Doe" or "John Doe" at start of line
            text = sent.text.strip()
            if ":" in text:
                parts = text.split(":", 1)
                if len(parts) == 2 and any(keyword in parts[0].lower() for keyword in ["name", "full name"]):
                    name = parts[1].strip()
                    if len(name.split()) >= 2:  # Ensure it's a full name
                        return name
            elif len(text.split()) >= 2 and len(text.split()) <= 4:  # If it's a short phrase, it might be a name
                return text
        
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address using regex and additional heuristics."""
        print(f"DEBUG: Attempting to extract email from text:\n{text[:500]}...")  # Print first 500 chars

        # Try to find email with potential spaces anywhere in the address
        email_with_spaces = re.search(
            r'([A-Za-z0-9._%+-]+)\s*@\s*([A-Za-z0-9.\s-]+)', text
        )
        if email_with_spaces:
            username = email_with_spaces.group(1).replace(" ", "")
            domain = email_with_spaces.group(2).replace(" ", "")
            email = f"{username}@{domain}"
            print(f"DEBUG: Found email with spaces: {email}")
            return email

        # Standard email pattern (remove spaces from the text first)
        text_no_spaces = text.replace(" ", "")
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        match = re.search(email_pattern, text_no_spaces)
        if match:
            print(f"DEBUG: Found email using standard pattern: {match.group(0)}")
            return match.group(0)

        # Try keyword-based patterns (as in your code)
        email_keywords = ["email", "e-mail", "mail", "contact"]
        for keyword in email_keywords:
            patterns = [
                f"{keyword}[:\\s]+([A-Za-z0-9._%+-]+)\\s*@\\s*([A-Za-z0-9.-]+(?:\\s*\\.\\s*[A-Za-z0-9.-]+)*)",
                f"{keyword}[\\s]*[=]+[\\s]*([A-Za-z0-9._%+-]+)\\s*@\\s*([A-Za-z0-9.-]+(?:\\s*\\.\\s*[A-Za-z0-9.-]+)*)",
                f"{keyword}[\\s]*[-]+[\\s]*([A-Za-z0-9._%+-]+)\\s*@\\s*([A-Za-z0-9.-]+(?:\\s*\\.\\s*[A-Za-z0-9.-]+)*)"
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    username = match.group(1).replace(" ", "")
                    domain = match.group(2).replace(" ", "")
                    email = f"{username}@{domain}"
                    print(f"DEBUG: Found email using pattern '{pattern}': {email}")
                    return email

        # Try to find email in contact information section
        contact_section = re.search(
            r'(?:contact|contact information|contact details)[^@]*?([A-Za-z0-9._%+-]+)\s*@\s*([A-Za-z0-9.-]+(?:\s*\.\s*[A-Za-z0-9.-]+)*)',
            text, re.IGNORECASE
        )
        if contact_section:
            username = contact_section.group(1).replace(" ", "")
            domain = contact_section.group(2).replace(" ", "")
            email = f"{username}@{domain}"
            print(f"DEBUG: Found email in contact section: {email}")
            return email

        print("DEBUG: No email found in text")
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number."""
        # List of keywords to look for before the phone number
        phone_keywords = [
            "phone", "phone no", "phone number", "mobile", "mobile no", "mobile number",
            "cell", "cell no", "cell number", "tel", "tel no", "telephone", "telephone no",
            "contact", "contact no", "reach me at", "call", "📞", "📱"
        ]
        # Build a regex pattern to match keywords followed by a phone number
        keyword_pattern = r'(' + '|'.join([re.escape(k) for k in phone_keywords]) + r')[\s:]*([+\d][\d\s\-().]{7,})'
        match = re.search(keyword_pattern, text, re.IGNORECASE)
        if match:
            # Clean up the phone number (remove spaces, dashes, parentheses, etc.)
            phone = re.sub(r'[^+\d]', '', match.group(2))
            return phone
        # Fallback: generic phone number pattern (allowing spaces, dashes, parentheses)
        phone_pattern = r'(\+?\d{1,3}[\s\-]?)?(\(?\d{2,4}\)?[\s\-]?)?\d{2,4}[\s\-]?\d{2,4}[\s\-]?\d{2,4}'
        match = re.search(phone_pattern, text)
        if match:
            phone = re.sub(r'[^+\d]', '', match.group(0))
            return phone
        return None
    

    def _calculate_years_of_experience(self, doc) -> float:
        """Calculate total years of experience from text and experience sections."""
        text = doc.text

        # Step 1: Regex for "X years of experience"
        text_lower = text.lower()
        patterns = [
            r'(\d+(?:\.\d+)?)(\s*\+)?\s*years? of experience',
            r'(\d+(?:\.\d+)?)(\s*\+)?\s*yrs? of experience',
            r'(\d+(?:\.\d+)?)(\s*\+)?\s*years? experience',
            r'(\d+(?:\.\d+)?)(\s*\+)?\s*yrs? experience'
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                years = float(match.group(1))
                if match.group(2):
                    years += 0.5
                return years

        # Step 2 & 3: Only consider "Experience" sections for date ranges and structured experience
        experience_section_pattern = re.compile(
            r'(project experience|professional experience|experience|project details)(.*?)(?=(\n[A-Z][^\n]*:|\Z))',
            re.IGNORECASE | re.DOTALL
        )
        experience_sections = experience_section_pattern.findall(text)
        total_months = 0

        for _, section_text, _ in experience_sections:
            # Step 2: Extract date ranges in this section
            date_range_pattern = re.compile(
                r'([A-Za-z]+ \d{4})\s*[-–]\s*([A-Za-z]+ \d{4}|Present|Till Date|Till Now|Current)', re.IGNORECASE
            )
            matches = date_range_pattern.findall(section_text)
            for start_str, end_str in matches:
                try:
                    start_date = date_parser.parse(start_str)
                    if re.search(r'present|till date|till now|current', end_str, re.IGNORECASE):
                        end_date = datetime.now()
                    else:
                        end_date = date_parser.parse(end_str)
                    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    if months > 0:
                        total_months += months
                except Exception as e:
                    print(f"DEBUG: Failed to parse date range '{start_str} - {end_str}': {e}")

            # Step 3: Structured experience (joining_year, end_year) in this section
            # (If your _extract_experience method can be limited to this section, use it here.
            # Otherwise, you may need to parse this section for years manually.)

        # Convert months to years
        total_years = total_months / 12.0
        return round(total_years, 1)

    def _extract_current_job_title(self, doc) -> Optional[str]:
        """Extract current job title."""
        # List of common job titles
        job_title_keywords = [
            "software engineer", "developer", "data scientist", "project manager", "product manager",
            "consultant", "analyst", "architect", "designer", "qa engineer", "test engineer",
            "full stack developer", "frontend developer", "backend developer", "devops engineer",
            "machine learning engineer", "ai engineer", "researcher", "intern", "lead", "manager",
            "director", "chief", "cto", "ceo", "coo", "founder", "owner", "administrator",
            "business analyst", "data analyst", "system administrator", "network engineer",
            "security engineer", "cloud engineer", "solutions architect", "technical lead",
            "senior engineer", "principal engineer", "staff engineer", "engineering manager"
        ]
        
        # First try to find job title from keywords in the text
        text = doc.text.lower()
        for title in job_title_keywords:
            if title in text:
                return title.title()
        
        # If no keyword match found, look for current position in work experience
        experience = self._extract_experience(doc)
        for exp in experience:
            if (exp.get("end_year") is None and exp.get("position")) or \
               (exp.get("end_year") and str(exp.get("end_year")).strip().lower() == "present"):
                return exp.get("position")
        
        return None


    def _extract_skills(self, doc) -> List[str]:
        """Extract skills using predefined skill list and NLP."""
        # Common technical skills
        skill_keywords = {
            "programming": ["python", "Numbpy", "pandas" "java", "javascript", "c++", "ruby", "php", "swift", "kotlin"],
            "databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "Couchbase", "Cassandra", "NoSql"],
            "frameworks": ["django", "flask", "react", "angular", "vue", "spring", "spring boot"],
            "tools": ["git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp", "postman", "swagger", "rest", "restful", "rest api", "restful api", "maven", "gradle","grafana","splunk"],
            "languages": ["english", "spanish", "french", "german", "chinese", "japanese"]
        }
        
        skills = set()
        text_lower = doc.text.lower()
        
        for category, keyword_list in skill_keywords.items():
            for keyword in keyword_list:
                if keyword in text_lower:
                    skills.add(keyword)
        
        return list(skills)

    def _extract_education(self, doc) -> List[Dict]:
        """Extract education information."""
        education = []
        education_keywords = ["university", "college", "institute", "bachelor", "master", "phd", "b.tech", "m.tech", "b.s.", "m.s."]
        
        # Degree patterns and their full forms
        degree_patterns = {
            "bachelor": ["bachelor", "b.s.", "b.tech", "b.e.", "b.sc.", "b.a."],
            "master": ["master", "m.s.", "m.tech", "m.e.", "m.sc.", "m.a."],
            "phd": ["phd", "doctorate", "d.phil"]
        }
        
        # Simple extraction - can be improved with more sophisticated NLP
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in education_keywords):
                # Try to extract year using regex
                year_pattern = r'\b(19|20)\d{2}\b'
                years = re.findall(year_pattern, sent.text)
                
                # Try to extract degree
                degree = None
                degree_type = None
                for degree_type, patterns in degree_patterns.items():
                    for pattern in patterns:
                        if pattern in sent.text.lower():
                            degree = pattern
                            degree_type = degree_type
                            break
                    if degree:
                        break
                
                # Extract institution name
                institution = sent.text
                if "in" in sent.text.lower():
                    institution = sent.text.split("in")[-1].strip()
                elif "at" in sent.text.lower():
                    institution = sent.text.split("at")[-1].strip()
                
                education.append({
                    "institution": institution,
                    "degree": degree,
                    "degree_type": degree_type,
                    "year": int(years[0]) if years else None
                })
        
        return education

    def _extract_experience(self, doc) -> List[Dict]:
        """Extract work experience information."""
        experience = []
        experience_keywords = ["experience", "worked", "job", "position", "role", "company", "employed"]
        
        # Simple extraction - can be improved with more sophisticated NLP
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in experience_keywords):
                # Try to extract years using regex
                year_pattern = r'\b(19|20)\d{2}\b'
                years = re.findall(year_pattern, sent.text)
                
                # Try to extract company name
                company_keywords = ["at", "with", "in", "for"]
                company = None
                for keyword in company_keywords:
                    if keyword in sent.text.lower():
                        parts = sent.text.lower().split(keyword)
                        if len(parts) > 1:
                            company = parts[1].strip().split()[0]
                            break
                
                # Try to extract position
                position_keywords = ["as", "position of", "role of"]
                position = None
                for keyword in position_keywords:
                    if keyword in sent.text.lower():
                        parts = sent.text.lower().split(keyword)
                        if len(parts) > 1:
                            position = parts[1].strip().split()[0]
                            break
                
                experience.append({
                    "company": company,
                    "position": position,
                    "joining_year": int(years[0]) if years else None,
                    "end_year": int(years[1]) if len(years) > 1 else None,
                    "description": sent.text
                })
        
        return experience


    def _extract_accolades(self, doc) -> List[Dict]:
        """Extract accolades and certifications."""
        accolades = []
        accolade_keywords = ["certified", "certification", "award", "achievement", "accomplishment"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in accolade_keywords):
                # Try to extract years using regex
                year_pattern = r'\b(19|20)\d{2}\b'
                years = re.findall(year_pattern, sent.text)
                
                # Try to extract URL if present
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                urls = re.findall(url_pattern, sent.text)
                
                accolades.append({
                    "url": urls[0] if urls else "",
                    "start_year": int(years[0]) if years else None,
                    "end_year": int(years[1]) if len(years) > 1 else None
                })
        
        return accolades 