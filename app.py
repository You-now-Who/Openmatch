import streamlit as st

# Set default page if not set - already set tho 😅
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
    
# Routing logic
if st.session_state.page == 'landing':
    import landing_page
elif st.session_state.page == 'projects':
    from pages import opensource_projects
elif st.session_state.page == 'stats':
    from pages import show_stats_page
else:
    st.error("Page not found.")
    