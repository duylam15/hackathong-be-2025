from typing import List, Optional
from pydantic import BaseModel

class Question(BaseModel):
    id: int
    question: str
    options: List[str]  # e.g., ["A: Option1", "B: Option2", ...]
    layer: int  # 1, 2, or 3

class QuizQuestions(BaseModel):
    questions: List[Question]

class Answer(BaseModel):
    question_id: int
    choice: str  # 'A', 'B', etc.

class QuizAnswers(BaseModel):
    answers: List[Answer]

class QuizResult(BaseModel):
    user_type: str
    novelty_score: float
    description: str
    suggested_tours: List[dict]  # e.g., [{"name": "Tour Sapa", "type": "Adventure"}]