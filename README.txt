# 🚀 JobSync  

**JobSync** is an **AI-powered platform** designed to streamline and enhance the **job application process** for both **students** and **placement teams**.  
It provides **instant, data-driven feedback** on resume-to-job-description compatibility — turning a historically manual and opaque process into an **efficient and transparent experience**.  

🔗 **[👉 Try it Live Here!](https://jobsync-horizon.streamlit.app/)**  

---

## 🏆 About the Project  
This project was built for the **Code 5 Edu-Tech Hackathon** as a solution for **Theme 2**.  

---

## ⚙️ How It Works  

JobSync is built on a **modern, decoupled architecture**, making it **scalable** and **reliable**.  
It consists of two main components:  

### 🎨 Frontend (Streamlit)  
- User-friendly interface for **students** and **placement teams**  
- Students can **upload resumes** and get **instant compatibility feedback**  
- Placement teams get a **dashboard** to manage job descriptions and evaluate candidates  

### ⚡ Backend (FastAPI)  
- High-performance API for all the **heavy lifting**  
- Handles resume & JD parsing, compatibility scoring, and detailed feedback  
- Independent deployment for smooth scalability  

👉 **Decoupled Deployment:** A surge in frontend traffic won’t slow down backend evaluations 🚀  

---

## ✨ Key Features  

✅ **Instant Resume Evaluation** – Get compatibility score + verdict (**High, Medium, Low**) instantly  
✅ **Actionable Feedback** – Concrete suggestions to improve resumes (skills, projects, etc.)  
✅ **Placement Team Dashboard** – Upload JDs, evaluate candidates, filter & export results  
✅ **Scalable Architecture** – Independent scaling of backend & frontend services  
✅ **AI-Ready** – Future integration with **LLM-powered semantic analysis** for deeper matching  

---

## 🛠 Tech Stack  

- **Frontend:** Streamlit 🎨  
- **Backend:** FastAPI ⚡  
- **Parsing:** pdfplumber, python-docx 📄  
- **Other Dependencies:** requests, numpy, uvicorn, python-multipart  
- **Hosting:**  
  - 🌐 Frontend → **Vercel / Streamlit Cloud**  
  - ⚙️ Backend → **Render**  

---

## 📐 System Architecture  

![Architecture Diagram](assets/architecture.png)  

*(Example: Streamlit frontend ↔ FastAPI backend ↔ Resume/Job Data Parsing & Scoring Modules)*  

---

## 🖼 Screenshots  

### 🔹 Student View  
![Student Dashboard](assets/student_dashboard.png)  

### 🔹 Placement Team Dashboard  
![Placement Dashboard](assets/placement_dashboard.png)  

---

## 🚀 Deployment Strategy  

- **Backend (FastAPI):**  
  - Deployed on **Render** using `render.yaml` blueprint  
  - Auto-scales to handle incoming requests  

- **Frontend (Streamlit):**  
  - Deployed on **Vercel** / Streamlit Cloud  
  - Connects to live backend using environment variable `BACKEND_URL`  

---

## 💻 Getting Started Locally  

To run JobSync locally, make sure you have **Python** + **conda** installed.  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/Devashish-Mishra-2003/job_sync.git
cd job_sync

