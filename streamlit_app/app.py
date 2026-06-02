import streamlit as st
from api import login, register, load_sessions
from state import init

init()

st.set_page_config(
    page_title="AI Repo Assistant",
    layout="centered"
)

# -----------------------------------
# APP TITLE
# -----------------------------------
st.title("🤖 AI Repo Assistant")

# -----------------------------------
# TABS
# -----------------------------------
tab1, tab2 = st.tabs(["Login", "Register"])

# ===================================
# LOGIN
# ===================================
with tab1:

    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):

        res = login(email, password)

        if res.status_code == 200:

            data = res.json()

            # -------------------------
            # STORE AUTH DATA
            # -------------------------
            st.session_state.token = data["access_token"]

            st.session_state.refresh_token = (
                data["refresh_token"]
            )


            st.session_state.email = email
            st.session_state.user_id = data.get("user_id")

            # -------------------------
            # LOAD USER SESSIONS
            # -------------------------
            session_res = load_sessions()
            st.write("DEBUG TYPE:", type(session_res))
            st.write("STATUS:", getattr(session_res, "status_code", None))
            st.write("TEXT:", getattr(session_res, "text", None))

            if session_res.status_code == 200:

                sessions = session_res.json()

                st.session_state.sessions = {
                    s["session_id"]: {
                        "title": s["title"],
                        "repo_url": s["repo_url"]
                    }
                    for s in sessions
                }

            else:
                st.session_state.sessions = {}

            # reset runtime chat state
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.repo_data = None

            st.success("Login successful")

            # go to chat page
            st.switch_page("pages/chat.py")

        else:
            st.error("Invalid credentials")

# ===================================
# REGISTER
# ===================================
with tab2:

    st.subheader("Register")

    reg_email = st.text_input("Email", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_password")

    if st.button("Register"):

        res = register(reg_email, reg_password)

        if res.status_code == 200:
            st.success("Registration successful. Please login.")
        else:
            st.error("Registration failed")