from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# Use SQLite for development - no server required!
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./autoscrum.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    jira_project_key = Column(String, unique=True, index=True)
    github_repo_name = Column(String)
    slack_channel_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship to standup sessions
    standup_sessions = relationship("StandupSession", back_populates="project")
    team_members = relationship("TeamMember", back_populates="project")
    ai_configs = relationship("AIConfig", back_populates="project")

class StandupSession(Base):
    __tablename__ = "standup_sessions"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    summary = Column(Text)
    status = Column(String, default="pending")  # pending, in-progress, completed
    participant_count = Column(Integer, default=0)
    blocker_count = Column(Integer, default=0)
    ai_generated_summary = Column(Text)  # AI-generated session summary
    sentiment_score = Column(Float)  # Overall session sentiment (-1 to 1)
    risk_level = Column(String)  # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="standup_sessions")
    responses = relationship("StandupResponse", back_populates="session")
    blocked_items = relationship("BlockedItem", back_populates="session")

class StandupResponse(Base):
    __tablename__ = "standup_responses"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('standup_sessions.id'), index=True)
    developer_email = Column(String, index=True)
    developer_name = Column(String)
    what_did_i_do = Column(Text)
    what_will_i_do = Column(Text)
    blockers = Column(Text)
    sentiment_score = Column(Float)  # -1.0 to 1.0 for more granular sentiment
    has_blockers = Column(Boolean, default=False)
    ai_analysis = Column(JSON)  # Raw AI analysis JSON response
    risk_level = Column(String)  # low, medium, high, critical
    confidence_score = Column(Float)  # AI analysis confidence (0.0 to 1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    session = relationship("StandupSession", back_populates="responses")
    blocked_items = relationship("BlockedItem", back_populates="response")

class BlockedItem(Base):
    __tablename__ = "blocked_items"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('standup_sessions.id'), index=True)
    response_id = Column(Integer, ForeignKey('standup_responses.id'), index=True)
    blocker_description = Column(Text)
    severity = Column(String)  # low, medium, high, critical
    status = Column(String, default="open")  # open, in-progress, resolved, escalated
    assigned_to = Column(String)
    ai_priority_score = Column(Float)  # AI-assigned priority (0.0 to 1.0)
    estimated_resolution_time = Column(String)  # AI-estimated resolution time
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    session = relationship("StandupSession", back_populates="blocked_items")
    response = relationship("StandupResponse", back_populates="blocked_items")

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    slack_user_id = Column(String)
    last_standup_date = Column(DateTime)
    participation_score = Column(Float, default=0.0)  # AI-calculated participation metric
    productivity_trend = Column(String)  # improving, stable, declining
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="team_members")

class AIConfig(Base):
    __tablename__ = "ai_configs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    openai_model = Column(String, default="gpt-4-turbo-preview")
    temperature = Column(Float, default=0.7)  # 0.0 to 1.0 scale (more standard)
    max_tokens = Column(Integer, default=500)
    summary_style = Column(String, default="professional")  # professional, concise, detailed
    analysis_depth = Column(String, default="standard")  # basic, standard, detailed
    auto_generate_summaries = Column(Boolean, default=True)
    sentiment_analysis_enabled = Column(Boolean, default=True)
    risk_assessment_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="ai_configs")

class AIAnalysisLog(Base):
    __tablename__ = "ai_analysis_logs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    session_id = Column(Integer, ForeignKey('standup_sessions.id'), index=True)
    response_id = Column(Integer, ForeignKey('standup_responses.id'), index=True)
    model_used = Column(String)
    tokens_consumed = Column(Integer)
    analysis_type = Column(String)  # sentiment, risk, summary, etc.
    processing_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Database utility functions
def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    print(f"Using database: {DATABASE_URL}")

# Run this to create tables when this file is executed directly
if __name__ == "__main__":
    init_db()