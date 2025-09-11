import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models import SessionLocal, AIAnalysisLog

try:
    import groq
except ImportError:
    print("Groq package not installed. Please install it with: pip install groq")
    groq = None

class GroqAnalysisService:
    def __init__(self):
        if groq is None:
            raise ImportError("Groq package is not installed. Please install it with: pip install groq")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        self.client = groq.Groq(api_key=api_key)
        self.default_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Free model option

    def analyze_standup_response(self, standup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single standup response using Groq AI"""
        prompt = self._build_analysis_prompt(standup_data)

        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )

            processing_time_ms = int((time.time() - start_time) * 1000)
            analysis_result = self._parse_ai_response(response.choices[0].message.content)

            # Log the analysis
            self._log_analysis(
                project_id=standup_data.get('project_id'),
                session_id=standup_data.get('session_id'),
                response_id=standup_data.get('response_id'),
                model_used=self.default_model,
                tokens_consumed=response.usage.total_tokens,
                analysis_type="standup_analysis",
                processing_time_ms=processing_time_ms,
                success=True
            )

            return {
                **analysis_result,
                "metadata": {
                    "model": self.default_model,
                    "tokens_used": response.usage.total_tokens,
                    "processing_time_ms": processing_time_ms
                }
            }

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            self._log_analysis(
                project_id=standup_data.get('project_id'),
                session_id=standup_data.get('session_id'),
                response_id=standup_data.get('response_id'),
                model_used=self.default_model,
                tokens_consumed=0,
                analysis_type="standup_analysis",
                processing_time_ms=processing_time_ms,
                success=False,
                error_message=str(e)
            )
            return {"error": str(e), "analysis": "AI analysis failed"}

    def generate_session_summary(self, session_data: Dict[str, Any], responses: List[Dict]) -> Dict[str, Any]:
        """Generate AI-powered session summary using Groq"""
        prompt = self._build_summary_prompt(session_data, responses)

        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.5
            )

            processing_time_ms = int((time.time() - start_time) * 1000)
            summary = response.choices[0].message.content

            # Log the analysis
            self._log_analysis(
                project_id=session_data.get('project_id'),
                session_id=session_data.get('session_id'),
                model_used=self.default_model,
                tokens_consumed=response.usage.total_tokens,
                analysis_type="session_summary",
                processing_time_ms=processing_time_ms,
                success=True
            )

            return {
                "summary": summary,
                "metadata": {
                    "model": self.default_model,
                    "tokens_used": response.usage.total_tokens,
                    "processing_time_ms": processing_time_ms
                }
            }

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            self._log_analysis(
                project_id=session_data.get('project_id'),
                session_id=session_data.get('session_id'),
                model_used=self.default_model,
                tokens_consumed=0,
                analysis_type="session_summary",
                processing_time_ms=processing_time_ms,
                success=False,
                error_message=str(e)
            )
            return {"error": str(e), "summary": "AI summary generation failed"}

    def _build_analysis_prompt(self, standup_data: Dict[str, Any]) -> str:
        """Build the prompt for standup analysis"""
        return f"""
        Analyze this daily standup response from a software development team and provide a JSON response with:
        {{
            "sentiment_score": -1.0 to 1.0 (negative to positive),
            "sentiment_label": "negative/neutral/positive",
            "risk_level": "low/medium/high/critical",
            "confidence_score": 0.0 to 1.0,
            "key_achievements": ["list", "of", "key", "accomplishments"],
            "planned_work": ["list", "of", "planned", "tasks"],
            "critical_blockers": ["list", "of", "critical", "blockers", "if any"],
            "suggested_actions": ["actionable", "suggestions", "for", "scrum", "master"],
            "productivity_insight": "brief insight about developer productivity"
        }}

        DEVELOPER: {standup_data.get('developer_name', standup_data.get('developer_email', 'Unknown'))}
        WHAT I DID: {standup_data.get('what_did_i_do', 'No information')}
        WHAT I WILL DO: {standup_data.get('what_will_i_do', 'No information')}
        BLOCKERS: {standup_data.get('blockers', 'None')}

        Provide only valid JSON response, no additional text.
        """

    def _build_summary_prompt(self, session_data: Dict[str, Any], responses: List[Dict]) -> str:
        """Build the prompt for session summary"""
        responses_text = "\n\n".join([
            f"Developer: {r.get('developer_name', r.get('developer_email', 'Unknown'))}\n"
            f"Completed: {r.get('what_did_i_do', 'Nothing')}\n"
            f"Planned: {r.get('what_will_i_do', 'Nothing')}\n"
            f"Blockers: {r.get('blockers', 'None')}\n"
            f"Sentiment: {r.get('sentiment_score', 0)}"
            for r in responses
        ])

        return f"""
        Generate a comprehensive daily standup summary for the development team.
        Analyze all individual responses and provide insights about:
        - Overall team progress and velocity
        - Key achievements and completed work
        - Planned work for the next period
        - Blockers and risks that need attention
        - Team sentiment and morale
        - Recommendations for the Scrum Master

        SESSION DATE: {session_data.get('date', datetime.now().isoformat())}
        PARTICIPANT COUNT: {len(responses)}

        INDIVIDUAL RESPONSES:
        {responses_text}

        Provide a well-structured summary with clear sections and actionable insights.
        """

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                return json.loads(response_text)

            # If not JSON, try to extract JSON from text
            lines = response_text.split('\n')
            for line in lines:
                if line.strip().startswith('{'):
                    return json.loads(line.strip())

            # Fallback: return as text analysis
            return {
                "analysis": response_text,
                "sentiment_score": 0.0,
                "risk_level": "medium",
                "confidence_score": 0.5
            }

        except json.JSONDecodeError:
            return {
                "analysis": response_text,
                "sentiment_score": 0.0,
                "risk_level": "medium",
                "confidence_score": 0.5
            }

    def _log_analysis(self,
                     project_id: Optional[int] = None,
                     session_id: Optional[int] = None,
                     response_id: Optional[int] = None,
                     model_used: str = "",
                     tokens_consumed: int = 0,
                     analysis_type: str = "",
                     processing_time_ms: int = 0,
                     success: bool = True,
                     error_message: Optional[str] = None):
        """Log AI analysis activity to database"""
        db = SessionLocal()
        try:
            log_entry = AIAnalysisLog(
                project_id=project_id,
                session_id=session_id,
                response_id=response_id,
                model_used=model_used,
                tokens_consumed=tokens_consumed,
                analysis_type=analysis_type,
                processing_time_ms=processing_time_ms,
                success=success,
                error_message=error_message
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            print(f"Failed to log AI analysis: {e}")
            db.rollback()
        finally:
            db.close()

# Global instance
groq_service = GroqAnalysisService()