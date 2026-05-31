import os
import google.generativeai as genai


genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


SYSTEM_PROMPT = """
You are a professional technical interviewer.

Your goal is to conduct a REAL job interview.

Rules:
- Ask ONLY interview questions
- Keep focus on the vacancy and level
- Questions must match candidate seniority
- Questions must stay related to the vacancy
- Use previous answer only to adapt depth
- Do NOT turn interview into casual conversation
- Ask one concise question at a time
- Mix:
  - technical questions
  - practical scenarios
  - theory
  - problem-solving
- Keep interview professional

Junior:
- basics
- fundamentals
- simple scenarios

Middle:
- practical experience
- architecture basics
- debugging
- optimization

Senior:
- system design
- tradeoffs
- leadership
- scalability
- architecture decisions

Language: Russian.
"""


# =========================
# NEXT QUESTION
# =========================

def generate_next_question(
    conversation: str,
    vacancy: str,
    level: str,
    language: str,
):
    prompt = f"""
Vacancy: {vacancy}

Candidate level: {level}

Interview language: {language}

Interview conversation:
{conversation}

Ask the NEXT interview question.

Requirements:
- Stay strictly inside vacancy topic
- Match difficulty to level
- Use previous candidate answer for follow-up depth
- Do NOT start casual conversation
- Ask only ONE question
- Keep it concise
"""

    response = model.generate_content(
        SYSTEM_PROMPT + "\n\n" + prompt
    )

    return response.text.strip()


# =========================
# REPORT
# =========================
def generate_report(
    conversation: str,
    vacancy: str,
    level: str,
):
    prompt = f"""
You are a fair technical interviewer.

IMPORTANT:
This is a MOCK INTERVIEW for practice, not an exam.

Candidate level: {level}
Vacancy: {vacancy}

Scoring rules:
- 0–30: beginner level, many gaps, but still acceptable for learning
- 31–60: basic understanding with mistakes
- 61–80: solid performance for given level
- 81–100: excellent performance, close to real job readiness

VERY IMPORTANT:
- Do NOT be overly strict
- Do NOT penalize minor wording mistakes
- Focus on overall understanding, not exact terminology
- Adjust expectations based on candidate level

For JUNIOR:
- allow mistakes in theory
- prioritize understanding over precision

For MIDDLE:
- expect practical knowledge, not perfect theory

For SENIOR:
- expect architecture thinking, not memorization

Return ONLY valid JSON:

{{
  "overall_score": number,
  "technical_score": number,
  "communication_score": number,
  "confidence_score": number,
  "feedback": string,
  "strong_points": [string],
  "weak_points": [string],
  "recommendations": [string]
}}

Interview:
{conversation}
"""

    response = model.generate_content(prompt)

    return response.text.strip()