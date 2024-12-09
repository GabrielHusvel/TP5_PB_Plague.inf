import streamlit as st

def configure_page():
    st.set_page_config(page_title='Plague.inf', page_icon='☣️', layout='wide')
    st.markdown(f'''<style>.stApp {{background-color: #212325;}}</style>''', unsafe_allow_html=True)
