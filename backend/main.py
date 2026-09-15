from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from database import init_db, get_conn
from auth import hash_password, verify_password, create_access_token, decode_access_token
from resume_parser import extract_resume_text
from ai_service import analyze_resume, generate_answer, generate_mock_questions, detect_question

app = FastAPI(title="Interview Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class AuthBody(BaseModel):
    email: str
    password: str

class QuestionBody(BaseModel):
    question: str

class TranscriptBody(BaseModel):
    transcript: str

def current_user_id(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    try:
        return decode_access_token(authorization.split(" ", 1)[1])
    except ValueError:
        raise HTTPException(401, "Invalid token")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/auth/register")
def register(body: AuthBody):
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users(email,password_hash) VALUES(?,?)",
                (body.email.lower().strip(), hash_password(body.password))
            )
            user_id = cur.lastrowid
        except Exception:
            raise HTTPException(400, "Email already registered")
    return {"token": create_access_token(user_id)}

@app.post("/auth/login")
def login(body: AuthBody):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (body.email.lower().strip(),)
        ).fetchone()
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"token": create_access_token(row["id"])}

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Depends(current_user_id)
):
    data = await file.read()
    try:
        text = extract_resume_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(400, str(e))

    if len(text) < 40:
        raise HTTPException(400, "Could not extract enough resume text")

    analysis = analyze_resume(text)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO resumes(user_id,filename,resume_text,analysis) VALUES(?,?,?,?)",
            (user_id, file.filename, text, analysis)
        )
    return {"filename": file.filename, "analysis": analysis}

def latest_resume(user_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()
    if not row:
        raise HTTPException(400, "Upload a resume first")
    return row

@app.get("/resume/latest")
def get_latest_resume(user_id: int = Depends(current_user_id)):
    row = latest_resume(user_id)
    return {
        "filename": row["filename"],
        "analysis": row["analysis"],
        "preview": row["resume_text"][:1200]
    }

@app.get("/practice/questions")
def practice_questions(user_id: int = Depends(current_user_id)):
    row = latest_resume(user_id)
    return {"questions": generate_mock_questions(row["resume_text"])}

@app.post("/practice/answer")
def practice_answer(body: QuestionBody, user_id: int = Depends(current_user_id)):
    row = latest_resume(user_id)
    return {
        "answer": generate_answer(body.question, row["resume_text"]),
        "mode": "practice"
    }

@app.post("/practice/transcript")
def transcript(body: TranscriptBody, user_id: int = Depends(current_user_id)):
    row = latest_resume(user_id)
    if not detect_question(body.transcript):
        return {"is_question": False, "answer": None}
    return {
        "is_question": True,
        "answer": generate_answer(body.transcript, row["resume_text"])
    }
