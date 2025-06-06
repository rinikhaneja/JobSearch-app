from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

RESUME_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ResumeData",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Full name of the candidate"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "Email address of the candidate"
        },
        "phone": {
            "type": ["string", "null"],
            "description": "Phone number of the candidate"
        },
        "education": {
            "type": "array",
            "description": "List of education entries",
            "items": {
                "type": "object",
                "properties": {
                    "degree": { "type": ["string", "null"] },
                    "school": { "type": ["string", "null"] },
                    "year": { "type": ["integer", "null"] }
                },
            }
        },
        "skills": {
            "type": "array",
            "description": "List of skills",
            "items": { "type": "string" }
        },
        "work_experience": {
            "type": "array",
            "description": "List of work experience entries",
            "items": {
                "type": "object",
                "properties": {
                    "company": { "type": ["string", "null"] },
                    "title": { "type": ["string", "null"] },
                    "start_year": { "type": ["integer", "null"] },
                    "end_year": { "type": ["integer", "null"] },
                    "description": { "type": ["string", "null"] }
                },
            }
        },
        "years_of_experience": {
            "type": ["number", "null"],
            "description": "Years of experience of the candidate"
        }
    },
    "required": ["name", "email", "skills"],
    "additionalProperties": False
}

def get_schema_prompt() -> str:
    """Convert schema to a prompt-friendly format"""
    return (
        "{\n"
        '  "name": "string", // Full name of the candidate\n'
        '  "email": "string", // Email address of the candidate\n'
        '  "phone": "string", // Phone number of the candidate\n'
        '  "years_of_experience": number, // Total years of experience (e.g., 5.2)\n'
        '  "education": [ // List of education entries\n'
        '    {\n'
        '      "degree": "string",\n'
        '      "school": "string",\n'
        '      "year": integer\n'
        '    }\n'
        '  ],\n'
        '  "skills": ["string"], // List of skills\n'
        '  "work_experience": [ // List of work experience entries\n'
        '    {\n'
        '      "company": "string",\n'
        '      "title": "string",\n'
        '      "start_year": integer,\n'
        '      "end_year": integer or null,\n'
        '      "description": "string"\n'
        '    }\n'
        '  ]\n'
        "}"
    )

