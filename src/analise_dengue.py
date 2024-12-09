import streamlit as st
import pandas as pd
from dengue_data_processing import carregar_dataset
import pydeck as pdk
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LinearRegression
import numpy as np

# Definir cores baseadas no risco
def definir_cor(risco):
    '''
    Determina a cor de um ponto em um mapa com base no nível de risco. O retorno é um valor RGBA (Red, Green, Blue, Alpha) para definir a cor e a opacidade.

    Parâmetros:
    risco (float): Representa o nível de risco associado ao município.
    Retorno:
    list: Uma lista com quatro valores inteiros [R, G, B, A], onde:
    R (Red): Intensidade de vermelho.
    G (Green): Intensidade de verde.
    B (Blue): Intensidade de azul.
    A (Alpha): Transparência (0 a 255).
    Regras de atribuição de cor:
    Risco Alto (risco > 7): Retorna vermelho [255, 0, 0, 160].
    Risco Moderado (1 < risco <= 6.99): Retorna amarelo [255, 255, 0, 160].
    Risco Baixo (risco <= 1): Retorna verde [0, 255, 0, 160].
    '''
    if risco > 7:
        return [255, 0, 0, 160]  # Vermelho (risco alto)
    elif 1 < risco <= 6.99:
        return [255, 255, 0, 160]  # Amarelo (risco moderado)
    else:
        return [0, 255, 0, 160]  # Verde (risco baixo)


# Predição de casos com regressão linear
def predicao_casos(df, municipio):
    # Filtrar dados do município
    df_mun = df[df['municipio'] == municipio]
    
    if len(df_mun) < 2:  # Garantir dados suficientes
        return None
    
    # Dados para o modelo
    df_mun['data_ordinal'] = pd.to_datetime(df_mun['data_week']).map(lambda x: x.toordinal())
    X = df_mun['data_ordinal'].values.reshape(-1, 1)
    y = df_mun['casos'].values
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    # Predição para a próxima data
    ultima_data = df_mun['data_ordinal'].max()
    proxima_data = np.array([[ultima_data + 10]])
    predicao = modelo.predict(proxima_data)
    
    return int(predicao[0]) if predicao > 0 else 0

# Adicionando zona de quarentena no mapa
def plotar_zona_quarentena(df, disseminacao_limite):
    # Garantir que a coluna 'disseminação' seja do tipo numérico
    df['disseminação'] = pd.to_numeric(df['disseminação'], errors='coerce')
    
    # Filtrar apenas os valores válidos (descartar NaN)
    df_filtrado = df[df['disseminação'] > disseminacao_limite].dropna(subset=['disseminação'])
    
    quarentena_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_filtrado,
        get_position="[longitude, latitude]",
        get_radius=9000,
        get_fill_color=[255, 50, 70, 70],  # Vermelho translúcido
        pickable=True
    )
    return quarentena_layer


def plotar_mapa(df, municipio):
    # Garantir que as colunas estejam no formato numérico correto
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['disseminação'] = pd.to_numeric(df['disseminação'], errors='coerce')
  

    # Garantir que não haja valores NaN
    df = df.dropna(subset=['longitude', 'latitude', 'cor', 'disseminação'])


# Camada de pontos principais
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[longitude, latitude]',
        get_radius=4000,
        get_fill_color='cor',
        pickable=True,
        auto_highlight=True,
    )
 # Camadas adicionais
    quarentena_layer = plotar_zona_quarentena(df, disseminacao_limite=3.0)
    
  # Destacar município selecionado
 
    df_selecionado = df[df['municipio'] == municipio]
    highlight_layer = pdk.Layer(
        'ScatterplotLayer',
        data=df_selecionado,
        get_position='[longitude, latitude]',
        get_radius=7000,  # Aumentar o raio
        get_fill_color=[0, 128, 255, 200],  # Azul
        pickable=True,
    )
    layers = [quarentena_layer, highlight_layer, scatter_layer ]


   
    # Configuração do mapa
    view_state = pdk.ViewState(
        latitude=df['latitude'].mean(),
        longitude=df['longitude'].mean(),
        zoom=6
    )
    
    # Renderizar mapa
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={
            'html': '''
                <b>Município:</b> {municipio}<br>
                <b>Casos:</b> {casos}<br>
                <b>Disseminação:</b> {disseminação}<br>
                <b>Temperatura:</b> {tempmed}°C<br>
                <b>Umidade:</b> {umidmed}%
            ''',
            'style': {'color': 'white'}
        }
    )
    st.pydeck_chart(r)
    

# Legenda do mapa
def exibir_legenda():
    st.markdown("""
    ### 
    - **Vermelho**: Risco alto
    - **Amarelo**: Risco moderado
    - **Verde**: Risco baixo
    - **Círculo médio Azul**: Município selecionado
    - **Círculo vermelho maior**: Zona de quarentena
    """)

# Função para plotar gráficos interativos
def plotar_graficos(df_municipio, df_min_max, municipio_usuario, estado_usuario):
    
    # previsoes, semanas_novas = prever_casos(df_municipio)
    
    fig = go.Figure()
    
    # Adicionar dados históricos
    fig.add_trace(go.Scatter(x=df_municipio['data_week'], y=df_municipio['casos'],
                             mode='lines+markers', name='Histórico de Casos'))
    
    # Configurar layout
    fig.update_layout(title=f'Previsão de Casos - {municipio_usuario}',
                      xaxis_title='Semana',
                      yaxis_title='Casos Estimados',
                      legend_title='Legenda')
    
    
    fig = go.Figure()
        # Verificar se há dados para o município
    if not df_municipio.empty:
        # Adiciona a linha do município selecionado
        fig.add_trace(go.Scatter(x=df_municipio['data_week'], y=df_municipio['casos'],
                                mode='lines+markers', name=f'{municipio_usuario} - Casos', line=dict(color='blue', width=4)))
    else:
        # Mensagem se não houver dados para o município
        st.warning(f'Não há dados disponíveis para o município {municipio_usuario} no período selecionado.')

    # Linha dos casos mínimos do estado
    fig.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('casos', 'min')],
                            mode='lines', name='Casos Mínimos (Estado)', line=dict(color='green', dash='dash')))
    # Linha dos casos máximos do estado
    fig.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('casos', 'max')],
                            mode='lines', name='Casos Máximos (Estado)', line=dict(color='red', dash='dash')))
    # Configurações do layout
    fig.update_layout(title=f'Comparação de Incidência de Casos {estado_usuario}', xaxis_title='Semana',
                    yaxis_title='Número de Casos', legend_title='Municípios')
    st.plotly_chart(fig)


    # Gráfico de linha para Temperatura Média (tempmed)
    fig_tempmed = go.Figure()

    # Adicionar a linha do município selecionado
    fig_tempmed.add_trace(go.Scatter(x=df_municipio['data_week'], y=df_municipio['tempmed'],
                                    mode='lines+markers', name=f'{municipio_usuario} - Temperatura Média', line=dict(color='blue', width=4)))

    # Adicionar a linha da temperatura mínima do estado
    fig_tempmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('tempmin', 'min')],
                                    mode='lines', name='Temperatura Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha da temperatura máxima do estado
    fig_tempmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('tempmax', 'max')],
                                    mode='lines', name='Temperatura Máxima (Estado)', line=dict(color='red', dash='dash')))

    # Adicionar título e rótulos
    fig_tempmed.update_layout(title=f'Comparação de Temperatura Média no Estado {estado_usuario}',
                            xaxis_title='Semana',
                            yaxis_title='Temperatura Média (°C)',
                            legend_title='Municípios')

    st.plotly_chart(fig_tempmed)


    # Gráfico de linha para Umidade Média (umidmed)
    fig_umidmed = go.Figure()

    # Adicionar a linha do município selecionado
    fig_umidmed.add_trace(go.Scatter(x=df_municipio['data_week'], y=df_municipio['umidmed'],
                                    mode='lines+markers', name=f'{municipio_usuario} - Umidade Média', line=dict(color='blue', width=4)))

    # Adicionar a linha da umidade mínima do estado
    fig_umidmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('umidmin', 'min')],
                                    mode='lines', name='Umidade Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha da umidade máxima do estado
    fig_umidmed.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('umidmax', 'max')],
                                    mode='lines', name='Umidade Máxima (Estado)', line=dict(color='red', dash='dash')))

    # Adicionar título e rótulos
    fig_umidmed.update_layout(title=f'Comparação de Umidade Média no Estado {estado_usuario}',
                            xaxis_title='Semana',
                            yaxis_title='Umidade Média (%)',
                            legend_title='Municípios')

    st.plotly_chart(fig_umidmed)


    # Gráfico de linha para Disseminação (disseminação)
    fig_disseminacao = go.Figure()

    # Adicionar a linha do município selecionado
    fig_disseminacao.add_trace(go.Scatter(x=df_municipio['data_week'], y=df_municipio['disseminação'],
                                        mode='lines+markers', name=f'{municipio_usuario} - Disseminação', line=dict(color='blue', width=4)))

    # Adicionar a linha da disseminação mínima do estado
    fig_disseminacao.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('disseminação', 'min')],
                                        mode='lines', name='Disseminação Mínima (Estado)', line=dict(color='green', dash='dash')))

    # Adicionar a linha da disseminação máxima do estado
    fig_disseminacao.add_trace(go.Scatter(x=df_min_max['data_week'], y=df_min_max[('disseminação', 'max')],
                                        mode='lines', name='Disseminação Máxima (Estado)', line=dict(color='red', dash='dash')))

    # Adicionar título e rótulos
    fig_disseminacao.update_layout(title=f'Comparação de Disseminação no Estado {estado_usuario}',
                                xaxis_title='Semana',
                                yaxis_title='Disseminação',
                                legend_title='Municípios')

    st.plotly_chart(fig_disseminacao)

import user_global
from user_global import MUNICIPIO_USUARIO, ESTADO_USUARIO
def exibir_analise_municipio(df):
    '''
    Realiza análises específicas para um município solicitado. A função valida a presença do município no dataframe, extrai dados detalhados para ele, e filtra dados dos municípios do mesmo estado para o último mês disponível.

    Parâmetros:
    df (DataFrame): O dataframe contendo informações epidemiológicas. Deve incluir as colunas:
    municipio: Nome dos municípios.
    estado: Nome dos estados associados aos municípios.
    data_week: Coluna de datas (tipo datetime ou string que possa ser convertida).
    municipio_usuario (str): Nome do município a ser analisado.
    Retorno:
    estado_usuario (str): Estado do município solicitado.
    municipio_usuario (str): Nome do município solicitado (confirmado no dataset).
    df_municipio (DataFrame): Subconjunto do dataframe contendo apenas os dados do município solicitado.
    df_filtrado (DataFrame): Dados filtrados para todos os municípios do mesmo estado durante o último mês disponível.
    Exceções:
    ValueError: Lançada se o município solicitado não for encontrado no dataframe.
    Fluxo de processamento:
    Conversão de Datas: Garante que a coluna data_week esteja no formato datetime.
    Validação de Município: Verifica se o município informado está presente no dataset.
    Filtragem de Dados:
    Seleciona os dados do município solicitado.
    Determina o estado do município.
    Filtra os dados de todos os municípios do estado correspondente para o último mês disponível.
    Retorno: Fornece os dados detalhados para análises adicionais.

    '''
    
    st.title("🦟Análise da Situação do Município - Dengue🦟")
    
    # Conversão e tratamento dos dados
    df['disseminação'] = pd.to_numeric(df['disseminação'], errors='coerce')
    df['casos'] = pd.to_numeric(df['casos'], errors='coerce')
    df['casos_est'] = pd.to_numeric(df['casos_est'], errors='coerce')
    df['incidência_100khab'] = pd.to_numeric(df['incidência_100khab'], errors='coerce')
    df['data_week'] = pd.to_datetime(df['data_week'], errors='coerce')
    municipio_usuario = MUNICIPIO_USUARIO
    municipio_usuario = st.sidebar.selectbox("Selecione seu município", sorted(df['municipio'].unique()))
    estado_usuario = ESTADO_USUARIO
    estado_usuario = df[df['municipio'] == municipio_usuario]['estado'].values[0]
    df_estado = df[df['estado'] == estado_usuario]
    data_maxima = df_estado['data_week'].max()
    filtro_periodo = st.radio("Filtrar por", ('Último Mês', 'Último Ano'))
    user_global.MUNICIPIO_USUARIO = municipio_usuario
    user_global.ESTADO_USUARIO = estado_usuario
    # Definir o período de filtragem
    if filtro_periodo == 'Último Mês':
        data_inicial = data_maxima - pd.DateOffset(months=1)
    elif filtro_periodo == 'Último Ano':
        data_inicial = data_maxima - pd.DateOffset(years=1)

    df_filtrado = df_estado[(df_estado['data_week'] >= data_inicial) & (df_estado['data_week'] <= data_maxima)].copy()

    
    # Calcular risco e aplicar cor
    df_filtrado.loc[:, 'risco_dengue'] = df_filtrado['casos_est'] * 0.1 + df_filtrado['casos'] * 0.3 + df_filtrado['incidência_100khab'] * 0.1 + df_filtrado['disseminação'] * 5
    df_filtrado.loc[:, 'cor'] = df_filtrado['risco_dengue'].apply(definir_cor)
    df_municipio = df_filtrado[df_filtrado['municipio'] == municipio_usuario]
    
    # Exibir legenda e mapa
    exibir_legenda()
    
    st.write("O mapa corresponde à opção de um mês.")
    plotar_mapa(df_filtrado, municipio_usuario)
    
    predicao = predicao_casos(df_municipio, municipio_usuario)
    if predicao is not None:
        st.write(f"**Predição de casos futuros no município {municipio_usuario}:** {predicao}")

    # Criar e exibir gráficos
    df_min_max = df_filtrado.groupby('data_week').agg({
        'casos': ['min', 'max'],
        'incidência_100khab': ['min', 'max'],
        'disseminação': ['min', 'max'],
        'umidmed': ['min', 'max'],
        'umidmin': ['min', 'max'],
        'umidmax': ['min', 'max'],
        'tempmed': ['min', 'max'],
        'tempmin': ['min', 'max'],
        'tempmax': ['min', 'max']
    }).reset_index()

    
    plotar_graficos(df_municipio, df_min_max, municipio_usuario, estado_usuario)

    return estado_usuario, municipio_usuario, df_municipio, df_filtrado 

