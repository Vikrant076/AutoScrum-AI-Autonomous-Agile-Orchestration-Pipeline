import os
from dotenv import load_dotenv

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    groq = None
    GROQ_AVAILABLE = False

load_dotenv()  # Load environment variables

def summarize_standup(standup_responses: list) -> str:
    """
    Takes a list of standup responses from developers and generates a summary using Groq AI.
    """
    # Build the prompt for the AI
    prompt = f"""
    Please act as a professional Scrum Master and summarize the following daily stand-up updates into a concise, well-structured paragraph.
    Focus on progress made, plans for the day, and especially any blockers or impediments that need attention.
    Provide actionable insights and highlight any risks or dependencies.
    
    Here are the individual updates:
    {standup_responses}

    Provide a comprehensive summary with the following sections:
    1. Overall Progress
    2. Key Accomplishments
    3. Planned Work
    4. Blockers and Impediments
    5. Recommendations

    Summary:
    """
    
    # Use Groq AI if available and configured
    if GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
        try:
            client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
            model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content
            print(f"Groq AI summary generated using model: {model}")
            return summary
            
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            # Fall back to mock response if API call fails
            return get_mock_summary()
    else:
        print("Groq not available or not configured. Using mock summary.")
        return get_mock_summary()

def get_mock_summary():
    """Return a mock summary when Groq is not available"""
    return """
**AI Generated Standup Summary - [Today's Date]**

**Overall Progress:**
The team is making steady progress on current sprint goals. Most tasks are on track, with a few minor blockers reported.

**Key Accomplishments:**
- John completed the login page implementation
- Jane fixed the database connection bug
- Mike implemented the user profile API endpoints

**Planned Work:**
- John will work on password reset functionality (pending design feedback)
- Jane will optimize database queries for better performance
- Mike will start work on the notification system

**Blockers and Impediments:**
- John is waiting for design feedback on the login page (blocker)
- Database performance issues need investigation (medium priority)

**Recommendations:**
1. Follow up with the design team for John's login page feedback
2. Schedule a session to review database performance metrics
3. Consider pair programming for the notification system implementation
"""