import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="AutoScrum Dashboard", page_icon="🚀")

# API configuration
API_BASE_URL = "http://autoscrum-production.up.railway.app"

# Header
st.title("🚀 AutoScrum Dashboard")
st.markdown("AI-Powered Agile Management System")

# Check backend connection
try:
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        st.success("✅ Backend connection successful!")
    else:
        st.warning("⚠️ Backend connection issue")
except:
    st.error("❌ Cannot connect to backend. Make sure it's running on localhost:8000")

# SIMPLE STANDUP FORM - This should definitely show
st.header("📝 Submit Your Daily Standup")

email = st.text_input("Email Address", "developer@example.com")
yesterday = st.text_area("What did you do yesterday?", "Worked on implementing user authentication")
today = st.text_area("What will you do today?", "Implement password reset feature")
blockers = st.text_area("Any blockers?", "Waiting for API documentation")

if st.button("Submit Standup"):
    standup_data = {
        "developer_email": email,
        "what_did_i_do": yesterday,
        "what_will_i_do": today,
        "blockers": blockers
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/webhook/standup", json=standup_data)
        if response.status_code == 200:
            st.success("✅ Standup submitted successfully!")
        else:
            st.error(f"❌ Error: {response.text}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")

# SIMPLE AI TEST FORM
st.header("🤖 Test AI Analysis")

test_input = st.text_input("What did you work on?", "Implemented user login system")
if st.button("Analyze with AI"):
    test_data = {
        "developer_email": "test@example.com",
        "what_did_i_do": test_input,
        "what_will_i_do": "Continue development",
        "blockers": "None",
        "project_id": 1,
        "session_id": 1
    }
    
    try:
        with st.spinner("🤖 AI is analyzing..."):
            response = requests.post(f"{API_BASE_URL}/analyze-standup", json=test_data)
        if response.status_code == 200:
            analysis = response.json()
            st.success("✅ Analysis complete!")
            
            # ===== BEAUTIFUL FORMATTED UI REPLACES RAW JSON =====
            # Create a container with a nice border for the main report
            with st.container(border=True):
                st.header("📊 Stand-up Analysis Report")
                
                # Create columns for the top metrics
                col1, col2, col3 = st.columns(3)
                
                # Sentiment Score with a gauge-like visual
                # Sentiment Score with a gauge-like visual
            with col1:
                st.metric(label="**Sentiment**", value=analysis.get('sentiment_label', 'N/A').title())
                # Handle negative sentiment scores for progress bar
                sentiment_score = analysis.get('sentiment_score', 0)
                # Convert negative scores to positive for display (but keep original value in text)
                display_score = max(0.0, min(1.0, abs(sentiment_score)))  # Ensure between 0-1
                st.progress(float(display_score), text=f"Score: {sentiment_score}")
                
                # Risk Level with color coding
                with col2:
                    risk_level = analysis.get('risk_level', 'unknown')
                    risk_emoji = "🟢" if risk_level == "low" else "🟡" if risk_level == "medium" else "🔴"
                    st.metric(label="**Risk Level**", value=f"{risk_emoji} {risk_level.title()}")
                
                # Confidence Score
                with col3:
                    confidence = analysis.get('confidence_score', 0)
                    st.metric(label="**AI Confidence**", value=f"{confidence * 100:.0f}%")
                
                st.divider()  # Adds a horizontal line
                
                # Key Achievements Section
                if analysis.get('key_achievements'):
                    st.subheader("✅ Key Achievements")
                    for achievement in analysis['key_achievements']:
                        st.markdown(f"- {achievement}")
                else:
                    st.subheader("✅ Key Achievements")
                    st.markdown("*No major achievements reported.*")
                
                # Planned Work Section
                if analysis.get('planned_work'):
                    st.subheader("📋 Planned Work")
                    for plan in analysis['planned_work']:
                        st.markdown(f"- {plan}")
                else:
                    st.subheader("📋 Planned Work")
                    st.markdown("*No planned work reported.*")
                
                # Critical Blockers Section (This one is important, so we color it red if needed)
                if analysis.get('critical_blockers'):
                    st.subheader("🚨 Critical Blockers", help="These require immediate attention!")
                    for blocker in analysis['critical_blockers']:
                        st.error(f"- {blocker}")  # Uses Streamlit's error style (red)
                else:
                    st.subheader("🚨 Critical Blockers")
                    st.success("No critical blockers!")  # Uses Streamlit's success style (green)
                
                # Suggested Actions Section
                if analysis.get('suggested_actions'):
                    st.subheader("💡 Suggested Actions")
                    for action in analysis['suggested_actions']:
                        st.info(f"- {action}")  # Uses Streamlit's info style (blue)
                else:
                    st.subheader("💡 Suggested Actions")
                    st.markdown("*No specific actions suggested.*")
                
                st.divider()
                
                # Productivity Insight
                if analysis.get('productivity_insight'):
                    st.subheader("🧠 Productivity Insight")
                    st.write(analysis['productivity_insight'])
            
            # Optional: Keep the raw JSON available but hidden in an expander for debugging
            with st.expander("Raw JSON Data (For Debugging)"):
                st.json(analysis)
            # ===== END OF BEAUTIFUL UI =====
            
        else:
            st.error(f"❌ Analysis failed: {response.text}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
