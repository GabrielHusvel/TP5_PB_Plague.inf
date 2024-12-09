# import pandas as pd
# import streamlit as st
# from sklearn.cluster import KMeans
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, r2_score
# import plotly.express as px


# def predict_dengue(df):

#     # Limpeza e seleção de dados
#     dados = df.dropna()  # Remover dados nulos
#     X = dados[['tempmed', 'umidmed', 'população']]  # Variáveis independentes
#     y = dados['casos_est']  # Variável dependente

#     # Divisão dos dados em treino e teste
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Treinamento do modelo de regressão
#     modelo = RandomForestRegressor(random_state=42)
#     modelo.fit(X_train, y_train)

#     # Previsões nos dados de teste
#     previsoes = modelo.predict(X_test)

#     # Avaliação do modelo
#     mse = mean_squared_error(y_test, previsoes)
#     r2 = r2_score(y_test, previsoes)

#     # Adicionar as previsões futuras ao dataframe
#     df['previsao_futura'] = modelo.predict(X)

#     # Salvar previsões futuras em um arquivo CSV
#     df.to_csv("previsoes_futuras.csv", index=False)

#     # Visualização no Streamlit
#     st.title("Análise de Regressão e Clustering de Dengue")

#     # Mostrar métricas de avaliação
#     st.subheader("Métricas do Modelo de Regressão")
#     st.write(f"**Erro Quadrático Médio (MSE):** {mse:.2f}")
#     st.write(f"**R² (Coeficiente de Determinação):** {r2:.2f}")

#     # Visualizar clusters com Plotly
#     st.subheader("Clusters de Municípios")
#     dados_cluster = df[['casos', 'casos_est']].dropna()
#     kmeans = KMeans(n_clusters=3, random_state=42)
#     dados_cluster['cluster'] = kmeans.fit_predict(dados_cluster)

#     fig = px.scatter(
#         dados_cluster,
#         x='casos',
#         y='casos_est',
#         color='cluster',
#         title="Clusters Baseados em Casos Estimados e Reais"
#     )
#     st.plotly_chart(fig)

#     # Tabela com dados e previsões
#     st.subheader("Dados com Previsões Futuras")
#     st.dataframe(df[['municipio', 'estado', 'casos', 'casos_est', 'previsao_futura']])

#     # Botão para download do CSV
#     st.download_button(
#         label="Baixar Previsões Futuras",
#         data=df.to_csv(index=False),
#         file_name="previsoes_futuras.csv",
#         mime="text/csv"
#     )

#     # Agente sugerindo ações
#     def agente_recomendacao(cluster):
#         if cluster == 0:
#             return "Monitoramento de rotina recomendado."
#         elif cluster == 1:
#             return "Risco moderado: aumentar as campanhas de conscientização."
#         elif cluster == 2:
#             return "Risco elevado: intensificar medidas de controle e prevenção."
#     dados['recomendacao'] = dados['cluster'].apply(agente_recomendacao)


#     import plotly.express as px

#     fig = px.scatter(dados, x='casos', y='tempmed', color='cluster',
#                     title="Análise de Clusters de Municípios")
#     st.plotly_chart(fig)
