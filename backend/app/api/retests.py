from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/retests", tags=["retests"])


class RetestCreate(BaseModel):
    student_id: str
    assessment_id: str
    remediation_assignment_id: Optional[str] = None


class RetestSubmit(BaseModel):
    score: int


@router.post("")
async def create_retest(data: RetestCreate):
    """Create a retest opportunity"""
    supabase = get_supabase()
    
    try:
        # Get the original attempt to get initial score
        attempt_response = supabase.table("assessment_attempts").select("*").eq(
            "assessment_id", data.assessment_id
        ).eq("student_id", data.student_id).execute()
        
        if not attempt_response.data:
            raise HTTPException(status_code=404, detail="Original attempt not found")
        
        initial_score = attempt_response.data[0].get("score", 0)
        
        # Create retest
        retest_data = {
            "student_id": data.student_id,
            "assessment_id": data.assessment_id,
            "remediation_assignment_id": data.remediation_assignment_id,
            "initial_score": initial_score,
            "created_at": "now()"
        }
        
        response = supabase.table("retests").insert(retest_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create retest")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_retests(student_id: Optional[str] = None):
    """Get retests"""
    supabase = get_supabase()
    
    try:
        if student_id:
            response = supabase.table("retests").select(
                "*, assessments(*), profiles(*)"
            ).eq("student_id", student_id).execute()
        else:
            raise HTTPException(status_code=400, detail="Must provide student_id")
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{retest_id}/submit")
async def submit_retest(retest_id: str, data: RetestSubmit):
    """Submit retest score"""
    supabase = get_supabase()
    
    try:
        # Get retest
        retest_response = supabase.table("retests").select("*").eq("id", retest_id).execute()
        
        if not retest_response.data:
            raise HTTPException(status_code=404, detail="Retest not found")
        
        retest = retest_response.data[0]
        
        # Calculate improvement
        improvement = data.score - retest["initial_score"]
        
        # Update retest
        response = supabase.table("retests").update({
            "retest_score": data.score,
            "improvement": improvement,
            "taken_at": "now()"
        }).eq("id", retest_id).execute()
        
        # Update student progress
        # Get assessment to get topic
        assessment_response = supabase.table("assessments").select("*").eq("id", retest["assessment_id"]).execute()
        assessment = assessment_response.data[0]
        
        # Update or create progress record
        progress_response = supabase.table("student_progress").select("*").eq(
            "student_id", retest["student_id"]
        ).eq("topic", assessment["topic"]).eq("subject", assessment["subject"]).execute()
        
        new_level = "foundation"
        if data.score >= 70:
            new_level = "mastery"
        elif data.score >= 50:
            new_level = "developing"
        
        if progress_response.data:
            supabase.table("student_progress").update({
                "current_level": new_level,
                "progress_percentage": data.score,
                "last_assessment_date": "now()",
                "updated_at": "now()"
            }).eq("id", progress_response.data[0]["id"]).execute()
        else:
            supabase.table("student_progress").insert({
                "student_id": retest["student_id"],
                "subject": assessment["subject"],
                "topic": assessment["topic"],
                "current_level": new_level,
                "progress_percentage": data.score,
                "last_assessment_date": "now()"
            }).execute()
        
        # Resolve learning gap if improvement is significant
        if improvement >= 20:
            gap_response = supabase.table("learning_gaps").select("*").eq(
                "student_id", retest["student_id"]
            ).eq("topic", assessment["topic"]).eq("subject", assessment["subject"]).is_("resolved_at", None).execute()
            
            if gap_response.data:
                supabase.table("learning_gaps").update({
                    "resolved_at": "now()"
                }).eq("id", gap_response.data[0]["id"]).execute()
        
        return {
            "message": "Retest submitted successfully",
            "initial_score": retest["initial_score"],
            "retest_score": data.score,
            "improvement": improvement
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
