# Teacher Copilot - Project Guide

## Project Overview

Teacher Copilot is an AI-Powered Classroom OS - a complete educational platform for teachers and students with AI-generated content, assessment management, learning gap detection, and personalized remediation.

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Context (AuthContext)
- **Auth**: Supabase Auth
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase PostgreSQL
- **Auth**: Supabase Auth
- **AI**: OpenAI API (with mock fallback)
- **Storage**: Supabase Storage

## Project Structure

```
teacher-copilot/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── auth/          # Login/Register pages
│   │   │   ├── teacher/       # Teacher portal
│   │   │   │   ├── dashboard/
│   │   │   │   ├── classes/
│   │   │   │   ├── ai-copilot/
│   │   │   │   └── assessments/
│   │   │   └── student/       # Student portal
│   │   │       ├── dashboard/
│   │   │       └── classes/
│   │   ├── components/
│   │   │   ├── ui/            # Reusable UI components
│   │   │   └── features/      # Feature-specific components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utilities
│   │   ├── services/          # API calls
│   │   └── types/             # TypeScript types
│   └── docs/                  # Documentation
├── backend/
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── classes.py     # Class management
│   │   │   ├── ai.py          # AI generation
│   │   │   └── assessments.py # Assessment management
│   │   ├── core/              # Configuration
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Business logic
│   │   │   └── ai_service.py  # AI service with mock fallback
│   │   └── repositories/      # Database operations
│   ├── supabase/
│   │   └── migrations/        # SQL migrations
│   └── seed/                 # Seed data scripts
└── README.md
```

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key (optional)
AI_PROVIDER=openai
APP_ENV=development
APP_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Features Implemented

### ✅ Completed
1. Project structure (frontend + backend)
2. Database schema with normalized tables
3. Authentication system (teacher/student roles)
4. Teacher portal with dashboard
5. Student portal with dashboard
6. Class management (create, join, view)
7. AI Copilot with generation features (lesson plans, worksheets, quizzes, remediation)
8. Assessment engine (create, list, with AI generation)
9. Premium UI/UX design system
10. Responsive layouts

### 🚧 Partially Implemented
- API endpoints need frontend integration
- Assessment submission flow needs completion
- Learning gap detection needs implementation
- Remediation assignment needs implementation
- Progress tracking needs implementation

### ❌ Not Yet Implemented
- Resource management (file uploads)
- Learning analytics dashboard
- Learning gap detection engine
- Remediation engine
- Retest engine
- PDF/PPT exports
- Notification system
- RLS policies (SQL written, needs to be applied)
- Seed data script

## Database Schema

Key tables and relationships:
- `profiles` → `classes` (teacher owns classes)
- `classes` → `class_members` (students join classes)
- `classes` → `assessments` (assessments belong to classes)
- `assessments` → `assessment_questions` (questions in assessments)
- `assessment_attempts` → `assessment_answers` (student submissions)
- `assessment_attempts` → `learning_gaps` (gap detection)
- `learning_gaps` → `remediation_plans` (remediation generation)
- `remediation_plans` → `remediation_assignments` (assign to students)
- `remediation_assignments` → `retests` (retest after remediation)

## AI Service

The AI service includes:
- Lesson plan generation
- Worksheet generation
- Quiz generation
- Remediation content generation

**Important**: The service has a mock fallback when OpenAI API key is not provided. This allows the application to work without an API key for demonstration purposes.

## Authentication Flow

1. User registers with email/password and role (teacher/student)
2. Supabase Auth handles authentication
3. Profile is created in `profiles` table
4. Role-based routing redirects to appropriate portal
5. Protected routes check user role

## Class Join Flow

1. Teacher creates class → generates 6-character code (e.g., "TC8A7K")
2. Teacher shares code with students
3. Student enters code to join class
4. System validates code and adds student to `class_members`

## Assessment Flow

1. Teacher creates assessment (manually or with AI)
2. Teacher assigns to class
3. Student sees assessment in dashboard
4. Student starts assessment → timer begins
5. Student submits answers
6. System auto-evaluates objective questions
7. Results stored and displayed

## Learning Gap Flow (Planned)

1. System analyzes assessment results
2. Detects topics with low performance
3. Creates learning gap record
4. AI generates remediation content
5. Teacher reviews and assigns
6. Student completes remediation
7. Retest becomes available
8. System tracks improvement

## Testing the Application

### Manual Testing Flow

1. **Setup Supabase**
   - Create project
   - Run migration SQL
   - Get API credentials

2. **Configure Environment**
   - Set up backend .env
   - Set up frontend .env.local

3. **Start Servers**
   - Backend: `python main.py` (port 8000)
   - Frontend: `npm run dev` (port 3000)

4. **Test Teacher Flow**
   - Register as teacher
   - Create class
   - Copy class code
   - Generate lesson plan with AI
   - Create assessment with AI
   - Assign assessment

5. **Test Student Flow**
   - Register as student
   - Join class with code
   - Take assessment
   - View results

## Known Limitations

1. AI features require OpenAI API key (has mock fallback)
2. RLS policies not yet applied to Supabase
3. File upload not implemented
4. PDF/PPT export not implemented
5. Real-time features not implemented
6. Email notifications not implemented
7. Some API endpoints need frontend integration

## Next Steps for Completion

1. Apply RLS policies to Supabase
2. Implement learning gap detection logic
3. Build remediation assignment flow
4. Implement retest system
5. Add progress tracking visualization
6. Implement file upload for resources
7. Add PDF export functionality
8. Create seed data script for demo
9. Add comprehensive error handling
10. Implement notification system

## Design System

The UI follows a premium, modern design:
- Clean typography with good hierarchy
- Spacious layouts with proper whitespace
- Subtle animations and transitions
- Responsive design (mobile-first)
- Dark mode support
- Accessible components
- Consistent color palette

Color scheme:
- Primary: Blue (blue-600)
- Success: Green (green-500)
- Warning: Orange (orange-500)
- Error: Red (red-500)
- Neutral: Gray scale

## API Endpoints

### Authentication
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- GET /auth/profile

### Classes
- POST /classes
- GET /classes
- GET /classes/{id}
- PUT /classes/{id}
- DELETE /classes/{id}
- POST /classes/{id}/join
- POST /classes/join-by-code
- GET /classes/{id}/students
- DELETE /classes/{id}/students/{student_id}

### AI
- POST /ai/lesson-plan
- POST /ai/worksheet
- POST /ai/quiz
- POST /ai/remediation

### Assessments
- POST /assessments
- GET /assessments
- GET /assessments/{id}
- POST /assessments/{id}/start
- POST /assessments/{id}/submit
- GET /assessments/{id}/attempts
- GET /assessments/student/{student_id}

## Important Notes

- Never commit API keys or secrets
- Use environment variables for all configuration
- Test both teacher and student flows
- Ensure role-based access control
- Validate all user inputs
- Handle errors gracefully
- Provide loading states for async operations
- Make the UI responsive
- Follow the existing code patterns
