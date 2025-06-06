from app.services.resume_llm_service import ResumeLLMService
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('custom_logger')
# Make sure your .env file has OPENAI_API_KEY set, or set it here:
# os.environ["OPENAI_API_KEY"] = "sk-..."

# Example resume text (replace with your own for testing)
resume_text = """
John Doe
Email: john.doe@example.com
Phone: 555-123-4567

Education:
Bachelor of Science in Computer Science, MIT, 2018

Skills:
Python, JavaScript, SQL

Work Experience:
Software Engineer, Google, 2018-2022
Worked on scalable backend systems.
"""

# Initialize the service
llm_service = ResumeLLMService(api_key=os.getenv("OPENAI_API_KEY"))

# Call the extraction method
try:
    print("Before LLM call: ")
    result = llm_service.extract_resume_data(resume_text)
    print("After LLM call:  ")
    print("LLM Resume Extraction Result: ")
    print(result)
    logger.info(result)
except Exception as e:
    print("Error:", e)