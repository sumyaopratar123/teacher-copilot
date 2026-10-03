# Teacher Copilot - Setup Guide

## Quick Start

This guide will help you set up Teacher Copilot locally for development and testing.

## Prerequisites

- Node.js 18+ 
- Python 3.10+
- Supabase account (free tier works)
- (Optional) OpenAI API key for AI features

## Step 1: Set up Supabase

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose a name (e.g., "teacher-copilot")
4. Choose a database password (save it somewhere safe)
5. Wait for the project to be ready (1-2 minutes)
6. Go to Settings > API
7. Copy:
   - Project URL
   - anon/public key
   - service_role key (for backend)

8. Go to SQL Editor
9. Create a new query
10. Copy and paste the contents of `backend/supabase/migrations/001_initial_schema.sql`
11. Run the query
12. Create another query
13. Copy and paste the contents of `backend/supabase/migrations/002_rls_policies.sql`
14. Run the query

## Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy from .env.example and fill in your values
```

Create `backend/.env` with:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key  # Optional, but recommended
AI_PROVIDER=openai
APP_ENV=development
APP_PORT=8000
FRONTEND_URL=http://localhost:3000
```

Start the backend:
```bash
python main.py
```

Backend will run on http://localhost:8000
- API docs: http://localhost:8000/docs

## Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

Create `frontend/.env.local` with:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:
```bash
npm run dev
```

Frontend will run on http://localhost:3000

## Step 4: Seed Demo Data (Optional)

To populate the database with demo data for testing:

```bash
cd backend
# Make sure your .env has SUPABASE_SERVICE_ROLE_KEY
python seed/seed_demo.py
```

This will create:
- 1 Teacher account (teacher@demo.com / demo123)
- 3 Student accounts (alice@demo.com, bob@demo.com, charlie@demo.com / demo123)
- 1 Class (8-A Mathematics)
- 3 Assessments
- Student attempts with varying scores
- Learning gaps
- Remediation plans

## Step 5: Test the Application

### Teacher Flow

1. Go to http://localhost:3000
2. Click "Sign up"
3. Register as a teacher (or use teacher@demo.com / demo123 if seeded)
4. You'll be redirected to the teacher dashboard
5. Create a class:
   - Go to "My Classes"
   - Click "Create Class"
   - Fill in details (e.g., "8-A Mathematics", Grade 8, Mathematics)
   - Copy the class code (e.g., "TC8A7K")
6. Generate content with AI:
   - Go to "AI Copilot"
   - Select "Lesson Plan"
   - Fill in: Grade 8, Mathematics, Linear Equations, Duration 45
   - Click "Generate"
   - Review the generated content
7. Create an assessment:
   - Go to "Assessments"
   - Click "Create Assessment"
   - Fill in details
   - Or use "Generate with AI" to auto-generate questions
   - Create the assessment

### Student Flow

1. Open a new browser or incognito window
2. Go to http://localhost:3000
3. Click "Sign up"
4. Register as a student (or use alice@demo.com / demo123 if seeded)
5. You'll be redirected to the student dashboard
6. Join a class:
   - Go to "My Classes"
   - Click "Join Class"
   - Enter the class code from the teacher (e.g., "TC8A7K")
7. Take an assessment:
   - Go to "Assessments"
   - Click on an available assessment
   - Answer questions
   - Submit
   - View results

## Troubleshooting

### Backend won't start
- Make sure virtual environment is activated
- Check that all dependencies are installed
- Verify .env file exists and has correct values
- Check port 8000 is not in use

### Frontend won't start
- Make sure dependencies are installed
- Verify .env.local file exists
- Check port 3000 is not in use

### Supabase connection errors
- Verify SUPABASE_URL and keys are correct
- Make sure migrations were run successfully
- Check Supabase project is active (not paused)

### AI generation not working
- Check OPENAI_API_KEY is set in backend .env
- If no key is set, the app will use mock data (still works for demo)
- Verify OpenAI API key has credits

### Authentication errors
- Make sure Supabase Auth is enabled
- Check email confirmation settings in Supabase
- For demo, you can disable email confirmation in Supabase settings

## Development Tips

- Backend: Changes require restarting the server
- Frontend: Next.js hot-reloads automatically
- Database: Use Supabase dashboard to view data
- API: Visit http://localhost:8000/docs to test endpoints directly

## Next Steps

After basic setup:
1. Implement the remaining features (analytics, learning gap detection, etc.)
2. Add real file upload for resources
3. Implement PDF export
4. Add email notifications
5. Deploy to production (Vercel for frontend, Render for backend)

## Support

If you encounter issues:
1. Check the logs in the terminal
2. Verify all environment variables are set
3. Ensure Supabase migrations were run
4. Check the AGENTS.md file for detailed project information
