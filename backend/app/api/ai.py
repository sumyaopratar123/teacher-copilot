from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


class LessonPlanRequest(BaseModel):
    grade: str
    subject: str
    topic: str
    duration: int
    learning_objectives: List[str]
    difficulty: Optional[str] = "developing"
    language: Optional[str] = "en"


class WorksheetRequest(BaseModel):
    grade: str
    subject: str
    topic: str
    num_questions: int = 10
    question_types: List[str] = ["mcq", "short_answer"]
    difficulty: Optional[str] = "developing"
    language: Optional[str] = "en"


class QuizRequest(BaseModel):
    grade: str
    subject: str
    topic: str
    num_questions: int = 10
    question_types: List[str] = ["mcq"]
    difficulty: Optional[str] = "developing"
    language: Optional[str] = "en"


class RemediationRequest(BaseModel):
    grade: str
    subject: str
    topic: str
    current_level: str
    target_level: str
    reason: str


@router.post("/lesson-plan")
async def generate_lesson_plan(request: LessonPlanRequest):
    """Generate a lesson plan using AI"""
    try:
        result = await ai_service.generate_lesson_plan(request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/worksheet")
async def generate_worksheet(request: WorksheetRequest):
    """Generate a worksheet using AI"""
    try:
        result = await ai_service.generate_worksheet(request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz")
async def generate_quiz(request: QuizRequest):
    """Generate a quiz using AI"""
    try:
        result = await ai_service.generate_quiz(request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remediation")
async def generate_remediation(request: RemediationRequest):
    """Generate remediation content using AI"""
    try:
        result = await ai_service.generate_remediation(request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
