import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv

load_dotenv()

# ─── Configuration ────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="Resume Analyzer AI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Models ──────────────────────────────────────────────────────────

class RephraseRequest(BaseModel):
    text: str
    temperature: float = 0.5
    max_tokens: int = 1024

class InterviewQuestionsRequest(BaseModel):
    job_description: str
    temperature: float = 0.5
    max_tokens: int = 1024

# ─── Core AI Logic (unchanged from original) ──────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_path: str) -> str:
    doc = Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def generate_response(message: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False
    )
    return response.choices[0].message.content

def analyze_resume_with_job_description(resume_text: str, job_description: str, temperature: float, max_tokens: int) -> str:
    prompt = f"""
    Please analyze the following resume in the context of the job description provided. Strictly check every single line in the job description and analyze the resume for exact matches. Maintain high ATS standards and give scores only to the correct matches. Focus on missing core skills and soft skills. Provide the following details:
    1. The match percentage of the resume to the job description.
    2. A list of missing keywords.
    3. Final thoughts on the resume's overall match with the job description in 3 lines.
    4. Recommendations on how to add the missing keywords and improve the resume in 3-4 points with examples.
    Job Description: {job_description}
    Resume: {resume_text}
    """
    return generate_response(prompt, "You are an expert ATS resume analyzer.", temperature, max_tokens)

def analyze_resume_without_job_description(resume_text: str, temperature: float, max_tokens: int) -> str:
    prompt = f"""
    Please analyze the following resume without a specific job description. Provide the following details:
    1. An overall score out of 10 for the resume.
    2. Suggestions for improvements based on the following criteria:
       - Impact (quantification, repetition, verb usage, tenses, responsibilities, spelling & consistency)
       - Brevity (length, bullet points, filler words)
       - Style (buzzwords, dates, contact details, personal pronouns, active voice, consistency)
       - Sections (summary, education, skills, unnecessary sections)
    3. A cumulative assessment of all the above fields.
    4. Recommendations for improving the resume in 3-4 points with examples.

    Resume: {resume_text}
    """
    return generate_response(prompt, "You are an expert ATS resume analyzer.", temperature, max_tokens)

def rephrase_text(text: str, temperature: float, max_tokens: int) -> str:
    prompt = f"""
    Please rephrase the following text according to ATS standards, including quantifiable measures and improvements where possible. Maintain precise and concise points which will pass ATS screening:
    Original Text: {text}
    """
    return generate_response(prompt, "You are an expert in rephrasing content for ATS optimization.", temperature, max_tokens)

def generate_cover_letter(resume_text: str, job_description: str, temperature: float, max_tokens: int) -> str:
    prompt = f"""
    Using the provided resume and job description, create a compelling cover letter. The cover letter should:
    1. Be tailored to the specific job and company.
    2. Highlight relevant skills and experiences from the resume.
    3. Show enthusiasm for the role and company.
    4. Be professional and concise (about 250-300 words).

    Resume: {resume_text}
    Job Description: {job_description}
    """
    return generate_response(prompt, "You are an expert in writing tailored cover letters.", temperature, max_tokens)

def generate_interview_questions(job_description: str, temperature: float, max_tokens: int) -> str:
    prompt = f"""
    Based on the following job description, generate a list of 10 probable interview questions. Include a mix of:
    1. Role-specific technical questions (if applicable)
    2. Behavioral questions related to the required skills
    3. Questions about the candidate's experience and background
    4. Questions to assess cultural fit

    Ensure the questions are tailored to the specific job role and requirements.

    Job Description: {job_description}
    """
    return generate_response(prompt, "You are an expert in creating relevant interview questions based on job descriptions.", temperature, max_tokens)

# ─── Helper: Parse Uploaded File ──────────────────────────────────────────────

async def parse_resume_file(file: UploadFile) -> str:
    """Save uploaded file to a temp path and extract text."""
    suffix = os.path.splitext(file.filename)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        if suffix == ".pdf":
            return extract_text_from_pdf(tmp_path)
        elif suffix == ".docx":
            return extract_text_from_docx(tmp_path)
        else:
            return ""
    finally:
        os.unlink(tmp_path)

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Resume Analyzer AI is running. Visit /docs for the API reference."}


@app.post("/analyze_resume")
async def api_analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    with_job_description: bool = Form(True),
    temperature: float = Form(0.5),
    max_tokens: int = Form(1024),
):
    resume_text = await parse_resume_file(file)
    if not resume_text.strip():
        return {"error": "Could not extract text from the uploaded file. Please upload a valid PDF or DOCX."}

    if with_job_description and job_description.strip():
        result = analyze_resume_with_job_description(resume_text, job_description, temperature, max_tokens)
    else:
        result = analyze_resume_without_job_description(resume_text, temperature, max_tokens)

    return {"result": result}


@app.post("/rephrase")
async def api_rephrase(body: RephraseRequest):
    if not body.text.strip():
        return {"error": "Please provide text to rephrase."}
    result = rephrase_text(body.text, body.temperature, body.max_tokens)
    return {"result": result}


@app.post("/generate_cover_letter")
async def api_generate_cover_letter(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    temperature: float = Form(0.5),
    max_tokens: int = Form(1024),
):
    resume_text = await parse_resume_file(file)
    if not resume_text.strip():
        return {"error": "Could not extract text from the uploaded file."}

    result = generate_cover_letter(resume_text, job_description, temperature, max_tokens)
    return {"result": result}


@app.post("/generate_interview_questions")
async def api_generate_interview_questions(body: InterviewQuestionsRequest):
    if not body.job_description.strip():
        return {"error": "Please provide a job description."}
    result = generate_interview_questions(body.job_description, body.temperature, body.max_tokens)
    return {"result": result}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
