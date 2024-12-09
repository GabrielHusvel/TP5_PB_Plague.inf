# import pandas as pd
# import plotly.express as px
# import streamlit as st

# # Leitura dos dados
# @st.cache_data
# def carregar_dados(arquivo_csv):
#     if arquivo_csv is not None:
#         # Verifica se é o tipo correto para leitura
#         if isinstance(arquivo_csv, str):
#             # Se for um caminho
#             df = pd.read_csv(arquivo_csv)
#         else:
#             # Caso seja o objeto UploadedFile do Streamlit
#             df = pd.read_csv(arquivo_csv)
#         df['data'] = pd.to_datetime(
#             df['epiweek'].astype(str) + df['epiyear'].astype(str) + '0', 
#             format='%U%Y%w', 
#             errors='coerce'
#         )
#         return df
#     else:
#         return None


# # # Função principal
# # def map_capital():
# df = carregar_dados('data_sus/infogripe-master/Dados/InfoGripe/2020-2024/capitais_serie_estimativas_fx_etaria.csv')
# print(df.columns)

# df['casos_notificados'] = df['casos_notificados'].fillna(0)  # Substitui NaN por 0

# if df[['latitude', 'longitude', 'casos_notificados']].isnull().any().any():
#     st.error("Os dados contêm valores inválidos. Por favor, corrija antes de prosseguir.")
# else:
#     st.write("Todos os dados estão válidos.")

# # Colunas que representam variações do vírus
# variacao_colunas = ['Q1', 'Q3', 'IC80I', 'IC80S', 'IC90I', 'IC90S', 'LI', 'LS']

# # Transformando essas colunas em uma única coluna chamada "variacao"
# df_long = df.melt(
#     id_vars=['latitude', 'longitude', 'CO_MUN_RES_nome', 'casos_notificados', 'epiyear', 'epiweek'],  # Incluí 'epiyear' e 'epiweek'
#     value_vars=variacao_colunas,  # Colunas a serem derretidas
#     var_name='variacao',          # Nome da nova coluna que conterá os nomes das colunas originais
#     value_name='valor'            # Nome da nova coluna que conterá os valores
# )
# df_long['variacao'] = df_long['variacao'].fillna(0)
# # Filtros de ano e semana
# anos_disponiveis = sorted(df_long['epiyear'].unique())
# semanas_disponiveis = sorted(df_long['epiweek'].unique())

# ano_selecionado = st.sidebar.selectbox("Selecione o ano", anos_disponiveis)
# semana_selecionada = st.sidebar.selectbox("Selecione a semana epidemiológica", semanas_disponiveis)

# # Aplicando filtros de ano e semana
# df_filtrado = df_long[
#     (df_long['epiyear'] == ano_selecionado) &
#     (df_long['epiweek'] == semana_selecionada)
# ]

# # Filtro por variações selecionadas
# variacoes_selecionadas = st.sidebar.multiselect(
#     "Selecione as variações do vírus", 
#     df_long['variacao'].unique(), 
#     default=df_long['variacao'].unique()  # Selecionar todas por padrão
# )
# df_filtrado = df_filtrado[df_filtrado['variacao'].isin(variacoes_selecionadas)]
# print(df_filtrado)
# # Resumo dos dados
# st.subheader("Resumo dos Dados Filtrados")
# if not df_filtrado.empty:
#     total_casos = df_filtrado['casos_notificados'].sum()
#     municipio_mais_afetado = df_filtrado.groupby('CO_MUN_RES_nome')['casos_notificados'].sum().idxmax()
#     st.write(f"**Total de casos notificados:** {total_casos}")
#     st.write(f"**Município mais afetado:** {municipio_mais_afetado}")
# else:
#     st.warning("Nenhum dado disponível para as opções selecionadas.")

# # Mapa interativo
# st.subheader("Mapa Interativo de Casos")
# if not df_filtrado.empty:
#     mapa = px.scatter_geo(
#         data_frame=df_filtrado,
#         lat="latitude",
#         lon="longitude",
#         size="casos_notificados",
#         color="variacao",  # Agora usamos a coluna única de variações
#         hover_name="CO_MUN_RES_nome",
#         title=f"Mapa de Casos - Ano {ano_selecionado}, Semana {semana_selecionada}",
#     )
#     st.plotly_chart(mapa)

# # Gráfico por variação do vírus
# st.subheader("Casos por Variação do Vírus")
# if not df_filtrado.empty:
#     grafico_virus = df_filtrado.groupby('variacao')['casos_notificados'].sum().reset_index()
#     fig_var = px.bar(grafico_virus, x='variacao', y='casos_notificados', color='variacao', title="Distribuição por Variação do Vírus")
#     st.plotly_chart(fig_var)

# # Gráfico de casos por faixa etária
# st.subheader("Casos por Faixa Etária")
# if not df_filtrado.empty:
#     grafico_etaria = df_filtrado.groupby('fx_etaria')['casos_notificados'].sum().reset_index()
#     fig_etaria = px.bar(grafico_etaria, x='fx_etaria', y='casos_notificados', color='fx_etaria', title="Distribuição por Faixa Etária")
#     st.plotly_chart(fig_etaria)
# else:
#     st.warning("Nenhum dado disponível para as opções selecionadas.")