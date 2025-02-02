import pandas as pd
import streamlit as st
import requests
from pages.parte2 import dados_jogadores
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import commonteamroster

st.title("Análise Estatística de Jogos")

df_p = dados_jogadores.get_players(1610612739)
df_g = dados_jogadores.get_player_games(dados_jogadores.player_selectbox(df_p))

df_f = dados_jogadores.get_player_games_df(df_g)

df_f

df_mean = df_f[["Pontos", "Rebotes Totais", "Assistências"]].mean()

colunas_comum = df_f.columns.intersection(df_mean.index)

abaixo_media = ((df_f[colunas_comum] < df_mean.loc[colunas_comum]).mean()) * 100

df_median = df_f[["Pontos", "Rebotes Totais", "Assistências"]].median()

df_f_alinhado, df_median_alinhado = df_f.align(df_median, axis=1, join='inner')

abaixo_mediana = (df_f_alinhado < df_median_alinhado).mean() * 100

df_mode = df_f[["Pontos", "Rebotes Totais", "Assistências"]].mode().iloc[0]
frequencia_moda = df_f[["Pontos", "Rebotes Totais", "Assistências"]].apply(lambda x: (x == df_mode[x.name]).sum())

df_f_alinhado, df_mode_alinhado = df_f.align(df_mode, axis=1, join='inner')

abaixo_moda = (df_f_alinhado < df_mode_alinhado).mean() * 100

df_std = df_f[["Pontos", "Rebotes Totais", "Assistências"]].std()

resultados = pd.DataFrame({
    "Média": df_mean,
    "Mediana": df_median,
    "Moda": df_mode,
    "Freq Moda": frequencia_moda,
    "Desvio Padrão": df_std,
    "% Abaixo da Média": abaixo_media,
    "% Abaixo da Mediana": abaixo_mediana,
    "% Abaixo da Moda": abaixo_moda
})

# Exibir a tabela no Streamlit
st.subheader("Resumo das Métricas Estatísticas")
st.write(resultados)