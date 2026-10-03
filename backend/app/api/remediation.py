from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.supabase_client import get_supabase
from app.services.ai_service import ai_service

router = APIRouter(prefix="/remediation", tags=["remediation"])


class RemediationCreate(BaseModel):
    learning_gap_id: str
    title: str
    content: dict
    target_level: str


@router.post("")
async def create_remediation(data: RemediationCreate, teacher_id: str):
    """Create a remediation plan"""
    supabase = get_supabase()
    
    try:
        # Verify teacher exists
        profile_response = supabase.table("profiles").select("*").eq("id", teacher_id).eq("role", "teacher").execute()
        
        if not profile_response.data:
            raise HTTPException(status_code=403, detail="Only teachers can create remediation plans")
        
        # Get learning gap
        gap_response = supabase.table("learning_gaps").select("*").eq("id", data.learning_gap_id).execute()
        
        if not gap_response.data:
            raise HTTPException(status_code=404, detail="Learning gap not found")
        
        gap = gap_response.data[0]
        
        # Create remediation plan
        remediation_data = {
            "learning_gap_id": data.learning_gap_id,
            "teacher_id": teacher_id,
            "title": data.title,
            "content": data.content,
            "target_level": data.target_level,
            "teacher_approved": True
        }
        
        response = supabase.table("remediation_plans").insert(remediation_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create remediation plan")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_remediation_plans(teacher_id: Optional[str] = None, student_id: Optional[str] = None):
    """Get remediation plans"""
    supabase = get_supabase()
    
    try:
        if teacher_id:
            response = supabase.table("remediation_plans").select("*").eq("teacher_id", teacher_id).execute()
        elif student_id:
            response = supabase.table("remediation_assignments").select(
                "remediation_plans(*)"
            ).eq("student_id", student_id).execute()
            # Extract plans
            plans = [item["remediation_plans"] for item in response.data if item.get("remediation_plans")]
            return plans
        else:
            raise HTTPException(status_code=400, detail="Must provide teacher_id or student_id")
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plan_id}/assign")
async def assign_remediation(plan_id: str, student_id: str):
    """Assign remediation to a student"""
    supabase = get_supabase()
    
    try:
        # Check if already assigned
        existing = supabase.table("remediation_assignments").select("*").eq(
            "remediation_plan_id", plan_id
        ).eq("student_id", student_id).eq("status", "pending").execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Remediation already assigned to this student")
        
        # Create assignment
        assignment_data = {
            "remediation_plan_id": plan_id,
            "student_id": student_id,
            "status": "pending"
        }
        
        response = supabase.table("remediation_assignments").insert(assignment_data).execute()
        
        return {"message": "Remediation assigned successfully", "assignment": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assignments/{assignment_id}/complete")
async def complete_remediation(assignment_id: str):
    """Mark remediation as completed by student"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("remediation_assignments").update({
            "status": "completed",
            "completed_at": "now()"
        }).eq("id", assignment_id).execute()
        
        # Get assignment to create retest
        assignment_response = supabase.table("remediation_assignments").select(
            "*, remediation_plans(*, learning_gaps(*))"
        ).eq("id", assignment_id).execute()
        
        if assignment_response.data:
            assignment = assignment_response.data[0]
            plan = assignment.get("remediation_plans")
            if plan:
                gap = plan.get("learning_gaps")
                if gap:
                    # Create retest opportunity
                    retest_data = {
                        "student_id": assignment["student_id"],
                        "assessment_id": gap.get("assessment_id"),
                        "remediation_assignment_id": assignment_id,
                        "initial_score": 0,  # Will be updated when needed
                        "created_at": "now()"
                    }
                    
                    supabase.table("retests").insert(retest_data).execute()
        
        return {"message": "Remediation marked as completed", "retest_available": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_id}/pending")
async def get_student_pending_remediation(student_id: str):
    """Get pending remediation assignments for a student"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("remediation_assignments").select(
            "*, remediation_plans(*, learning_gaps(*))"
        ).eq("student_id", student_id).eq("status", "pending").execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
