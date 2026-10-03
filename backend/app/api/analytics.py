from fastapi import APIRouter, HTTPException
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/teacher/{teacher_id}")
async def get_teacher_analytics(teacher_id: str):
    """Get comprehensive analytics for a teacher"""
    supabase = get_supabase()
    
    try:
        # Get teacher's classes
        classes_response = supabase.table("classes").select("*").eq("teacher_id", teacher_id).execute()
        classes = classes_response.data
        
        class_ids = [c["id"] for c in classes]
        
        # Get total students
        students_response = supabase.table("class_members").select("*").in_("class_id", class_ids).execute()
        total_students = len(set(s["student_id"] for s in students_response.data))
        
        # Get assessments
        assessments_response = supabase.table("assessments").select("*").in_("class_id", class_ids).execute()
        total_assessments = len(assessments_response.data)
        
        # Get assessment attempts
        attempts_response = supabase.table("assessment_attempts").select("*").in_(
            "assessment_id", [a["id"] for a in assessments_response.data]
        ).execute()
        
        # Calculate average performance
        total_score = 0
        attempts_with_score = 0
        for attempt in attempts_response.data:
            if attempt.get("percentage"):
                total_score += attempt["percentage"]
                attempts_with_score += 1
        
        average_performance = (total_score / attempts_with_score) if attempts_with_score > 0 else 0
        
        # Get learning gaps
        gaps_response = supabase.table("learning_gaps").select("*").in_(
            "student_id", [s["student_id"] for s in students_response.data]
        ).is_("resolved_at", None).execute()
        
        # Get topic performance
        topic_performance = {}
        for attempt in attempts_response.data:
            assessment = next((a for a in assessments_response.data if a["id"] == attempt["assessment_id"]), None)
            if assessment:
                topic = assessment["topic"]
                if topic not in topic_performance:
                    topic_performance[topic] = {"total": 0, "count": 0}
                if attempt.get("percentage"):
                    topic_performance[topic]["total"] += attempt["percentage"]
                    topic_performance[topic]["count"] += 1
        
        topic_averages = {}
        for topic, data in topic_performance.items():
            topic_averages[topic] = data["total"] / data["count"] if data["count"] > 0 else 0
        
        return {
            "total_students": total_students,
            "total_classes": len(classes),
            "total_assessments": total_assessments,
            "total_attempts": len(attempts_response.data),
            "average_performance": round(average_performance, 2),
            "active_learning_gaps": len(gaps_response.data),
            "topic_performance": topic_averages,
            "classes": classes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class/{class_id}")
async def get_class_analytics(class_id: str, teacher_id: str):
    """Get analytics for a specific class"""
    supabase = get_supabase()
    
    try:
        # Verify teacher owns the class
        class_response = supabase.table("classes").select("*").eq("id", class_id).eq("teacher_id", teacher_id).execute()
        
        if not class_response.data:
            raise HTTPException(status_code=403, detail="You can only view analytics for your own classes")
        
        class_data = class_response.data[0]
        
        # Get students
        students_response = supabase.table("class_members").select(
            "student_id, profiles(*)"
        ).eq("class_id", class_id).execute()
        
        # Get assessments
        assessments_response = supabase.table("assessments").select("*").eq("class_id", class_id).execute()
        
        # Get attempts
        attempts_response = supabase.table("assessment_attempts").select("*").in_(
            "assessment_id", [a["id"] for a in assessments_response.data]
        ).execute()
        
        # Calculate class average
        total_score = 0
        attempts_with_score = 0
        for attempt in attempts_response.data:
            if attempt.get("percentage"):
                total_score += attempt["percentage"]
                attempts_with_score += 1
        
        class_average = (total_score / attempts_with_score) if attempts_with_score > 0 else 0
        
        # Get learning gaps
        gaps_response = supabase.table("learning_gaps").select("*").in_(
            "student_id", [s["student_id"] for s in students_response.data]
        ).is_("resolved_at", None).execute()
        
        # Get completion rate
        completion_rate = 0
        if assessments_response.data:
            total_possible = len(assessments_response.data) * len(students_response.data)
            completion_rate = (len(attempts_response.data) / total_possible * 100) if total_possible > 0 else 0
        
        return {
            "class": class_data,
            "student_count": len(students_response.data),
            "students": students_response.data,
            "assessment_count": len(assessments_response.data),
            "attempts_count": len(attempts_response.data),
            "class_average": round(class_average, 2),
            "completion_rate": round(completion_rate, 2),
            "learning_gaps_count": len(gaps_response.data),
            "learning_gaps": gaps_response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_id}")
async def get_student_analytics(student_id: str):
    """Get analytics for a student"""
    supabase = get_supabase()
    
    try:
        # Get attempts
        attempts_response = supabase.table("assessment_attempts").select(
            "*, assessments(*)"
        ).eq("student_id", student_id).execute()
        
        # Calculate overall average
        total_score = 0
        attempts_with_score = 0
        for attempt in attempts_response.data:
            if attempt.get("percentage"):
                total_score += attempt["percentage"]
                attempts_with_score += 1
        
        overall_average = (total_score / attempts_with_score) if attempts_with_score > 0 else 0
        
        # Get progress
        progress_response = supabase.table("student_progress").select("*").eq("student_id", student_id).execute()
        
        # Get learning gaps
        gaps_response = supabase.table("learning_gaps").select("*").eq("student_id", student_id).is_("resolved_at", None).execute()
        
        # Get retests
        retests_response = supabase.table("retests").select("*").eq("student_id", student_id).execute()
        
        # Calculate improvement
        total_improvement = 0
        retests_with_improvement = 0
        for retest in retests_response.data:
            if retest.get("improvement"):
                total_improvement += retest["improvement"]
                retests_with_improvement += 1
        
        average_improvement = (total_improvement / retests_with_improvement) if retests_with_improvement > 0 else 0
        
        return {
            "total_attempts": len(attempts_response.data),
            "overall_average": round(overall_average, 2),
            "progress_records": progress_response.data,
            "active_learning_gaps": len(gaps_response.data),
            "learning_gaps": gaps_response.data,
            "total_retests": len(retests_response.data),
            "average_improvement": round(average_improvement, 2),
            "attempts": attempts_response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
