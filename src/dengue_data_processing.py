import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dataset(file_path='data_sus/df_dengue_2023_2024.csv'):
    '''
    Carrega as bases de dados necessárias para o funcionamento do aplicativo
    '''
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error("Arquivo não encontrado.")
        df = pd.DataFrame()  
    return df