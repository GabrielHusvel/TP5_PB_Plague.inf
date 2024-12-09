import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from gripe_data_processing import carregar_dados
import user_global

def create_dashboard():
    st.title("🦠Monitoramento Epidemiológico de Gripes - Brasil🦠")
    
    # Carregar os dados
    df_municipios, df_capitais = carregar_dados()

    # Filtro por ano epidemiológico
    anos = df_municipios['Ano epidemiológico'].unique()
    ano_selecionado = st.sidebar.selectbox('Selecione o Ano epidemiológico', anos)

    # Filtro por semana epidemiológica
    semanas = df_municipios['Semana epidemiológica'].unique()
    semana_inicial, semana_final = st.sidebar.select_slider(
        'Selecione o intervalo de semanas epidemiológicas',
        options=semanas,
        value=(min(semanas), max(semanas))
    )

    # Filtrar os dados com base nos filtros aplicados
    df_filtrado = df_municipios[
        (df_municipios['Ano epidemiológico'] == ano_selecionado) &
        (df_municipios['Semana epidemiológica'] >= semana_inicial) &
        (df_municipios['Semana epidemiológica'] <= semana_final)
    ]

    # Certifique-se de que as colunas "transmissão comunitária" e "População" estão no dataframe antes de criar o gráfico
    df_agrupado = df_filtrado.groupby('municipio').agg({
        'casos estimados': 'sum', 
        'latitude': 'first', 
        'longitude': 'first', 
        'transmissão comunitária': 'first',
        'média móvel': 'mean',
        'Semana epidemiológica' : 'count'
    }).reset_index()

    # Soma dos casos estimados no período filtrado para o estado
    soma_casos_estimados = df_agrupado['casos estimados'].sum()

    # Exibir a soma dos casos estimados
    st.write(f"Soma dos casos estimados no período selecionado: {soma_casos_estimados:,.2f}")

    # Criando o gráfico de mapa
    fig = go.Figure(go.Scattermapbox(
        lat=df_agrupado['latitude'],
        lon=df_agrupado['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color=df_agrupado['casos estimados'],
            # Definindo uma escala de cores personalizada: verde -> amarelo -> laranja -> vermelho
            colorscale=[
                [0, "yellow"],    # Menos casos
                [0.25, "orange"],
                [0.5, "red"],
                [1, "purple"]       # Mais casos
            ],
            cmin=df_agrupado['casos estimados'].min(),  # Valor mínimo de casos
            cmax=df_agrupado['casos estimados'].max(),  # Valor máximo de casos
            showscale=True,
            sizemode='area',
        ),
        
        # Adicionar mais dados ao hover text (município, casos estimados, transmissão comunitária, população)
        text=df_agrupado['municipio'] + 
            '<br>Casos estimados: ' + df_agrupado['casos estimados'].apply(lambda x: f"{x:,.2f}") +
            '<br>Transmissão comunitária: ' + df_agrupado['transmissão comunitária']
    ))

    # Definindo o layout do mapa
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=5,
        mapbox_center={"lat": df_agrupado['latitude'].mean(), "lon": df_agrupado['longitude'].mean()},
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)
    
    # Filtros adicionais para limitar os dados
    municipios = df_filtrado['municipio'].unique()
    municipio_selecionado = st.sidebar.selectbox('Selecione o Município', municipios)
    user_global.MUNICIPIO_USUARIO_GRIPE = municipio_selecionado
    # Filtrar os dados com base no município selecionado
    df_filtrado_municipio = df_filtrado[df_filtrado['municipio'] == municipio_selecionado]

    # Calcular a média móvel apenas para o município selecionado
    df_filtrado_municipio['média móvel'] = df_filtrado_municipio['casos estimados'].rolling(window=4).mean()

    # Agrupar os dados por 'Semana epidemiológica' para evitar múltiplas linhas
    df_agrupado = df_filtrado_municipio.groupby('Semana epidemiológica', as_index=False).agg({
        'casos estimados': 'mean',
        'média móvel': 'mean'
    })

    # Gráfico de casos notificados apenas para o município selecionado
    fig_casos = px.line(
        df_agrupado,
        x='Semana epidemiológica', 
        y='casos estimados',
        labels={'casos estimados': 'Casos Notificados', 'Semana epidemiológica': 'Semana Epidemiológica'},
        title=f'Casos Notificados ao Longo das Semanas ({ano_selecionado}) - {municipio_selecionado}'
    )

    # Gráfico de média móvel para o município selecionado
    fig_media_movel = px.line(
        df_agrupado, 
        x='Semana epidemiológica', 
        y='média móvel',
        labels={'média móvel': 'Média Móvel', 'Semana epidemiológica': 'Semana Epidemiológica'},
        title=f'Média Móvel ao Longo das Semanas ({ano_selecionado}) - {municipio_selecionado}'
    )

    # Layout para ambos os gráficos
    fig_casos.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color='white',
    )

    fig_media_movel.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color='white',
    )
    
    # Exibir os gráficos no Streamlit
    st.plotly_chart(fig_casos)
    st.plotly_chart(fig_media_movel)
    
    return 
