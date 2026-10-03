# Teacher Copilot

AI-Powered Classroom OS - A complete AI-powered classroom management and personalized learning platform for teachers and students.

## 🎓 Features

### Teacher Portal
- **Dashboard**: Overview of classroom health, student performance, and activity
- **Class Management**: Create classes, generate class codes, manage students
- **AI Copilot**: Generate lesson plans, worksheets, quizzes, and remediation content
- **Assessment Engine**: Create quizzes, tests, and assignments with AI assistance
- **Learning Analytics**: Track class performance, topic mastery, and learning gaps
- **Remediation System**: AI-generated personalized support for struggling students
- **Retest Engine**: Track improvement after remediation

### Student Portal
- **Dashboard**: View enrolled classes, pending assignments, and progress
- **Class Management**: Join classes using class codes
- **Assessment Taking**: Complete quizzes and tests with timer
- **Progress Tracking**: View learning levels and topic mastery
- **Remediation Access**: Receive and complete personalized remediation activities

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with shadcn/ui patterns
- **State Management**: React Context
- **Authentication**: Supabase Auth
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth
- **AI**: OpenAI API (with provider abstraction)
- **Storage**: Supabase Storage

## 📁 Project Structure

```
teacher-copilot/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── lib/             # Utilities
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript types
│   └── docs/                # Documentation
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── ai/             # AI services
│   ├── supabase/
│   │   └── migrations/     # Database migrations
│   └── seed/               # Seed data scripts
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Supabase account
- OpenAI API key (optional, for AI features)

### 1. Set up Supabase

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Go to Settings > API
4. Copy the Project URL and anon/public key
5. Run the migration from `backend/supabase/migrations/001_initial_schema.sql`

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# SUPABASE_URL=your_supabase_url
# SUPABASE_ANON_KEY=your_supabase_anon_key
# SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
# OPENAI_API_KEY=your_openai_api_key (optional)

# Run the server
python main.py
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
# Copy from docs/env-config.md for reference
# NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

The frontend will run on `http://localhost:3000`

## 🎯 Demo Flow

1. **Teacher Registration**
   - Sign up as a teacher
   - Create a class (e.g., "8-A Mathematics")
   - Copy the generated class code (e.g., "TC8A7K")

2. **Student Registration**
   - Sign up as a student
   - Join class using the class code

3. **AI Content Generation**
   - Teacher opens AI Copilot
   - Selects: Grade 8, Mathematics, Linear Equations
   - Generates lesson plan, worksheet, and quiz
   - Reviews and approves content

4. **Assessment Creation**
   - Teacher creates assessment from generated quiz
   - Assigns to class

5. **Student Assessment**
   - Student takes the quiz
   - Submits answers
   - Views results

6. **Learning Gap Detection**
   - System analyzes performance
   - Detects learning gaps (e.g., Linear Equations at 42%)
   - AI generates remediation content

7. **Remediation**
   - Teacher reviews and assigns remediation
   - Student completes remediation activities
   - Retest becomes available

8. **Progress Tracking**
   - Student takes retest
   - System shows improvement (e.g., 40% → 80%)
   - Teacher analytics updated

## 🔐 Security

- Row Level Security (RLS) configured in Supabase
- Teacher-student data isolation
- API key management via environment variables
- No hardcoded credentials

## 📊 Database Schema

Key tables:
- `profiles` - User profiles
- `classes` - Class information
- `class_members` - Student-class relationships
- `assessments` - Quizzes, tests, assignments
- `assessment_questions` - Assessment questions
- `assessment_attempts` - Student submissions
- `learning_gaps` - Detected learning gaps
- `remediation_plans` - AI-generated remediation
- `retests` - Retest results
- `student_progress` - Progress tracking

See `backend/supabase/migrations/001_initial_schema.sql` for complete schema.

## 🎨 Design System

The UI follows a modern, clean design inspired by Linear, Notion, and premium EdTech products:
- Premium dark/light theme support
- Clean typography
- Strong visual hierarchy
- Spacious layouts
- Subtle animations
- Responsive design (mobile, tablet, desktop)

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel deploy
```

### Backend (Render/Heroku)
```bash
cd backend
# Deploy to Render/Heroku with Python support
```

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

This is a MVP project. Key areas for enhancement:
- Complete RLS policies
- Add more AI providers
- Implement PDF/PPT export
- Add notification system
- Build analytics dashboard
- Add real-time features

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

Built with:
- Next.js
- FastAPI
- Supabase
- OpenAI
- Tailwind CSS
