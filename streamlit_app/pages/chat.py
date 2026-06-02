import streamlit as st
from api import analyze, send_message, load_session, load_sessions
from state import init

# -----------------------------------
# INITIALIZE SESSION STATE
# -----------------------------------
init()

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="AI Repo Assistant",
    layout="wide"
)

# -----------------------------------
# AUTH CHECK
# -----------------------------------
if not st.session_state.token:
    st.warning("Please login first")
    st.stop()

# -----------------------------------
# SIDEBAR
# -----------------------------------
with st.sidebar:

    st.title("💬 AI Repo Assistant")
    st.markdown("---")

    # -----------------------------
    # REPO INPUT
    # -----------------------------
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/user/repo"
    )

    # -----------------------------
    # ANALYZE REPO (FIXED)
    # -----------------------------
    if st.button("Analyze Repository"):

        if repo_url.strip():

            with st.spinner("Analyzing repository..."):


                res = analyze(repo_url)

            if res.status_code == 200:

                data = res.json()

                st.session_state.session_id = data["session_id"]
                st.session_state.messages = []

                st.session_state.repo_data = {
                    "summary": data.get("summary", ""),
                    "stars": data.get("stars", 0),
                    "forks": data.get("forks", 0),
                    "quality_score": data.get("quality_score", 0),
                    "tags": data.get("tags", []),
                    "confidence": data.get("confidence", 0),
                    "review_feedback": data.get("review_feedback", {}),
                    "prev_issue_count": data.get("prev_issue_count", 0),
                    "attempts": data.get("attempts", 1)
                }

                st.success("Analysis complete")
                st.rerun()

            else:
                st.error("Failed to analyze repository")

    st.markdown("---")

    # -----------------------------
    # SESSION HISTORY (FIXED)
    # -----------------------------
    st.subheader("Chats")

    session_res = load_sessions()

    if session_res.status_code == 200:
        sessions = session_res.json()
    else:
        sessions = []

    for s in sessions:

        sid = s["session_id"]
        title = s.get("title", "Untitled")

        if st.button(title[:30], key=sid):

            res = load_session(sid)

            if res.status_code == 200:

                data = res.json()

                st.session_state.session_id = sid
                st.session_state.messages = data["messages"]

                st.session_state.repo_data = {
                    "summary": data.get("summary", ""),
                    "stars": data.get("stars", 0),
                    "forks": data.get("forks", 0),
                    "quality_score": data.get("quality_score", 0),
                    "tags": data.get("tags", []),
                    "confidence": data.get("confidence", 0),
                    "review_feedback": data.get("review_feedback", {}),
                    "prev_issue_count": data.get("prev_issue_count", 0),
                    "attempts": data.get("attempts", 1)
                }

                st.rerun()

    st.markdown("---")

    # -----------------------------
    # ACTIVE SESSION
    # -----------------------------
    st.write("Active Session")
    st.code(st.session_state.session_id or "None")

    # -----------------------------
    # NEW CHAT
    # -----------------------------
    if st.button("➕ New Chat"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.repo_data = None
        st.rerun()

    # -----------------------------
    # PROFILE
    # -----------------------------
    st.markdown("---")
    st.markdown("### 👤 Profile")

    st.write(f"**Email:** {st.session_state.email}")
    st.write(f"**User ID:** {st.session_state.user_id}")

    # -----------------------------
    # LOGOUT (FIXED)
    # -----------------------------
    if st.button("Logout"):

        st.session_state.clear()
        st.switch_page("app.py")

# -----------------------------------
# MAIN PAGE
# -----------------------------------
st.title("🤖 AI Repo Assistant")

if not st.session_state.session_id:

    st.info("Analyze a repository or select a previous chat")
    st.stop()

# -----------------------------------
# REPO OVERVIEW
# -----------------------------------
repo_data = st.session_state.get("repo_data")

if repo_data:

    st.subheader("📦 Repository Overview")
    st.write(repo_data.get("summary", ""))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("⭐ Stars", repo_data.get("stars", 0))
    col2.metric("🍴 Forks", repo_data.get("forks", 0))
    col3.metric("🧠 Quality", repo_data.get("quality_score", 0))
    col4.metric("🎯 Confidence", repo_data.get("confidence", 0))

    st.write("**Tags:** " + ", ".join(repo_data.get("tags", [])))

    st.markdown("---")

    feedback = repo_data.get("review_feedback", {})

    if feedback is None:
        feedback = {}

    if isinstance(feedback, str):
        feedback = {"message": feedback}

    if isinstance(feedback, dict) and feedback:
        st.write("### 🧾 Review Feedback")
        for k, v in feedback.items():
            st.write(f"**{k.replace('_', ' ').title()}**: {v}")

# -----------------------------------
# CHAT HISTORY
# -----------------------------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------------
# CHAT INPUT
# -----------------------------------
user_input = st.chat_input("Ask something about the repository...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):


            res = send_message(
                st.session_state.session_id,
                user_input
            )

        if res.status_code == 200:
            bot_reply = res.json().get("response", "No response")
        else:
            bot_reply = "Error generating response"

        st.markdown(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })