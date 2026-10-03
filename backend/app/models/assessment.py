from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    options: Optional[dict] = None
    correct_answer: str
    marks: int = 1
    difficulty: Optional[str] = None
    topic: Optional[str] = None
    order_index: int


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: str
    assessment_id: str

    class Config:
        from_attributes = True


class AssessmentBase(BaseModel):
    title: str
    type: str
    subject: str
    topic: str
    duration: int
    total_marks: int
    passing_score: int
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    instructions: Optional[str] = None


class AssessmentCreate(AssessmentBase):
    class_id: str
    questions: List[QuestionCreate]


class Assessment(AssessmentBase):
    id: str
    teacher_id: str
    class_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentAttemptBase(BaseModel):
    assessment_id: str
    student_id: str


class AssessmentAttemptCreate(AssessmentAttemptBase):
    pass


class AssessmentAttempt(AssessmentAttemptBase):
    id: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    score: Optional[int] = None
    total_marks: Optional[int] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    time_taken: Optional[int] = None

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    question_id: str
    answer: str
