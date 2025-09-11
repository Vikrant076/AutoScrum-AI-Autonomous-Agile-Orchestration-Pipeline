import os
from dotenv import load_dotenv
from app.services.ai_analysis import ai_service
import json

load_dotenv()

# Test data
test_standup = {
    "developer_email": "test@example.com",
    "developer_name": "Test Developer",
    "what_did_i_do": "Worked on user authentication API, fixed login bugs, implemented JWT tokens",
    "what_will_i_do": "Continue with password reset functionality, write unit tests",
    "blockers": "Waiting for design approval on the login page, need access to production database",
    "project_id": 1,
    "session_id": 1,
    "response_id": 1
}

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set OPENAI_API_KEY in your .env file")
    else:
        print("🧪 Testing AI Analysis Service...")
        result = ai_service.analyze_standup_response(test_standup)
        print("✅ AI Analysis Result:")
        print(json.dumps(result, indent=2))