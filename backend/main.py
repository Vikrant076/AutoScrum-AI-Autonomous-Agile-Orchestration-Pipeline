import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from app.models import get_db, init_db, StandupResponse, StandupSession, Project
from app.services.groq_analysis import groq_service
from app.services.ai_analysis import ai_service
from app.services.jira_service import JiraService

# Initialize database
init_db()

app = FastAPI(
    title="AutoScrum API",
    description="AI-Powered Agile Orchestration Backend",
    version="1.0.0"
)

# Get frontend URL from environment or use default
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.environ.get("RAILWAY_STATIC_URL", "http://localhost:8000")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AutoScrum API is running",
        "version": "1.0.0",
        "docs": f"{BACKEND_URL}/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "frontend_url": FRONTEND_URL}

# Standup endpoints
@app.post("/api/standup/analyze")
async def analyze_standup(response_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Analyze a single standup response"""
    try:
        # Save to database first
        db_response = StandupResponse(
            developer_email=response_data.get('developer_email'),
            developer_name=response_data.get('developer_name'),
            what_did_i_do=response_data.get('what_did_i_do'),
            what_will_i_do=response_data.get('what_will_i_do'),
            blockers=response_data.get('blockers')
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        
        # Analyze with AI
        analysis_data = response_data.copy()
        analysis_data.update({
            'response_id': db_response.id,
            'session_id': response_data.get('session_id'),
            'project_id': response_data.get('project_id')
        })
        
        # Use Groq if available, otherwise OpenAI
        try:
            analysis_result = groq_service.analyze_standup_response(analysis_data)
        except:
            analysis_result = ai_service.analyze_standup_response(analysis_data)
        
        # Update response with analysis
        if 'error' not in analysis_result:
            db_response.sentiment_score = analysis_result.get('sentiment_score')
            db_response.risk_level = analysis_result.get('risk_level')
            db_response.confidence_score = analysis_result.get('confidence_score')
            db_response.ai_analysis = analysis_result
            db_response.has_blockers = bool(analysis_result.get('critical_blockers'))
            db.commit()
        
        return analysis_result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/standup/responses")
async def get_standup_responses(db: Session = Depends(get_db)):
    """Get all standup responses"""
    responses = db.query(StandupResponse).all()
    return responses

# Jira endpoints
@app.get("/api/jira/issues/{project_key}")
async def get_jira_issues(project_key: str):
    """Get Jira issues for a project"""
    try:
        jira_service = JiraService(
            base_url=os.environ.get("JIRA_URL"),
            email=os.environ.get("JIRA_EMAIL"),
            api_token=os.environ.get("JIRA_API_TOKEN")
        )
        issues = jira_service.get_in_progress_issues(project_key)
        return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI endpoints
@app.get("/api/ai/models")
async def get_ai_models():
    """Get available AI models"""
    return {
        "openai_available": bool(os.environ.get("OPENAI_API_KEY")),
        "groq_available": bool(os.environ.get("GROQ_API_KEY")),
        "default_model": os.environ.get("GROQ_MODEL", "gpt-3.5-turbo")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
