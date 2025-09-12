from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="FlowCore API", version="0.0.1")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock services for testing
class MockJiraService:
    pass

class MockGroqService:
    def analyze_standup_response(self, data):
        return {
            "sentiment_score": 0.8,
            "sentiment_label": "positive",
            "risk_level": "low",
            "confidence_score": 0.9,
            "key_achievements": ["Completed task A", "Started task B"],
            "planned_work": ["Finish task B", "Start task C"],
            "critical_blockers": ["None"],
            "suggested_actions": ["Continue current work"],
            "productivity_insight": "Developer is making good progress"
        }
    
    def generate_session_summary(self, session_data, responses):
        return {
            "summary": "Team is progressing well with no major blockers",
            "key_insights": ["Good momentum", "No critical issues"]
        }

# Use mock services for now
jira_service = MockJiraService()
ai_service = MockGroqService()

# Pydantic models
class StandupResponse(BaseModel):
    developer_email: str
    what_did_i_do: str
    what_will_i_do: str
    blockers: str
    project_id: Optional[int] = None
    session_id: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "FlowCore API DEPLOYED SUCCESSFULLY!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "deployment": "successful"}

@app.post("/webhook/standup")
async def receive_standup_response(response: StandupResponse):
    return {
        "message": f"Received standup from {response.developer_email}",
        "analysis": ai_service.analyze_standup_response(response.dict())
    }

import os
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
