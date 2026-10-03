from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClassBase(BaseModel):
    name: str
    grade: str
    subject: str
    section: Optional[str] = None
    academic_year: str
    description: Optional[str] = None


class ClassCreate(ClassBase):
    class_code: str


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Class(ClassBase):
    id: str
    teacher_id: str
    class_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassMember(BaseModel):
    id: str
    class_id: str
    student_id: str
    joined_at: datetime

    class Config:
        from_attributes = True
