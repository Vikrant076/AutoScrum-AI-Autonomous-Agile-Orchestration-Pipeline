# This file makes the app directory a Python package
from app.models import init_db

# Initialize database when package is imported
init_db()
