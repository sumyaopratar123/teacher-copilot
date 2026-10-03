from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, classes, ai, assessments, learning_gaps, remediation, retests, progress, analytics, resources, notifications

app = FastAPI(
    title="Teacher Copilot API",
    version="1.0.0",
    description="AI-Powered Classroom OS API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(ai.router)
app.include_router(assessments.router)
app.include_router(learning_gaps.router)
app.include_router(remediation.router)
app.include_router(retests.router)
app.include_router(progress.router)
app.include_router(analytics.router)
app.include_router(resources.router)
app.include_router(notifications.router)


@app.get("/")
async def root():
    return {
        "message": "Teacher Copilot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)
