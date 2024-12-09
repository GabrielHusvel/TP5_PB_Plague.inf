import streamlit as st

from gripe_mapa_regional import create_dashboard
from config import configure_page  
from noticias_gripe import noticias_informacoes_gripe
import streamlit as st
import google.generativeai as genai
import os
from analise_llm import analise_llm_municipio
from dengue_data_processing import carregar_dataset
from dotenv import load_dotenv
import pandas as pd
from langchain.tools import tool
from langchain.agents import initialize_agent
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from user_global import MUNICIPIO_USUARIO
configure_page()
load_dotenv('../.env')

# Obtém a chave da API 
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Carregar o dataset
df = carregar_dataset()

# Definir as opções de navegação
menu = ["Tela Inicial", "Chat de Consulta", 'Mapa Interativo']
choice = st.sidebar.selectbox("Navegue pelo App", menu)

# Tela Inicial
if choice == "Tela Inicial":
    st.title("Bem-vindo ao Sistema de Consulta de Doenças Plague.inf☣️")
    st.markdown(
        """
        Este aplicativo permite consultar a situação da dengue e gripe(inlfuenza) em municípios brasileiros.
        Você pode:
        - Obter análises detalhadas com base nos dados disponíveis.
        - Interagir com um modelo de IA para resumir e interpretar informações.

        **Como usar**:
        - Navegue até o "Chat de Consulta" no menu lateral.
            - Insira o nome do município que deseja consultar.
            - Receba análises detalhadas e orientações baseadas nos dados.
        - Navegue até o "Mapa Interativo" no menu lateral.
            - Escolha seu municipio e veja no mapa a situação os municipios da região.
            - Descubra notícias sobre a região escolhida.
            - Obtenha análises interativas e personalizadas e acesso aos dados.
        **⚠️ Nota:** Os dados são atualizados periodicamente para refletir a situação mais recente.
        """
    )
    st.image("https://i.imgur.com/gygo72j.jpg")

# Chat de Consulta
elif choice == "Chat de Consulta":
    from noticias_dengue import scrape_dengue_info
    from pydantic import BaseModel
    from typing import Union
    import re
    from analise_llm import analise_llm_municipio, scrape_news_llm
    import logging
    
    # Interface do Streamlit
    st.title("Chat de Consulta de Dengue")

    # Histórico de mensagens no Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

  
    # Entrada do usuário
    if user_input := st.chat_input("Digite o nome do município que deseja consultar:"):
        class UserInput(BaseModel):
            municipio: str

     
     
        @tool
        def info_dengue(input: str) -> str:
            """
            Retorna informações gerais sobre a dengue, como sintomas, formas de prevenção e cuidados básicos.
            """
            informacoes = scrape_dengue_info()
            return informacoes
        
        @tool
        def noticia_dengue(user_input: Union[str, UserInput]) -> str:
            """
            Busca notícias relacionadas sobre a dengue no municipio selecionado pelo usuário.
            """

            try:
                news = scrape_news_llm(user_input)
                if news:
                    return "\n".join(f"- {item}" for item in news)  
                return "Nenhuma notícia encontrada para o município solicitado."
            except Exception as e:
                return f"Erro ao buscar notícias: {str(e)}"
        
        

    
        tools = [
            info_dengue,
            noticia_dengue,
    
        ]
        llm = GoogleGenerativeAI(model="gemini-pro")

        # Inicializar a memória da conversa
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Inicializar o agente
        agent = initialize_agent(
            tools,
            llm,
            agent="chat-conversational-react-description",
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
        )
        
      
        user_input = user_input.strip().title()
        
        
        st.session_state.messages.append({"role": "user", "content": user_input})


        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analisando os dados..."):
                            try:
                                df = carregar_dataset()        
                                estado_usuario, municipio_usuario, df_municipio, df_filtrado = analise_llm_municipio(df, user_input)

                               
                                prompt_inf = f"""
                                Você é um analista de dados experiente. O usuário consultou o município {municipio_usuario}.
                                Os dados carregados sobre a situação da dengue incluem:
                                
                                Dados do município: {df_municipio.to_dict()}
                                
                                Com base nesses dados:
                                - Resuma a situação mais recente (11/2024) da dengue em {municipio_usuario}.
                                - Dê algumas dicas importantes sobre cuidados que o usuário pode tomar.
                                """
                                response_inf = agent.run(input=prompt_inf)
                                st.session_state.messages.append({"role": "assistant", "content": response_inf})
                                st.markdown(response_inf)
                                
                                
                                prompt_new = f"""
                                O usuário consultou as notícias do município {user_input}.

                                Ao usar a ferramenta usando como entrada somente a entrada do usuário,
                                será retornada uma lista de notícias relevantes.

                                - Resuma as notícias mais importantes em formato de lista organizada.
                                """

                                response_new = agent.run(input=prompt_new)

    
                                
                                formatted_response = f"**As notícias mais relevantes sobre dengue são:**\n\n{response_new}"
                                st.markdown(formatted_response)

              
                            except ValueError as ve:
                                st.error(str(ve))
                                st.session_state.messages.append({"role": "assistant", "content": str(ve)})
                            except Exception as e:
                                erro_msg = f"Houve um erro ao consultar o município: {e}"
                                st.error(erro_msg)
                                st.session_state.messages.append({"role": "assistant", "content": erro_msg})        


elif choice == "Mapa Interativo":
    
    # Escolha de abas
    diase = st.sidebar.selectbox('Escolha a doença', ['Dengues', 'Gripes'])

    if diase == 'Gripes':
        
        abas = st.tabs(["Análise por Município", "Informações e Notícias", "Dados Epidemiológicos-Opção em desenvolvimento"])
        
        with abas[0]:
            create_dashboard()

        with abas[1]:
            noticias_informacoes_gripe()



    import streamlit as st
    from dengue_data_processing import carregar_dataset
    from analise_dengue import exibir_analise_municipio
    from noticias_dengue import exibir_noticias_informacoes
    from dados_dengue import exibir_dados_epidemiologicos
    

    if diase == "Dengues":
        df = carregar_dataset()

        if not df.empty:
            abas = st.tabs(["Análise por Município", "Informações e Notícias", "Dados Epidemiológicos", "Pred"])
            
            with abas[0]:
                exibir_analise_municipio(df)

            with abas[1]:
                exibir_noticias_informacoes()

            with abas[2]:
                exibir_dados_epidemiologicos(df)

        
