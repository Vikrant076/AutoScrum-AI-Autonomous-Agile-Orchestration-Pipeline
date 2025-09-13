import streamlit as st
import os

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="AutoScrum Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Your app code here
def main():
    st.title("AutoScrum Dashboard")
    st.write("Welcome to AutoScrum - Your AI Agile Orchestration Tool")
    # Add the rest of your app code here

if __name__ == "__main__":
    # Get port from environment variable or default to 8501
    port = int(os.environ.get("PORT", 8501))
    main()
