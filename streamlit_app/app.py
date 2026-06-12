import streamlit as st
from api import login, register, load_sessions
from state import init
from api import warmup_backend

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
        warmup_backend()

        try:
            res = login(email, password)

            # -----------------------------
            # SUCCESS
            # -----------------------------
            if res.status_code == 200:

                data = res.json()

                st.session_state.token = data["access_token"]
                st.session_state.refresh_token = data["refresh_token"]
                st.session_state.email = email
                st.session_state.user_id = data.get("user_id")

                # Load sessions
                session_res = load_sessions()

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

                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.repo_data = None

                st.success("Login successful")
                st.switch_page("pages/chat.py")

            # -----------------------------
            # INVALID CREDENTIALS
            # -----------------------------
            elif res.status_code == 401:
                st.error("Invalid email or password")

            # -----------------------------
            # SERVER ERROR (IMPORTANT FOR RENDER)
            # -----------------------------
            elif res.status_code in [ 502, 503, 504]:
                st.warning(
                    "Server is starting or temporarily unavailable. Please wait a few seconds and try again."
                )
                st.write(res.text)

            # -----------------------------
            # OTHER ERRORS
            # -----------------------------
            else:
                st.error(f"Unexpected error: {res.status_code}")
                st.write(res.text)

        # -----------------------------
        # NETWORK / COLD START FAILURE
        # -----------------------------
        except Exception as e:
            st.warning(
                "Cannot reach server. The server may be waking up on Render. Please wait a few seconds and retry."
            )
            st.write(str(e))
# ===================================
# REGISTER
# ===================================
# ===================================
# REGISTER
# ===================================
with tab2:

    st.subheader("Register")

    reg_email = st.text_input("Email", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_password")

    if st.button("Register"):

        try:
            res = register(reg_email, reg_password)

            # -----------------------------
            # SUCCESS
            # -----------------------------
            if res.status_code == 200:
                st.success("Registration successful. Please login.")

            # -----------------------------
            # USER / VALIDATION ERROR
            # -----------------------------
            elif res.status_code == 400:
                st.error("Invalid input or user already exists")

            elif res.status_code == 409:
                st.error("User already exists")

            # -----------------------------
            # SERVER ERROR (Render cold start / backend issue)
            # -----------------------------
            elif res.status_code in [500, 502, 503, 504]:
                st.warning(
                    "Server is starting or temporarily unavailable. Please try again in a few seconds."
                )
                st.write(res.text)

            # -----------------------------
            # OTHER ERRORS
            # -----------------------------
            else:
                st.error(f"Unexpected error: {res.status_code}")
                st.write(res.text)

        # -----------------------------
        # NETWORK ERROR / COLD START
        # -----------------------------
        except Exception as e:
            st.warning(
                "Cannot reach server. Server may be starting up. Please retry."
            )
            st.write(str(e))