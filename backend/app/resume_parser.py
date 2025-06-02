import os
from typing import Dict, List, Optional
import docx
from PyPDF2 import PdfReader
import spacy
import magic
from datetime import datetime
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from different file formats."""
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        
        if file_type == "application/pdf":
            text = self._extract_from_pdf(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        print(f"DEBUG: Extracted text from file:\n{text[:500]}...")  # Print first 500 chars
        return text

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume text and extract structured information."""
        # First extract text from the file
        text = self.extract_text_from_file(file_path)
        doc = self.nlp(text)
        
        # Initialize result dictionary
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
        
        # First try to find email with potential spaces
        email_with_spaces = re.search(r'email\s*:?\s*([\w\.-]+)\s*@\s*([\w\.-]+(?:\s*\.\s*[\w\.-]+)*)', text, re.IGNORECASE)
        if email_with_spaces:
            # Remove all spaces from the email parts
            username = email_with_spaces.group(1).replace(" ", "")
            domain = email_with_spaces.group(2).replace(" ", "")
            email = f"{username}@{domain}"
            print(f"DEBUG: Found email with spaces: {email}")
            return email
        
        # Standard email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # First try exact email pattern
        match = re.search(email_pattern, text)
        if match:
            print(f"DEBUG: Found email using standard pattern: {match.group(0)}")
            return match.group(0)
        
        # If not found, try to find email in common formats
        # Look for patterns like "Email: john@example.com" or "E-mail: john@example.com"
        email_keywords = ["email", "e-mail", "mail", "contact"]
        for keyword in email_keywords:
            # Look for the keyword followed by various separators
            patterns = [
                f"{keyword}[:\\s]+([A-Za-z0-9._%+-]+)\\s*@\\s*([A-Za-z0-9.-]+(?:\\s*\\.\\s*[A-Za-z0-9.-]+)*)",
                f"{keyword}[\\s]*[=]+[\\s]*([A-Za-z0-9._%+-]+)\\s*@\\s*([A-Za-z0-9.-]+(?:\\s*\\.\\s*[A-Za-z0-9.-]+)*)",
                f"{keyword}[\\s]*[-]+[\\s]*([A-Za-z0-9._%+-]+)\\s*@\\s*([A-Za-z0-9.-]+(?:\\s*\\.\\s*[A-Za-z0-9.-]+)*)"
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Remove all spaces from the email parts
                    username = match.group(1).replace(" ", "")
                    domain = match.group(2).replace(" ", "")
                    email = f"{username}@{domain}"
                    print(f"DEBUG: Found email using pattern '{pattern}': {email}")
                    return email
        
        # Try to find email in contact information section
        contact_section = re.search(r'(?:contact|contact information|contact details)[^@]*?([A-Za-z0-9._%+-]+)\s*@\s*([A-Za-z0-9.-]+(?:\s*\.\s*[A-Za-z0-9.-]+)*)', text, re.IGNORECASE)
        if contact_section:
            # Remove all spaces from the email parts
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
            "contact", "contact no", "reach me at", "call", "📞"
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
        """Calculate total years of experience."""
        experience = self._extract_experience(doc)
        if experience:
            total_years = 0.0
            for exp in experience:
                start_year = exp.get("joining_year")
                end_year = exp.get("end_year")
                if start_year and end_year:
                    total_years += end_year - start_year
                elif start_year:
                    # If no end year, assume current year
                    current_year = datetime.now().year
                    total_years += current_year - start_year
            if total_years > 0:
                return round(total_years, 1)
        
        # Fallback: look for phrases like 'X years of experience' in the text
        text = doc.text.lower()
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(\+)?\s*years? of experience',
            r'(\d+(?:\.\d+)?)\s*(\+)?\s*yrs? of experience',
            r'(\d+(?:\.\d+)?)\s*(\+)?\s*years? experience',
            r'(\d+(?:\.\d+)?)\s*(\+)?\s*yrs? experience'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                years = float(match.group(1))
                if match.group(2):
                    years += 0.5
                return years
        
        return 0.0

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
            "programming": ["python", "java", "javascript", "c++", "ruby", "php", "swift", "kotlin"],
            "databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "oracle"],
            "frameworks": ["django", "flask", "react", "angular", "vue", "spring", "express"],
            "tools": ["git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp"],
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