from app.celery import celery_app
from app.services.groq_analysis import groq_service
from app.services.ai_analysis import ai_service
import time

@celery_app.task
def analyze_standup_response_task(standup_data):
    """Background task for standup analysis"""
    try:
        # Use Groq if available, otherwise fall back to OpenAI
        if hasattr(groq_service, 'analyze_standup_response'):
            return groq_service.analyze_standup_response(standup_data)
        else:
            return ai_service.analyze_standup_response(standup_data)
    except Exception as e:
        return {"error": str(e), "analysis": "Background analysis failed"}

@celery_app.task
def generate_session_summary_task(session_data, responses):
    """Background task for session summary generation"""
    try:
        if hasattr(groq_service, 'generate_session_summary'):
            return groq_service.generate_session_summary(session_data, responses)
        else:
            return ai_service.generate_session_summary(session_data, responses)
    except Exception as e:
        return {"error": str(e), "summary": "Background summary generation failed"}
