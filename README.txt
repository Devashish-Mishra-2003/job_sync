JobSync
JobSync is an AI-powered platform designed to streamline and enhance the job application process for both students and placement teams. It provides instant, data-driven feedback on resume-to-job-description compatibility, turning a historically manual and opaque process into an efficient and transparent one.

This project was built for the Code 5 Edu-Tech Hackathon as a solution for Theme 2.

How It Works
JobSync is built on a modern, decoupled architecture, a key feature that makes it highly scalable and reliable. The application is split into two main components:

Frontend (Streamlit): A user-friendly interface that handles all user interactions. It allows students to upload their resumes and get instant feedback, while giving placement teams a dashboard to manage job descriptions and evaluate candidates.

Backend (FastAPI): A high-performance API that handles all the heavy lifting. This includes parsing resumes and job descriptions, calculating compatibility scores using intelligent heuristics, and providing detailed feedback.

These two services are deployed independently, allowing them to scale separately to meet demand. For instance, a surge in user visits on the frontend won't impact the backend's performance during heavy evaluation tasks.

Key Features
Instant Resume Evaluation: Students receive an immediate compatibility score and verdict (High, Medium, or Low) after uploading their resume.

Actionable Feedback: The app provides concrete, personalized suggestions on how to improve a resume for a specific job, including missing skills and project ideas.

Placement Team Dashboard: A centralized dashboard allows recruiters to upload job descriptions, view all candidate evaluations in one place, and filter results by score and location.

Scalable Architecture: The decoupled setup with a Streamlit frontend and FastAPI backend ensures the application can handle a large number of users and evaluations without compromising on performance.

AI-Ready: The application's foundation is built to easily integrate advanced AI features, such as LLM-powered semantic analysis for even more nuanced feedback and matching in the future.

Tech Stack
Frontend: Streamlit

Backend: FastAPI

Parsing: pdfplumber, python-docx

Dependencies: requests, numpy, uvicorn, python-multipart

Hosting: StreamlitCloud (Frontend) and Render (Backend)

Deployment
The application uses a modern, two-part deployment strategy for maximum efficiency.

Backend: The FastAPI service is deployed on Render using a render.yaml blueprint. The service automatically scales to handle incoming API requests.

Frontend: The Streamlit application is deployed on Vercel, connecting to the live backend using an environment variable (BACKEND_URL).

Getting Started Locally
To run this application on your local machine, you'll need Python and conda.

Clone the repository:

git clone [https://github.com/Devashish-Mishra-2003/job_sync.git](https://github.com/Devashish-Mishra-2003/job_sync.git)
cd job_sync

Set up the environment:

conda create -n resume_env python=3.10
conda activate resume_env
pip install -r requirements.txt

Run the backend:
Open a new terminal and run the backend server.

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

Run the frontend:
Open another terminal and run the Streamlit application.

streamlit run app.py

Your app will now be available in your web browser, ready to use!
