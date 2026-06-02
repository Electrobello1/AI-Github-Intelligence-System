from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import logging
import uuid
import uvicorn
from database import SessionData,User
from database import  save_message,ChatMessage,get_recent_messages
from agents import llm_enrichment_agent,update_conversation_summary

from fastapi import Depends

from auth import get_current_user

from graph import build_graph
from database import (
    SessionLocal,
    save_session,
    get_session
)
from jose import JWTError, jwt
from auth import (
    hash_password,
    verify_password,
    create_access_token,create_refresh_token,REFRESH_SECRET_KEY
)
# =========================
# APP INIT
# =========================
app = FastAPI(title="A3 Multi-Agent System")

app_graph = build_graph()

logging.basicConfig(level=logging.INFO)


# =========================
# REQUEST MODEL
# =========================
class RepoRequest(BaseModel):
    repo_url: HttpUrl
class HITLRequest(BaseModel):
    session_id: str
    user_message: str

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# =========================
# VALIDATION
# =========================
def validate_github_url(url: str):
    if "github.com" not in url:
        raise HTTPException(
            status_code=400,
            detail="Only GitHub repository URLs are allowed"
        )

    parts = url.replace("https://github.com/", "").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository format"
        )


# =========================
# SAFE GETTER
# =========================
def safe_get(result, key, default=None):
    value = result.get(key, default)
    return value if value is not None else default


# =========================
# OUTPUT SANITIZER
# =========================
def sanitize_output(result: dict):

    def clean_text(text, max_length):
        if not isinstance(text, str):
            return "N/A"

        text = text.strip()

        if len(text) <= max_length:
            return text

        trimmed = text[:max_length]
        last_space = trimmed.rfind(" ")

        if last_space != -1:
            trimmed = trimmed[:last_space]

        return trimmed + "..."

    return {
        "title": clean_text(safe_get(result, "title", "N/A"), 100),

        # 🔥 IMPORTANT FIX: use LLM output first
        "summary": clean_text(
             safe_get(result, "llm_improved_summary")
            or safe_get(result, "summary", "N/A"),
            500
        ),

        "quality_score": int(safe_get(result, "quality_score", 0)),
        "status": safe_get(result, "status", "unknown"),
        "confidence": round(float(safe_get(result, "confidence", 0.0)), 2),

        "tags": safe_get(result, "tags", []),
        "stars": safe_get(result, "stars", 0),
        "language": safe_get(result, "language", "unknown"),
        "forks": safe_get(result, "forks", 0),
        "review_feedback": safe_get(result, "review_feedback", {}),

        "attempts": safe_get(result,"attempts", 0),

        "prev_issue_count": safe_get(result,"prev_issue_count", 0),
    }


# =========================
# MAIN ENDPOINT
# =========================

@app.post("/analyze")
def analyze_repo(
    request: RepoRequest,
    user=Depends(get_current_user)
):

    request_id = str(uuid.uuid4())

    url = str(request.repo_url)
    validate_github_url(url)

    try:
        logging.info(f"[{request_id}] Processing repo: {url}")

        initial_state = {
            "repo_url": url,
            "attempts": 0
        }

        result = app_graph.invoke(initial_state) or {}

        # =========================
        # ✅ SAVE TO DATABASE HERE
        # =========================
        db = SessionLocal()

        save_session(db, {
            "user_id": user["user_id"],
            "session_id": request_id,
            "repo_url": url,
            "summary": result.get("summary", ""),
            "title": result.get("title", ""),
            "tags": result.get("tags", []),
            "quality_score": result.get("quality_score", 0),
            "stars": result.get("stars", 0),
            "forks": result.get("forks", 0),
            "review_feedback": result.get("review_feedback", ""),
            "status": result.get("status", "unknown"),
            "attempts": result.get("attempts", 0),
            "confidence": result. get("confidence",0),
            "prev_issue_count": result.get("prev_issue_count", 0),
        }, user)
        db.commit()
        db.close()

        logging.info(f"[{request_id}] Saved session successfully")
        logging.info(f"[{request_id}] Completed successfully")

        return {
        "user_id": user["user_id"],
        "session_id": request_id,
        **sanitize_output(result)
       }

    except Exception as e:
        logging.error(f"[{request_id}] Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error (ref: {request_id})"
        )


# =========================
# CHAT / HITL ENDPOINT
# =========================


@app.post("/chat")
def chat_with_repo(
    request: HITLRequest,
    user=Depends(get_current_user)
):

    db = SessionLocal()

    try:

        # =========================
        # GET SESSION
        # =========================
        session = get_session(
            db,
            request.session_id,
            user["user_id"]
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        # =========================
        # SAVE USER MESSAGE
        # =========================
        save_message(
            db,
            session.session_id,
            user["user_id"],
            "user",
            request.user_message
        )

        # =========================
        # GET RECENT MESSAGES
        # =========================
        recent_messages = get_recent_messages(
            db,
            session.session_id,
            user["user_id"],
            limit=15
        )

        # =========================
        # FORMAT RECENT HISTORY
        # =========================
        recent_chat = "\n".join(
            f"{m.role}: {m.message}"
            for m in recent_messages
        )

        # =========================
        # LLM CALL
        # =========================
        llm_result = llm_enrichment_agent({

            # Repo context
            "summary": session.summary,
            "title": session.title,
            "tags": session.tags.split(",") if session.tags else [],
            "quality_score": session.quality_score,
            "stars": session.stars,
            "review_feedback":session.review_feedback,
            "status":session.status,
            "prev_issue_count":session.prev_issue_count,
            "confidence":session.confidence,
            "forks":session.forks,


            # 🧠 MEMORY
            "conversation_summary": session.conversation_summary or "",
            "chat_history": recent_chat,

            # User question
            "user_question": request.user_message
        })

        response = llm_result.get(
            "llm_response",
            "No response generated"
        )

        # =========================
        # SAVE AI RESPONSE
        # =========================
        save_message(
            db,
            session.session_id,
            user["user_id"],
            "assistant",
            response
        )

        # =========================
        # AUTO UPDATE SUMMARY
        # every 10 messages
        # =========================
        total_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.session_id,
            ChatMessage.user_id == user["user_id"]
        ).count()

        if total_messages % 10 == 0:

            update_conversation_summary(
                db,
                session,
                recent_chat
            )

        return {
            "response": response
        }

    finally:
        db.close()

#endpoint for chat_history
@app.get("/session/{session_id}")
def get_session_data(
    session_id: str,
    user=Depends(get_current_user)
):

    db = SessionLocal()

    session = get_session(
        db,
        session_id,
        user["user_id"]
    )

    if not session:
        db.close()

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.user_id == user["user_id"]
    ).order_by(ChatMessage.id.asc()).all()

    db.close()

    return {
        "session_id": session.session_id,
        "summary": session.summary,
        "stars": session.stars,
        "forks": session.forks,
        "quality_score": session.quality_score,
        "tags": session.tags.split(","),
        "review_feedback": session.review_feedback
            if session.tags else [],
        "messages": [
            {
                "role": m.role,
                "content": m.message
            }
            for m in messages
        ]
    }

@app.get("/sessions")
def get_user_sessions(user=Depends(get_current_user)):

    db = SessionLocal()

    sessions = db.query(SessionData).filter(
        SessionData.user_id == user["user_id"]
    ).order_by(SessionData.user_id.desc()).all()

    db.close()

    return [
        {
            "session_id": s.session_id,
            "title": s.title,
            "repo_url": s.repo_url
        }
        for s in sessions
    ]
@app.post("/register")
def register(request: RegisterRequest):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=request.email,
        password_hash=hash_password(
            request.password
        )
    )

    db.add(user)

    db.commit()

    db.close()

    return {
        "message": "User registered successfully"
    }

@app.post("/login")
def login(request: LoginRequest):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
    db.close()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "token_type": "bearer"
    }


@app.post("/refresh")
def refresh_token(data: RefreshRequest):

    refresh_token = data.refresh_token

    try:
        payload = jwt.decode(
            refresh_token,
            REFRESH_SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload.get("user_id")
        email = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        new_access_token = create_access_token(
            data={
                "sub": email,
                "user_id": user_id
            }
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )
# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )