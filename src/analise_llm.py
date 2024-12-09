
import pandas as pd

def definir_cor(risco):
    if risco > 7:
        return [255, 0, 0, 160]  # Vermelho (risco alto)
    elif 1 < risco <= 6.99:
        return [255, 255, 0, 160]  # Amarelo (risco moderado)
    else:
        return [0, 255, 0, 160]  # Verde (risco baixo)

def analise_llm_municipio(df, municipio_usuario):

    # Converter datas e preparar o dataframe
    df['data_week'] = pd.to_datetime(df['data_week'], errors='coerce')

    # Verificar se o município existe no dataframe
    if municipio_usuario not in df['municipio'].unique():
        raise ValueError(f"O município '{municipio_usuario}' não foi encontrado no dataset.")

    # Dados do município solicitado
    df_municipio = df[df["municipio"] == municipio_usuario]
    # Verificar se o município foi encontrado
    if df_municipio.empty:
        raise ValueError(f"O município '{municipio_usuario}' não foi encontrado no dataset.")
    estado_usuario = df_municipio["estado"].iloc[0]
    df_filtrado = df[df["estado"] == estado_usuario]
    # Filtrar dados do estado
    df_estado = df[df['estado'] == estado_usuario]

    # Determinar o período de análise
    data_maxima = df_estado['data_week'].max()
    data_inicial = data_maxima - pd.DateOffset(months=1) 
    df_filtrado = df_estado[(df_estado['data_week'] >= data_inicial) & (df_estado['data_week'] <= data_maxima)].copy()

   

    # Retorna informações necessárias
    return estado_usuario, municipio_usuario, df_municipio, df_filtrado

import logging
import requests
from bs4 import BeautifulSoup

# Simulando um navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# Função auxiliar para verificar relevância sobre dengue
def is_dengue_related(title, description):
    keywords = [
        'dengue', 'zika', 'chikungunya', 
        'aedes aegypti', 'febre amarela', 
        'mosquito'
    ]
    return any(keyword.lower() in (title + description).lower() for keyword in keywords)

# Função para coletar notícias do G1
def scrape_news_llm(user_input):
    try:
        search_query = f"dengue {user_input}"
        url = f"https://g1.globo.com/busca/?q={search_query}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            logging.error(f"Erro ao acessar a página do G1 (Status code: {response.status_code})")
            raise Exception(f"Erro ao acessar a página do G1 (Status code: {response.status_code})")

        soup = BeautifulSoup(response.content, 'html.parser')
        news_elements = soup.find_all('div', class_='widget--info__text-container')

        if not news_elements:
            logging.info(f"Nenhuma notícia encontrada para a cidade {user_input}.")
            return []

        news_data = []
        for element in news_elements[:5]:  # Limite de 5 notícias
            title_tag = element.find('div', class_='widget--info__title')
            link_tag = element.find('a', href=True)
            description_tag = element.find('p', class_='widget--info__description')
            date_tag = element.find('div', class_='widget--info__meta')

            # Verificar existência e processar os elementos
            title = title_tag.text.strip() if title_tag else "Título não disponível"
            link = link_tag['href'] if link_tag else "Link não disponível"
            description = description_tag.text.strip() if description_tag else "Descrição não disponível"
            date = date_tag.text.strip() if date_tag else "Data não informada"

            if is_dengue_related(title, description):
                news_data.append({
                    "title": title,
                    "description": description,
                    "date": date
                })

        if not news_data:
            logging.info(f"Nenhuma notícia relevante sobre dengue foi encontrada para a cidade {user_input}.")

        return news_data

    except Exception as e:
        logging.error(f"Erro ao coletar notícias para a cidade {user_input}: {e}")
        return [{"error": f"Não foi possível coletar notícias: {str(e)}"}]
