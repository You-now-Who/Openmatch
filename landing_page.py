import streamlit as st
from PIL import Image
import webbrowser
from streamlit_javascript import st_javascript

#session state management
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

st.set_page_config(
        page_title="OpenMatch",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="auto",
    )


#Removed URL manipulation (handled by Streamlit's native navigation)
# Old approach:
# url = st_javascript("await fetch('').then(r => window.parent.location.href)")
# projectsUrl = url + "opensource_projects" 
# statsUrl = url + "show_stats_page"

st.markdown("""
<style>
/* Main container styling */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

/* Button styling */
.stButton>button {
    background: linear-gradient(45deg, #6e48aa, #9d50bb);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
    margin: 10px;
    width: 100%;
}

/* Button hover effects */
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

/* Logo styling */
.stImage {
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

#logo and header section
image = Image.open('logo.png')
st.image(image, use_column_width=True, width=200)  # Removed caption, added size control  

st.markdown("<h1 style='text-align: center; color: white;'>OpenMatch</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: white;font-family: 'arial'>OpenMatch: Match your coding skills!</h5>", unsafe_allow_html=True)
st.write("""

    "OpenMatch is the ultimate destination of your work goals. It helps you find cool projects to work on, just like finding hidden treasures. It's super fun and makes you feel like a tech superhero! So, if you're a coder, don't miss out on OpenMatch – it's awesome!,
         Especially for the festivals of ghw, hacktoberfest or hackquad, OpenMatch has got you covered!"
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("Get Started! 🔥, Please Find projects for me!", key="find_projects"):
        st.session_state.page = 'projects'
        st.experimental_rerun()  # Changed from webbrowser.open()

with col2: 
    if st.button("📊 Yay! Please show me my stats, for my own knowledge!", key="view_stats"):
        st.session_state.page = 'stats'
        st.experimental_rerun()
