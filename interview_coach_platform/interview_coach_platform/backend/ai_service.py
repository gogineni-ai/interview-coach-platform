import re
from collections import Counter

SKILL_WORDS = {
    "python", "java", "javascript", "react", "sql", "aws", "azure", "gcp",
    "machine learning", "artificial intelligence", "data analytics",
    "fastapi", "django", "flask", "tableau", "power bi", "docker",
    "kubernetes", "oracle", "oic", "hcm", "pl/sql", "spark"
}

def analyze_resume(resume_text: str) -> str:
    text = resume_text.lower()
    found = sorted([skill for skill in SKILL_WORDS if skill in text])

    years = re.findall(r"\b(20\d{2})\b", resume_text)
    year_note = ""
    if years:
        year_note = f" Timeline references detected: {', '.join(sorted(set(years)))}."

    skills = ", ".join(found[:18]) if found else "No common technical skills automatically detected."

    return (
        f"Resume strengths: {skills}.{year_note} "
        "For interview preparation, be ready to explain your recent project, "
        "your exact contribution, one difficult problem you solved, measurable impact, "
        "and how your experience maps to the target role."
    )

def detect_question(text: str) -> bool:
    q = text.strip().lower()
    starters = (
        "tell me", "describe", "explain", "what", "why", "how", "when",
        "where", "which", "walk me", "give me", "can you", "have you",
        "do you", "did you", "could you"
    )
    return q.endswith("?") or q.startswith(starters)

def generate_answer(question: str, resume_text: str) -> str:
    # Local fallback: produces a practice answer grounded in the resume.
    # Replace this function with an LLM provider for higher-quality responses.
    lines = [ln.strip() for ln in resume_text.splitlines() if len(ln.strip()) > 25]
    context = " ".join(lines[:8])[:1200]

    return (
        "Practice answer:\n\n"
        f"For the question: “{question.strip()}”\n\n"
        "Use a concise first-person response based only on experience you can truthfully defend. "
        "A strong structure is: context → your responsibility → actions → result → what you learned.\n\n"
        f"Resume context detected:\n{context}\n\n"
        "Suggested delivery: keep the first response to about 45–75 seconds, use specific tools "
        "and measurable outcomes where accurate, and be prepared for a follow-up."
    )

def generate_mock_questions(resume_text: str):
    text = resume_text.lower()
    qs = [
        "Tell me about yourself.",
        "Walk me through your most recent project.",
        "What was the most difficult technical problem you solved?",
        "Describe a time you disagreed with a teammate and how you handled it.",
        "What measurable impact did your work have?",
        "Why are you interested in this role?"
    ]
    if "python" in text:
        qs.append("How have you used Python in a production project?")
    if "machine learning" in text or "artificial intelligence" in text:
        qs.append("Describe an AI or machine-learning project you built and how you evaluated it.")
    if "sql" in text:
        qs.append("Tell me about a complex SQL or data-analysis problem you solved.")
    return qs
