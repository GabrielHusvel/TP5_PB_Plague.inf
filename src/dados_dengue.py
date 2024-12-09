import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

def exibir_dados_epidemiologicos(df):
    '''
    Função para exibir dados epidemiológicos e gerar visualizações interativas em um aplicativo Streamlit.

    A função permite o upload de arquivos CSV, filtragem de dados por estados e municípios, 
    criação de gráficos interativos (linhas, barras, pizza, histograma), e exibição de dados em um mapa interativo.
    Além disso, oferece a funcionalidade de download dos dados filtrados.

    Parâmetros:
    ----------
    df : pandas.DataFrame
        DataFrame contendo os dados epidemiológicos.

    Funcionalidades:
    -----------------
    1. **Incorporação do Power BI**:
        - Um painel do Power BI é exibido em um iframe embutido.

    2. **Upload de Arquivos**:
        - Permite ao usuário carregar um arquivo CSV contendo dados epidemiológicos.

    3. **Filtragem de Dados**:
        - Filtragem por estados e municípios selecionados pelo usuário.
        - Seleção de colunas específicas para exibição.

    4. **Intervalo de Datas**:
        - O usuário pode definir uma data inicial e final para filtrar os dados temporais.

    5. **Agrupamento e Processamento de Dados**:
        - Agrupa os dados por município e calcula somatórios (casos, estimativa de casos) 
          e médias (temperatura média e umidade média).
        - Reduz as casas decimais das colunas numéricas relevantes.

    6. **Mapa Interativo**:
        - Um mapa Pydeck é exibido com pontos representando municípios, indicando casos, 
          estimativa de casos, temperatura média e umidade.

    7. **Gráficos**:
        - Linhas:
          - Evolução dos casos ao longo do tempo.
          - Variação da temperatura e umidade ao longo do tempo.
        - Barras:
          - Comparação entre duas variáveis selecionadas.
        - Pizza:
          - Distribuição percentual de uma variável numérica com base em categorias.
        - Histograma:
          - Frequência de dados categóricos ou numéricos.

    8. **Download de Dados**:
        - Permite ao usuário baixar os dados filtrados em formato CSV.

    9. **Interface Interativa**:
        - Uso de widgets como seletores múltiplos, caixas de seleção e barras de progresso para melhorar a experiência do usuário.
    '''
    st.title(f"📊Dados Epidemiológicos📊")
    # Incorporar o Power BI no Streamlit
    st.components.v1.iframe("https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc", height=600)


    st.write('Here you need upload the csv with data from 2010 to 2024. \nHas customizable graphics and an interactive map. \n Google Drive Data link: https://drive.google.com/drive/folders/19OGg_d3S9L6wc99I3FZxc5Mn9Ba-jXos?usp=drive_link \n DropBox Data Link: https://www.dropbox.com/scl/fo/wuwb1zpcxuvvlnyfrkcpf/AIBXL31_YW6QpjbWKyG-v2s?rlkey=8vzsj4lddvx5sh61ce8hl2df1&st=zvb71bzb&dl=0')

    uploaded_file = st.file_uploader('Faça o upload do arquivo da região desejada.')
    if uploaded_file:
        @st.cache_data
        def load_data(uploaded_file):
            df = pd.read_csv(uploaded_file)
            return df
        
        df = load_data(uploaded_file)       
        st.write('Dados carregados com sucesso!')

        # Certifique-se de que a coluna 'estado' seja do tipo string e remova valores nulos
        df['estado'] = df['estado'].astype(str)
        df = df[df['estado'].notna()]
    
        # Multiselect para selecionar as colunas desajas
        selected_columns = st.multiselect("Selecione as colunas. :)", df.columns.tolist(), default=df.columns.tolist())

        # Multiselect para selecionar os estados, ordenados alfabeticamente
        selected_estado = st.multiselect(" Selecione os estados.", sorted(df['estado'].astype(str).unique()))
        df_filtrado = df[(df['estado'].isin(selected_estado))]

        # Multiselect para selecionar os municípios, ordenados alfabeticamente
        selected_municipio = st.multiselect("Selecione os municípios.", sorted(df_filtrado['municipio'].astype(str).unique()), default=sorted(df_filtrado['municipio'].astype(str).unique()))
        df_filtrado = df_filtrado[(df_filtrado['municipio'].isin(selected_municipio))]
        st.write('Dados filtrados:')
        st.write(len(df_filtrado), ' Registros')
        st.dataframe(df_filtrado[selected_columns])


        def convert_df(df):
            return df.to_csv().encode('utf-8')

        csv = convert_df(df_filtrado)
        # Baixar csv
        st.download_button(
            label='Baixar dados filtrados',
            data=csv,
            file_name='dados_filtrados.csv',
            mime='text/csv',
        )

        if selected_municipio:
            # Converter a coluna para o tipo datetime
            df_filtrado['data_week'] = pd.to_datetime(df_filtrado['data_week'])

            # Selecionar o intervalo de datas para visualização
            data_inicial = st.date_input('Data inicial', value=df_filtrado['data_week'].min(), min_value=df_filtrado['data_week'].min(), max_value=df_filtrado['data_week'].max())
            data_final = st.date_input('Data final', value=df_filtrado['data_week'].max(), min_value=df_filtrado['data_week'].min(), max_value=df_filtrado['data_week'].max())

            # Filtrar os dados para o intervalo de datas selecionado
            dados_filtrados = df_filtrado[(df_filtrado['data_week'] >= pd.to_datetime(data_inicial)) & (df_filtrado['data_week'] <= pd.to_datetime(data_final))]

            # Agrupar os dados por município e somar os casos e a estimativa de casos
            dados_agrupados = dados_filtrados.groupby(['municipio', 'latitude', 'longitude']).agg(
                casos=('casos', 'sum'),
                casos_est=('casos_est', 'sum'),
                tempmed=('tempmed', 'mean'),  # Somar as temperaturas médias
                umidmed=('umidmed', 'mean')   # Somar as umidades médias
            ).reset_index()

            # Limitar o número de casas decimais de tempmed e umidmed
            dados_agrupados['tempmed'] = dados_agrupados['tempmed'].round(2)
            dados_agrupados['umidmed'] = dados_agrupados['umidmed'].round(2)

        # Verificar se há dados após a filtragem
        if selected_municipio:

            # Criar o mapa interativo
            layer = pdk.Layer(
                'ScatterplotLayer',
                data=dados_agrupados,
                get_position='[longitude, latitude]',  # Coordenadas corretas
                get_radius=9000,  # Ajustar o tamanho dos pontos
                get_fill_color='[255, 0, 0, 160]',  # Vermelho translúcido
                pickable=True
            )

            view_state = pdk.ViewState(
                latitude=-15.7801,  # Posição central do Brasil
                longitude=-47.9292,
                zoom=4,
                pitch=50
            )

            r = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{municipio} Casos: {casos} Estimativa: {casos_est} Temp: {tempmed} nUmidade: {umidmed} %"}
            )

            st.pydeck_chart(r)


            # Evolução dos casos ao longo do tempo
            fig = px.line(dados_filtrados, x='data_week', y='casos', color='municipio', title='Evolução dos casos ao longo do tempo')
            st.plotly_chart(fig)

            # Temperatura ao longo do tempo
            fig = px.line(dados_filtrados, x='data_week', y='tempmed', color='municipio', title='Temperatura ao longo do tempo')
            st.plotly_chart(fig)
            
            # Úmidade ao longo do tempo
            fig = px.line(dados_filtrados, x='data_week', y='umidmed', color='municipio', title='Úmidade ao longo do tempo')
            st.plotly_chart(fig)
        
        
        if selected_municipio:   
            # Seletor de colunas
            colunas = dados_filtrados.columns.tolist()

            # Gráfico de barras
            st.subheader('Gráfico de Barras')
            x_col_barra = st.selectbox('Para o eixo X indico selecionar data, municipios ou estados', colunas, key='x_barra')
            y_col_barra = st.selectbox('Para o eixo Y indico selecionar uma coluna numérica ', colunas, key='y_barra')

            if x_col_barra and y_col_barra:
                grafico_barra = px.bar(dados_filtrados, x=x_col_barra, y=y_col_barra, title=f'Gráfico de Barras: {x_col_barra} vs {y_col_barra}')
                st.plotly_chart(grafico_barra)


            # Gráfico de pizza 
            st.subheader('Gráfico de Pizza')
            pie_col = st.selectbox('Selecione a coluna para os valores, indico selecionar uma coluna numérica', colunas, key='pie')
            pie_col_names = st.selectbox('Selecione a coluna para os nomes como data, municipios ou estados', colunas, key='pie_names')

            if pie_col and pie_col_names:
                grafico_pizza = px.pie(dados_filtrados, values=pie_col, names=pie_col_names, title=f'Gráfico de Pizza: {pie_col_names} - {pie_col}')
                st.plotly_chart(grafico_pizza)
                

            # Histograma
            st.subheader('Histograma')
            x_col_histo = st.selectbox('Selecione o eixo x, indico selecionar uma coluna categórica', colunas, key='x_histo')
            y_col_histo = st.selectbox('Selecione o eixo Y, indico selecionar uma coluna numérica', colunas, key='y_histo')
            grafico_histograma = px.histogram(dados_filtrados, x=x_col_histo, y=y_col_histo, nbins=200, )
            st.plotly_chart(grafico_histograma)

    else:
        st.write('Nenhum arquivo foi carregado.')
