from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressUpdate(BaseModel):
    student_id: str
    subject: str
    topic: str
    current_level: str
    progress_percentage: float


@router.get("/student/{student_id}")
async def get_student_progress(student_id: str):
    """Get all progress for a student"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("student_progress").select("*").eq("student_id", student_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class/{class_id}")
async def get_class_progress(class_id: str, teacher_id: str):
    """Get progress for all students in a class (teacher only)"""
    supabase = get_supabase()
    
    try:
        # Verify teacher owns the class
        class_response = supabase.table("classes").select("*").eq("id", class_id).eq("teacher_id", teacher_id).execute()
        
        if not class_response.data:
            raise HTTPException(status_code=403, detail="You can only view progress in your own classes")
        
        # Get progress for students in this class
        response = supabase.table("student_progress").select(
            "*, profiles(full_name, email)"
        ).in_(
            "student_id",
            supabase.table("class_members").select("student_id").eq("class_id", class_id)
        ).execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def update_progress(data: ProgressUpdate):
    """Update or create progress record"""
    supabase = get_supabase()
    
    try:
        # Check if exists
        existing = supabase.table("student_progress").select("*").eq(
            "student_id", data.student_id
        ).eq("topic", data.topic).eq("subject", data.subject).execute()
        
        if existing.data:
            # Update
            response = supabase.table("student_progress").update({
                "current_level": data.current_level,
                "progress_percentage": data.progress_percentage,
                "last_assessment_date": "now()",
                "updated_at": "now()"
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # Create
            response = supabase.table("student_progress").insert({
                "student_id": data.student_id,
                "subject": data.subject,
                "topic": data.topic,
                "current_level": data.current_level,
                "progress_percentage": data.progress_percentage,
                "last_assessment_date": "now()"
            }).execute()
        
        return response.data[0] if response.data else {"message": "Progress updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
