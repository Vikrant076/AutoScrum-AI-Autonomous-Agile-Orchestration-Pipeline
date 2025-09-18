import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models import SessionLocal, AIAnalysisLog

# Try to import other AI services
try:
    from app.services.groq_analysis import groq_service
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from app.services.deepseek_analysis import deepseek_service
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

class AIAnalysisService:
    def __init__(self):
        self.default_model = "deepseek-chat"  # Default to DeepSeek
    
    def analyze_standup_response(self, standup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze standup response using available AI services (priority: DeepSeek > Groq)"""
        
        # Try DeepSeek first
        if DEEPSEEK_AVAILABLE:
            try:
                return deepseek_service.analyze_standup_response(standup_data)
            except Exception as e:
                print(f"DeepSeek analysis failed: {e}")
        
        # Try Groq as fallback
        if GROQ_AVAILABLE:
            try:
                return groq_service.analyze_standup_response(standup_data)
            except Exception as e:
                print(f"Groq analysis failed: {e}")
        
        # Fallback mock response
        return self._get_mock_response()

    def generate_session_summary(self, session_data: Dict[str, Any], responses: List[Dict]) -> Dict[str, Any]:
        """Generate session summary using available AI services"""
        
        # Try DeepSeek first
        if DEEPSEEK_AVAILABLE:
            try:
                return deepseek_service.generate_session_summary(session_data, responses)
            except Exception as e:
                print(f"DeepSeek summary failed: {e}")
        
        # Try Groq as fallback
        if GROQ_AVAILABLE:
            try:
                return groq_service.generate_session_summary(session_data, responses)
            except Exception as e:
                print(f"Groq summary failed: {e}")
        
        # Fallback mock summary
        return {"summary": self._get_mock_summary()}

    def _get_mock_response(self) -> Dict[str, Any]:
        """Fallback mock response when no AI service is available"""
        return {
            "sentiment_score": 0.5,
            "sentiment_label": "positive",
            "risk_level": "low",
            "confidence_score": 0.8,
            "key_achievements": ["Completed backend API development"],
            "planned_work": ["Continue with database integration"],
            "critical_blockers": [],
            "suggested_actions": ["Review code quality", "Plan for testing"],
            "productivity_insight": "Developer is making good progress"
        }

    def _get_mock_summary(self) -> str:
        """Fallback mock summary"""
        return """
        **Daily Standup Summary**
        
        **Overall Progress**: Team is making good progress on current sprint goals.
        **Key Achievements**: Backend API development completed, login functionality implemented.
        **Planned Work**: Database integration, testing phase preparation.
        **Blockers**: No critical blockers reported.
        **Recommendations**: Continue current pace, focus on testing.
        """

# Global instance
ai_service = AIAnalysisService()
