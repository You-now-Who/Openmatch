import streamlit as st
from PIL import Image
import webbrowser
from streamlit_javascript import st_javascript

# session state management
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

st.set_page_config(
        page_title="OpenMatch",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="auto",
    )


# removed URL manipulation (handled by Streamlit's native navigation)
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

# logo and header section
image = Image.open('logo.png')
st.image(image, use_column_width=True, width=200)  # Removed caption, added size control  

# enhanced text styling
st.markdown("""
<h1 style='text-align: center; color: white; font-family: "Arial", sans-serif;'>
    OpenMatch
</h1>
<h4 style='text-align: center; color: #c9d1d9; font-family: "Arial", sans-serif;'>
    Match your coding skills with perfect open-source projects!
</h4>
""", unsafe_allow_html=True)

# content layout
with st.container():
    st.markdown("""
    <div style='background: rgba(30, 30, 30, 0.7); padding: 2rem; border-radius: 10px;'>
    <p style='color: white; font-size: 1.1rem;'>
    OpenMatch helps developers discover ideal open-source projects based on their GitHub activity. 
    Whether you're preparing for Hacktoberfest or looking to contribute year-round, we'll match you 
    with projects that fit your skills and interests.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
st.divider()

# button layout with columns
col1, col2 = st.columns(2)

with col1:
    if st.button("Get Started! 🔥, Please Find projects for me!", key="find_projects"):
        st.session_state.page = 'projects'
        st.experimental_rerun()  # changed from webbrowser.open()

with col2: 
    if st.button("📊 Yay! Please show me my stats, for my own knowledge!", key="view_stats"):
        st.session_state.page = 'stats'
        st.experimental_rerun()
