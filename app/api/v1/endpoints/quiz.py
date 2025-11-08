from fastapi import APIRouter, HTTPException
from typing import Dict

from app.schemas.quiz import QuizQuestions, QuizAnswers, QuizResult
from app.services.quiz_service import get_questions, classify_user

router = APIRouter()

@router.get("/questions", response_model=Dict)  # Use Dict for layered structure
async def get_quiz_questions():
    """GET: Retrieve quiz questions grouped by layers."""
    return get_questions()

@router.post("/result", response_model=QuizResult)
async def submit_quiz_answers(quiz_answers: QuizAnswers):
    """POST: Submit answers and get personalized result."""
    try:
        result = classify_user(quiz_answers.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))