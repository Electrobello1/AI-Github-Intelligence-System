from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class SessionData(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    user_id = Column(Integer)
    repo_url = Column(Text)
    summary = Column(Text)
    title = Column(Text)
    tags = Column(Text)
    quality_score = Column(Integer)
    stars = Column(Integer)
    conversation_summary = Column(Text, default="")
    forks= Column(Integer)
    review_feedback = Column(JSONB)
    status= Column(Text)
    attempts=Column(Integer)
    confidence=Column(Integer)
    prev_issue_count=Column(Integer)
    language=Column(Text)
    missing_sections=Column(Text)
    readme=Column(Text)
    llm_summary=Column(Text)






def save_session(db, data, user):

    session = SessionData(
        user_id=user["user_id"],  # 🔥 FIXED (DO NOT trust input)
        session_id=data["session_id"],
        repo_url=data["repo_url"],
        summary=data["summary"],
        title=data["title"],
        tags=",".join(data["tags"]),
        quality_score=data["quality_score"],
        stars=data["stars"],
        forks=data["forks"],
        review_feedback=str(data.get("review_feedback", "")),
        status=data["status"],
        attempts=data["attempts"],
        confidence=data["confidence"],
        prev_issue_count=data["prev_issue_count"],
        language=data["language"],
        missing_sections=data["missing_sections"],
        readme=data["readme"],
        llm_summary=data["llm_summary"]
    )

    try:
        db.add(session)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def get_session(db, session_id, user_id):
    return db.query(SessionData).filter(
        SessionData.session_id == session_id,
        SessionData.user_id == user_id
    ).first()

def save_message(db, session_id, user_id, role, message):

    msg = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role=role,
        message=message
    )

    db.add(msg)
    db.commit()

def get_recent_messages(db, session_id, user_id, limit=15):

    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == user_id
        )
        .order_by(ChatMessage.timestamp.desc())
        .limit(limit)
        .all()
    )[::-1]  # reverse back to chronological order


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, index=True)
    session_id = Column(String, index=True)

    role = Column(String)  # "user" or "assistant"
    message = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow)

class AgentTrace(Base):
        __tablename__ = "agent_traces"

        id = Column(Integer, primary_key=True)
        session_id = Column(String)
        agent_name = Column(String)
        input_data = Column(Text)
        output_data = Column(Text)


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    email = Column(
        String,
        unique=True,
        index=True
    )

    password_hash = Column(String)

Base.metadata.create_all(bind=engine)