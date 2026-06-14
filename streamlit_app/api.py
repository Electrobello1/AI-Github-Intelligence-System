import requests
from requests.exceptions import RequestException
import streamlit as st
import time
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
#BASE_URL = "http://localhost:8000"

# -----------------------------------
# AUTH
# -----------------------------------
def warmup_backend():

        try:
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(3)

# AUTH
# -----------------------------------
def login(email, password):

    for i in range(3):

        try:
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            # Success or invalid credentials
            if response.status_code in [200, 401]:
                return response

            # Too many requests
            if response.status_code == 429:
                time.sleep(5)
                continue

            # Temporary server issues
            if response.status_code in [500, 502, 503, 504]:
                time.sleep(2 ** i)
                continue

            # Any other response
            return response

        except requests.exceptions.RequestException:
            time.sleep(2 ** i)

    # final fallback
    class FakeResponse:
        status_code = 503
        text = "server unavailable"

        def json(self):
            return {
                "detail": "server unavailable"
            }

    return FakeResponse()
# =========================================================
# REGISTER FUNCTION (SAME LOGIC AS LOGIN)
# =========================================================
def register(email, password):

    for i in range(3):

        try:
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            # Success or email already exists
            if response.status_code in [200, 409]:
                return response

            # Too many requests
            if response.status_code == 429:
                time.sleep(5)
                continue

            # Temporary server issues
            if response.status_code in [500, 502, 503, 504]:
                time.sleep(2 ** i)
                continue

            # Any other response
            return response

        except RequestException:
            time.sleep(2 ** i)

    # final fallback
    class FakeResponse:
        status_code = 503
        text = "server unavailable"

        def json(self):
            return {
                "detail": "server unavailable"
            }

    return FakeResponse()



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