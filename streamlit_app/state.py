

import streamlit as st


def init():

    if "token" not in st.session_state:
        st.session_state.token = None

    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None

    if "email" not in st.session_state:
        st.session_state.email = None

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "session_id" not in st.session_state:
        st.session_state.session_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "sessions" not in st.session_state:
        st.session_state.sessions = {}

    if "repo_data" not in st.session_state:
        st.session_state.repo_data = None