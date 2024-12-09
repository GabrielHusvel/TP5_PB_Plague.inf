import pandas as pd
import streamlit as st


# Função para carregar os dados
@st.cache_data
def carregar_dados():
    '''
    Carrega as bases de dados necessárias para o funcionamento do aplicativo
    '''
    df_municipios = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/2020-2024/macrorregiao_municipios_fx_etaria_casos_2024.csv')
    df_capitais = pd.read_csv('data_sus/infogripe-master/Dados/InfoGripe/2020-2024/capitais_serie_estimativas_fx_etaria.csv')
    return df_municipios, df_capitais
