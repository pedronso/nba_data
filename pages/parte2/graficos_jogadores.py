import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from pages.parte2 import dados_jogadores

st.title("Gráficos dos Jogadores")

def plot_distribution_altair(df, coluna, nome_estatistica):
    media = df[coluna].mean()
    mediana = df[coluna].median()
    moda = df[coluna].mode()[0] if not df[coluna].mode().empty else None

    # Criação condicional do DataFrame de estatísticas
    estatisticas = [
        ('Média', media, 'blue'),
        ('Mediana', mediana, 'orange')
    ]
    if moda is not None:
        estatisticas.append(('Moda', moda, 'green'))

    # Convertendo a lista para um DataFrame
    linhas = pd.DataFrame(estatisticas, columns=['Estatística', 'Valor', 'Cor'])

    # Gráfico de distribuição
    chart = alt.Chart(df).mark_bar(opacity=0.5, color='skyblue').encode(
        alt.X(coluna, bin=alt.Bin(maxbins=7), title=nome_estatistica),
        alt.Y('count()', title='Frequência')
    ).properties(
        title=f'Distribuição de {nome_estatistica}'
    )

    # Gráfico das linhas das estatísticas
    linhas_chart = alt.Chart(linhas).mark_rule().encode(
        x='Valor:Q',
        color=alt.Color('Estatística:N', scale=alt.Scale(domain=linhas['Estatística'], range=linhas['Cor'])),
        size=alt.value(2),
        tooltip=['Estatística', 'Valor']
    )

    # Combinando os gráficos
    st.altair_chart(chart + linhas_chart, use_container_width=True)

def plot_box_plot_plotly(df, colunas):
    fig = px.box(df, y=colunas, points="all", title="Box Plot de Pontos, Rebotes e Assistências")
    fig.update_layout(yaxis_title="Valores")
    st.plotly_chart(fig)

df_p = dados_jogadores.get_players(1610612739)
df_g = dados_jogadores.get_player_games(dados_jogadores.player_selectbox(df_p))

df_f = dados_jogadores.get_player_games_df(df_g)

st.subheader("Distribuição de Pontos, Rebotes e Assistências")
plot_distribution_altair(df_f, "Pontos", "Pontos por Jogo")
plot_distribution_altair(df_f, "Rebotes Totais", "Rebotes por Jogo")
plot_distribution_altair(df_f, "Assistências", "Assistências por Jogo")

st.subheader("Box Plot Interativo")
plot_box_plot_plotly(df_f, ["Pontos", "Rebotes Totais", "Assistências"])