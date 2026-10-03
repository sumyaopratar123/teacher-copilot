from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/learning-gaps", tags=["learning-gaps"])


@router.get("/student/{student_id}")
async def get_student_learning_gaps(student_id: str):
    """Get all learning gaps for a student"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("learning_gaps").select("*").eq("student_id", student_id).is_("resolved_at", None).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class/{class_id}")
async def get_class_learning_gaps(class_id: str, teacher_id: str):
    """Get all learning gaps for a class (teacher only)"""
    supabase = get_supabase()
    
    try:
        # Verify teacher owns the class
        class_response = supabase.table("classes").select("*").eq("id", class_id).eq("teacher_id", teacher_id).execute()
        
        if not class_response.data:
            raise HTTPException(status_code=403, detail="You can only view learning gaps in your own classes")
        
        # Get learning gaps for students in this class
        response = supabase.table("learning_gaps").select(
            "*, profiles(full_name, email)"
        ).in_(
            "student_id",
            supabase.table("class_members").select("student_id").eq("class_id", class_id)
        ).is_("resolved_at", None).execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teacher/{teacher_id}")
async def get_teacher_learning_gaps(teacher_id: str):
    """Get all learning gaps across all classes for a teacher"""
    supabase = get_supabase()
    
    try:
        # Get all class IDs for this teacher
        classes_response = supabase.table("classes").select("id").eq("teacher_id", teacher_id).execute()
        class_ids = [c["id"] for c in classes_response.data]
        
        if not class_ids:
            return []
        
        # Get learning gaps for students in all these classes
        response = supabase.table("learning_gaps").select(
            "*, profiles(full_name, email)"
        ).in_(
            "student_id",
            supabase.table("class_members").select("student_id").in_("class_id", class_ids)
        ).is_("resolved_at", None).execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect/{attempt_id}")
async def detect_learning_gaps(attempt_id: str):
    """Detect learning gaps based on assessment attempt"""
    supabase = get_supabase()
    
    try:
        # Get the attempt
        attempt_response = supabase.table("assessment_attempts").select("*").eq("id", attempt_id).execute()
        
        if not attempt_response.data:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        attempt = attempt_response.data[0]
        
        # Get the assessment
        assessment_response = supabase.table("assessments").select("*").eq("id", attempt["assessment_id"]).execute()
        assessment = assessment_response.data[0]
        
        # Get answers with questions
        answers_response = supabase.table("assessment_answers").select(
            "*, assessment_questions(*, topic, difficulty)"
        ).eq("attempt_id", attempt_id).execute()
        
        # Analyze performance by topic
        topic_performance = {}
        
        for answer in answers_response.data:
            question = answer.get("assessment_questions")
            if question:
                topic = question.get("topic", assessment["topic"])
                if topic not in topic_performance:
                    topic_performance[topic] = {"correct": 0, "total": 0}
                
                topic_performance[topic]["total"] += 1
                if answer.get("is_correct"):
                    topic_performance[topic]["correct"] += 1
        
        # Detect gaps (topics with < 50% performance)
        detected_gaps = []
        
        for topic, performance in topic_performance.items():
            percentage = (performance["correct"] / performance["total"] * 100) if performance["total"] > 0 else 0
            
            if percentage < 50:
                # Check if gap already exists and not resolved
                existing = supabase.table("learning_gaps").select("*").eq(
                    "student_id", attempt["student_id"]
                ).eq("topic", topic).eq("subject", assessment["subject"]).is_("resolved_at", None).execute()
                
                if not existing.data:
                    gap_data = {
                        "student_id": attempt["student_id"],
                        "assessment_id": attempt["assessment_id"],
                        "topic": topic,
                        "subject": assessment["subject"],
                        "confidence": "high" if percentage < 30 else "medium",
                        "reason": f"Student scored {percentage:.0f}% on {topic} questions",
                        "current_level": "foundation" if percentage < 30 else "developing"
                    }
                    
                    gap_response = supabase.table("learning_gaps").insert(gap_data).execute()
                    detected_gaps.append(gap_response.data[0])
        
        return {
            "message": f"Detected {len(detected_gaps)} learning gaps",
            "gaps": detected_gaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{gap_id}/resolve")
async def resolve_learning_gap(gap_id: str):
    """Mark a learning gap as resolved"""
    supabase = get_supabase()
    
    try:
        response = supabase.table("learning_gaps").update({
            "resolved_at": "now()"
        }).eq("id", gap_id).execute()
        
        return {"message": "Learning gap marked as resolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
