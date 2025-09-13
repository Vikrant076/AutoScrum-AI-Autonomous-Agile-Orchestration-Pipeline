import streamlit as st
import requests
import os

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "https://autoscrum-production.up.railway.app")

# Set page config
st.set_page_config(
    page_title="AutoScrum Dashboard",
    page_icon="🚀",
    layout="wide"
)

def main():
    st.title("AutoScrum Dashboard")
    st.write("Welcome to AutoScrum - Your AI Agile Orchestration Tool")
    
    # Test connection to backend
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            st.success("✅ Connected to backend API successfully!")
            st.json(response.json())
        else:
            st.error("❌ Backend connection failed")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    
    # Add your actual app functionality here

if __name__ == "__main__":
    main()
