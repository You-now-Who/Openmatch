import streamlit as st
from PIL import Image

image = Image.open('logo.png')
st.set_page_config(
        page_title="OpenMatch",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="auto",
    )

st.image(image, caption='OpenMatch logo',use_column_width=True, width=100)
st.markdown("<h1 style='text-align: center; color: white;'>OpenMatch</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: white;font-family: 'arial'>OpenMatch: Match your coding skills!</h5>", unsafe_allow_html=True)
st.write("""

    "OpenMatch is the ultimate destination of your work goals. It helps you find cool projects to work on, just like finding hidden treasures. It's super fun and makes you feel like a tech superhero! So, if you're a coder, don't miss out on OpenMatch – it's awesome!,
         Especially for the festivals of ghw, hacktoberfest or hackquad, OpenMatch has got you covered!"
""")

st.divider()


st.button("Get Started! 🔥, Please Find projects for me!")
st.button('Yay! Please show me my stats, for my own knowledge!')
