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
    
"""
    --Supplementary info--
How it works:

1. Run your app with streamlit run app.py.
2. The landing page appears first.
3. Clicking a button sets the page in session state and reruns, so app.py loads the correct module.
4. All pages use the correct logic and error handling.

"""