from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from services.jira_service import JiraService
from services.groq_analysis import groq_service as ai_service  # Changed to Groq service

# Load environment variables
load_dotenv()

# Create the FastAPI application
app = FastAPI(title="FlowCore API", description="The Brains behind the Auto-Agile Pipeline", version="0.0.1")

# Allow our frontend to talk to the backend (important for later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], # Streamlit runs on this port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A simple in-memory "database" for our MVP. We'll replace this with PostgreSQL later.
fake_db = {}

# Pydantic models define the structure of incoming/outgoing data
class StandupResponse(BaseModel):
    developer_email: str
    what_did_i_do: str
    what_will_i_do: str
    blockers: str
    project_id: Optional[int] = None  # Added for AI analysis
    session_id: Optional[int] = None  # Added for AI analysis

class StandupSummary(BaseModel):
    summary: str

class AIAnalysisResult(BaseModel):
    sentiment_score: float
    sentiment_label: str
    risk_level: str
    confidence_score: float
    key_achievements: List[str]
    planned_work: List[str]
    critical_blockers: List[str]
    suggested_actions: List[str]
    productivity_insight: str
    metadata: Optional[dict] = None

# --- API Routes ---

@app.get("/")
async def root():
    return {"message": "Welcome to the FlowCore API! The future of Agile automation."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# This endpoint will receive standup responses from Slack
@app.post("/webhook/standup", response_model=StandupSummary)
async def receive_standup_response(response: StandupResponse, background_tasks: BackgroundTasks):
    print(f"Received standup from {response.developer_email}")
    
    # For now, just store it in our fake DB
    if 'standups' not in fake_db:
        fake_db['standups'] = []
    fake_db['standups'].append(response.dict())

    # Analyze the standup response with Groq AI
    analysis_result = ai_service.analyze_standup_response(response.dict())
    print(f"AI Analysis Result: {analysis_result}")

    # In a real scenario, we would check if we have all responses, then trigger the summary
    # Let's just simulate it for one user for now.
    background_tasks.add_task(generate_and_send_summary, [response])
    return StandupSummary(summary="Thank you for your standup update! A summary will be generated shortly.")

@app.post("/analyze-standup", response_model=AIAnalysisResult)
async def analyze_standup(response: StandupResponse):
    """Endpoint to analyze a single standup response with Groq AI"""
    try:
        analysis_result = ai_service.analyze_standup_response(response.dict())
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
            
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.post("/generate-summary")
async def generate_summary(session_data: dict, responses: List[StandupResponse]):
    """Endpoint to generate a session summary with Groq AI"""
    try:
        # Convert responses to dict format
        responses_dict = [r.dict() for r in responses]
        
        summary_result = ai_service.generate_session_summary(session_data, responses_dict)
        
        if "error" in summary_result:
            raise HTTPException(status_code=500, detail=summary_result["error"])
            
        return summary_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

def generate_and_send_summary(responses: List[StandupResponse]):
    """Background task to generate summary. This is where Celery will go later."""
    print("Background task: Generating summary...")
    
    # Convert to dict format for the AI service
    responses_dict = [r.dict() for r in responses]
    
    # Create session data
    session_data = {
        "date": "2023-01-01",  # You might want to use actual date
        "participant_count": len(responses)
    }
    
    # Generate summary using Groq AI
    summary_result = ai_service.generate_session_summary(session_data, responses_dict)
    
    if "error" not in summary_result:
        summary = summary_result["summary"]
        print(f"SUMMARY:\n{summary}")
        # In the next steps, we will send this to Slack instead of just printing it.
        print("Mock: Summary would now be posted to Slack channel.")
    else:
        print(f"Failed to generate summary: {summary_result['error']}")

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    # Initialize our "services"
    print("FlowCore API is starting up...")
    print(f"Using Groq AI with model: {ai_service.default_model}")
    # This is where we would initialize a real database connection
# Add this at the VERY BOTTOM of the file
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)    