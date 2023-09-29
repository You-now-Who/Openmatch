# Just setting up the enviorment right now. This is a very basic streamlit test
import streamlit as st

btn = st.button("When I get clicked, there should be new text")

if btn:
    st.write("See, this is the new text")