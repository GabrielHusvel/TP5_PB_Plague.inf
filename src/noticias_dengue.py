import requests
from bs4 import BeautifulSoup
import streamlit as st
from pydantic import BaseModel


# Simulando um navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# Validação de input para a ferramenta
class NoticiaDengueInput(BaseModel):
    estado: str
    municipio: str

# Função auxiliar para verificar relevância sobre dengue
def is_dengue_related(title, description):
    keywords = ['dengue', 'zika', 'chikungunya', 'aedes aegypti', 'febre amarela']
    return any(keyword.lower() in title.lower() or keyword.lower() in description.lower() for keyword in keywords)

# Função para extrair informações sobre a dengue (site do governo)
def scrape_dengue_info():
    url = 'https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/dengue'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar o site: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    dengue_info = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    return dengue_info


# Função para coletar notícias da CNN Brasil
def scrape_cnn_news():
    # URL do site
    url = "https://www.cnnbrasil.com.br/tudo-sobre/dengue/"
    
    # Cabeçalho para evitar bloqueios
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    
    # Requisição à página
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar o site: {response.status_code}")
    
    # Parse do conteúdo HTML
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Selecionar o container principal das notícias
    news_items = soup.find_all("li", class_="home__list__item")
    news_data = []
    
    for item in news_items:
        # Extrair o título
        title_tag = item.find("h3", class_="news-item-header__title")
        title = title_tag.text.strip() if title_tag else "Título não encontrado"
        
        # Extrair o link
        link_tag = item.find("a", href=True)
        link = link_tag["href"] if link_tag else "Link não encontrado"
        
        # Extrair a data de publicação
        date_tag = item.find("span", class_="home__title__date")
        date = date_tag.text.strip() if date_tag else "Data não encontrada"
        
        # Filtrar por relevância (dengue)
        if "dengue" or "zika" or "chikungunya" or "aedes aegypty" in title.lower():
            news_data.append({
                "title": title,
                "link": link,
                "description": title,  # A descrição é igual ao título
                "date": date
            })
    
    return news_data

def sanitize_input(text):
    """Remove caracteres indesejados e normaliza o texto."""
    return text.strip().title()

# Função para coletar notícias do G1
def scrape_g1_news(state, city=None):
    state = state.strip().title()
    city = city.strip().title() if city else None
    search_query = f"dengue {state}" + (f" {city}" if city else "")
    url = f"https://g1.globo.com/busca/?q={search_query}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a página do G1 (Status code: {response.status_code})")

    soup = BeautifulSoup(response.content, 'html.parser')
    news_elements = soup.find_all('div', class_='widget--info__text-container')
    if not news_elements:
        return []

    news_data = []
    for element in news_elements[:5]:  # Limite de 5 notícias
        title_tag = element.find('div', class_='widget--info__title')
        link_tag = element.find('a', href=True)
        description_tag = element.find('p', class_='widget--info__description')
        date_tag = element.find('div', class_='widget--info__meta')

        if title_tag and link_tag:
            title = title_tag.text.strip()
            link = link_tag['href']
            description = description_tag.text.strip() if description_tag else "Descrição não disponível"
            date = date_tag.text.strip() if date_tag else "Data não informada"

            if is_dengue_related(title, description):
                news_data.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "date": date
                })

    return news_data

# Função para exibir as notícias no Streamlit
def show_news(news, title):
    st.subheader(title)
    if not news:
        st.write("Nenhuma notícia encontrada.")
        return
    
    for item in news:
        st.markdown(f"**[{item['title']}]({item['link']})**")
        st.write(f"*Publicado em: {item['date']}*")
        st.write(f"{item['description']}")
        st.write("---")


# Streamlit App
def exibir_noticias_informacoes():
    st.title("🔍 Notícias e Informações sobre Dengue 🔍")
    
    # Informações gerais
    if st.button("Carregar Informações sobre Dengue"):
        try:
            informacoes = scrape_dengue_info()
            for info in informacoes:
                st.write(info)
        except Exception as e:
            st.error(f"Erro ao carregar informações: {e}")
    
    # Notícias gerais da CNN
    if st.button("Carregar Notícias Gerais"):
        try:
            cnn_news = scrape_cnn_news()
            show_news(cnn_news, "Notícias Gerais sobre Dengue - CNN Brasil")
        except Exception as e:
            st.error(f"Erro ao carregar notícias gerais: {e}")
    
    # Notícias por estado e município
    from user_global import ESTADO_USUARIO, MUNICIPIO_USUARIO
    
    if st.button("Carregar Notícias por Estado e Município"):
        try:
            state_news = scrape_g1_news(ESTADO_USUARIO)
            city_news = scrape_g1_news(ESTADO_USUARIO, MUNICIPIO_USUARIO) if MUNICIPIO_USUARIO else []
            
            show_news(state_news, f"Notícias no Estado: {ESTADO_USUARIO}")
            show_news(city_news, f"Notícias no Município: {MUNICIPIO_USUARIO}")
        except Exception as e:
            st.error(f"Erro ao carregar notícias por estado ou município: {e}")
