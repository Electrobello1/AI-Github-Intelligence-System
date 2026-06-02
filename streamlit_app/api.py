import requests
import streamlit as st
BASE_URL = "http://localhost:8000"



# -----------------------------------
# AUTH
# -----------------------------------
def login(email, password):

    return requests.post(
        f"{BASE_URL}/login",
        json={
            "email": email,
            "password": password
        }
    )


def register(email, password):

    return requests.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password
        }
    )


# -----------------------------------
# REFRESH ACCESS TOKEN
# -----------------------------------
def refresh_access_token():

    token = st.session_state.get("refresh_token")

    if not token:
        return None
    res = requests.post(
        f"{BASE_URL}/refresh",
        json={"refresh_token": st.session_state.refresh_token}
    )



    if res.status_code == 200:
        new_token = res.json()["access_token"]


        return new_token

    return None

# -----------------------------------
# AUTHORIZED REQUEST
# -----------------------------------
def authorized_post(endpoint, payload):

    headers = {
        "Authorization":
        f"Bearer {st.session_state.token}"
    }

    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json=payload,
        headers=headers
    )

    # -----------------------------------
    # TOKEN EXPIRED
    # -----------------------------------
    if response.status_code == 401:

        new_token = refresh_access_token()

        if new_token:

            headers["Authorization"] = (
                f"Bearer {new_token}"
            )

            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=payload,
                headers=headers
            )

    return response


# -----------------------------------
# AUTHORIZED GET
# -----------------------------------
def authorized_get(endpoint):

    headers = {
        "Authorization":
        f"Bearer {st.session_state.token}"
    }

    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=headers
    )

    # -----------------------------------
    # TOKEN EXPIRED
    # -----------------------------------
    if response.status_code == 401:

        new_token = refresh_access_token()

        if new_token:

            headers["Authorization"] = (
                f"Bearer {new_token}"
            )

            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers
            )

    return response


# -----------------------------------
# ANALYZE REPOSITORY
# -----------------------------------
def analyze(repo_url):

    return authorized_post(
        "/analyze",
        {
            "repo_url": repo_url
        }
    )


# -----------------------------------
# SEND CHAT MESSAGE
# -----------------------------------
def send_message(session_id, message):

    return authorized_post(
        "/chat",
        {
            "session_id": session_id,
            "user_message": message
        }
    )


# -----------------------------------
# LOAD ALL SESSIONS
# -----------------------------------
def load_sessions():

    return authorized_get(
        "/sessions"
    )


# -----------------------------------
# LOAD SINGLE SESSION
# -----------------------------------
def load_session(session_id):

    return authorized_get(
        f"/session/{session_id}"
    )