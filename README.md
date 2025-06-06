# JobSearch App

This project is a job search application built with FastAPI for the backend and React (Material-UI) for the frontend. It allows users to upload their resumes, analyze them, search for jobs, and match jobs based on their qualifications.

## Features

- Upload Resume: Users can upload their resumes in .pdf, .doc, or .docx formats.
- Analyze Resume: The application analyzes the uploaded resume.
- Job Search: Users can search for jobs based on their qualifications.
- Match Jobs: The application matches jobs based on the user's qualifications.

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