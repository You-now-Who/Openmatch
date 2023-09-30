import streamlit as st
import requests

st.set_page_config(
        page_title="OpenMatch",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="auto",
    )

st.markdown("<h2 style='text-align: center; color: white;'>Let's find some projects for you to contribute on, please specify criteria (optional)!</h2><br><br>", unsafe_allow_html=True)

