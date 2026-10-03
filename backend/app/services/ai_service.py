from openai import OpenAI
from app.core.config import settings
from typing import Dict, Any, Optional
import json

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.provider = settings.AI_PROVIDER

    async def generate_lesson_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a lesson plan based on input parameters"""
        if not self.client:
            return self._mock_lesson_plan(params)

        prompt = self._build_lesson_plan_prompt(params)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates detailed, pedagogically sound lesson plans."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "content": content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": self._mock_lesson_plan(params)["content"]
            }

    async def generate_worksheet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a worksheet based on input parameters"""
        if not self.client:
            return self._mock_worksheet(params)

        prompt = self._build_worksheet_prompt(params)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates engaging worksheets with diverse question types."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "content": content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": self._mock_worksheet(params)["content"]
            }

    async def generate_quiz(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a quiz based on input parameters"""
        if not self.client:
            return self._mock_quiz(params)

        prompt = self._build_quiz_prompt(params)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates accurate assessments with clear questions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "content": content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": self._mock_quiz(params)["content"]
            }

    async def generate_remediation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate remediation content for learning gaps"""
        if not self.client:
            return self._mock_remediation(params)

        prompt = self._build_remediation_prompt(params)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates personalized remediation content to help students overcome learning gaps."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "content": content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": self._mock_remediation(params)["content"]
            }

    def _build_lesson_plan_prompt(self, params: Dict[str, Any]) -> str:
        return f"""Create a detailed lesson plan with the following parameters:
- Grade: {params.get('grade')}
- Subject: {params.get('subject')}
- Topic: {params.get('topic')}
- Duration: {params.get('duration')} minutes
- Learning Objectives: {params.get('learning_objectives', [])}
- Difficulty: {params.get('difficulty', 'developing')}
- Language: {params.get('language', 'en')}

Return a JSON object with this structure:
{{
  "learning_objectives": ["objective 1", "objective 2"],
  "introduction": "engaging introduction",
  "explanation": "clear explanation of the concept",
  "examples": ["example 1", "example 2"],
  "classroom_activity": "interactive activity description",
  "practice_questions": ["question 1", "question 2"],
  "assessment": "how to assess understanding",
  "homework": "homework assignment",
  "remediation_suggestions": "how to help struggling students",
  "differentiation": {{
    "foundation": "basic level content",
    "developing": "intermediate level content",
    "mastery": "advanced level content"
  }}
}}"""

    def _build_worksheet_prompt(self, params: Dict[str, Any]) -> str:
        return f"""Create a worksheet with the following parameters:
- Grade: {params.get('grade')}
- Subject: {params.get('subject')}
- Topic: {params.get('topic')}
- Number of questions: {params.get('num_questions', 10)}
- Question types: {params.get('question_types', ['mcq', 'short_answer'])}
- Difficulty: {params.get('difficulty', 'developing')}
- Language: {params.get('language', 'en')}

Return a JSON object with this structure:
{{
  "title": "Worksheet Title",
  "questions": [
    {{
      "question_text": "question text",
      "question_type": "mcq|fill_blank|short_answer|true_false|application",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "correct answer",
      "marks": 1,
      "difficulty": "foundation|developing|mastery"
    }}
  ]
}}"""

    def _build_quiz_prompt(self, params: Dict[str, Any]) -> str:
        return f"""Create a quiz with the following parameters:
- Grade: {params.get('grade')}
- Subject: {params.get('subject')}
- Topic: {params.get('topic')}
- Number of questions: {params.get('num_questions', 10)}
- Question types: {params.get('question_types', ['mcq'])}
- Difficulty: {params.get('difficulty', 'developing')}
- Language: {params.get('language', 'en')}

Return a JSON object with this structure:
{{
  "title": "Quiz Title",
  "questions": [
    {{
      "question_text": "question text",
      "question_type": "mcq|multiple_select|true_false|short_answer",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "correct answer",
      "marks": 1,
      "difficulty": "foundation|developing|mastery",
      "topic": "subtopic"
    }}
  ]
}}"""

    def _build_remediation_prompt(self, params: Dict[str, Any]) -> str:
        return f"""Create remediation content for a learning gap with the following parameters:
- Grade: {params.get('grade')}
- Subject: {params.get('subject')}
- Topic: {params.get('topic')}
- Current level: {params.get('current_level')}
- Target level: {params.get('target_level')}
- Reason for gap: {params.get('reason')}

Return a JSON object with this structure:
{{
  "title": "Remediation Plan Title",
  "simplified_explanation": "clear, simple explanation",
  "worked_examples": [
    {{
      "problem": "example problem",
      "solution": "step-by-step solution"
    }}
  ],
  "practice_questions": [
    {{
      "question": "practice question",
      "answer": "answer with explanation"
    }}
  ],
  "mini_worksheet": {{
    "questions": ["question 1", "question 2"],
    "answers": ["answer 1", "answer 2"]
  }},
  "concept_notes": "key concept summary",
  "revision_activity": "short revision activity",
  "estimated_time": "time to complete"
}}"""

    def _mock_lesson_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "content": {
                "learning_objectives": [
                    f"Understand {params.get('topic', 'the concept')}",
                    "Apply the concept to solve problems",
                    "Demonstrate mastery through practice"
                ],
                "introduction": f"Begin with an engaging hook about {params.get('topic', 'the topic')}",
                "explanation": f"Provide clear explanation of {params.get('topic', 'the concept')} with examples",
                "examples": ["Example 1: Basic application", "Example 2: Intermediate problem"],
                "classroom_activity": "Interactive group work",
                "practice_questions": ["Practice question 1", "Practice question 2"],
                "assessment": "Formative assessment through questions",
                "homework": "Practice problems from textbook",
                "remediation_suggestions": "Provide additional examples and one-on-one support",
                "differentiation": {
                    "foundation": "Basic concepts with visual aids",
                    "developing": "Standard difficulty problems",
                    "mastery": "Advanced application problems"
                }
            },
            "tokens_used": 0,
            "model": "mock"
        }

    def _mock_worksheet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        num_questions = params.get('num_questions', 5)
        return {
            "success": True,
            "content": {
                "title": f"{params.get('topic', 'Topic')} Worksheet",
                "questions": [
                    {
                        "question_text": f"Question {i+1} about {params.get('topic', 'the topic')}",
                        "question_type": "mcq",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "marks": 1,
                        "difficulty": params.get('difficulty', 'developing')
                    }
                    for i in range(num_questions)
                ]
            },
            "tokens_used": 0,
            "model": "mock"
        }

    def _mock_quiz(self, params: Dict[str, Any]) -> Dict[str, Any]:
        num_questions = params.get('num_questions', 5)
        return {
            "success": True,
            "content": {
                "title": f"{params.get('topic', 'Topic')} Quiz",
                "questions": [
                    {
                        "question_text": f"Question {i+1} about {params.get('topic', 'the topic')}",
                        "question_type": "mcq",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "marks": 1,
                        "difficulty": params.get('difficulty', 'developing'),
                        "topic": params.get('topic', 'General')
                    }
                    for i in range(num_questions)
                ]
            },
            "tokens_used": 0,
            "model": "mock"
        }

    def _mock_remediation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "content": {
                "title": f"Remediation for {params.get('topic', 'the topic')}",
                "simplified_explanation": f"Here's a simple explanation of {params.get('topic', 'the concept')}",
                "worked_examples": [
                    {
                        "problem": "Example problem",
                        "solution": "Step-by-step solution"
                    }
                ],
                "practice_questions": [
                    {
                        "question": "Practice question",
                        "answer": "Answer with explanation"
                    }
                ],
                "mini_worksheet": {
                    "questions": ["Question 1", "Question 2"],
                    "answers": ["Answer 1", "Answer 2"]
                },
                "concept_notes": f"Key notes about {params.get('topic', 'the topic')}",
                "revision_activity": "Short revision activity",
                "estimated_time": "30 minutes"
            },
            "tokens_used": 0,
            "model": "mock"
        }


ai_service = AIService()
