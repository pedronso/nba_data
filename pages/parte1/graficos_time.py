import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
import locale
from nba_api.stats.static import teams
from pages.parte1 import lista_jogos
from babel.dates import format_date

def plot_bars(df):
    df["Data do Jogo"] = pd.to_datetime(df["Data do Jogo"], format="%d/%m/%Y")
    
    df.sort_values("Data do Jogo", inplace=True)
    
    df["Mês_Ano"] = df["Data do Jogo"].dt.to_period("M") #YYYY-MM
    df["Mês"] = df["Data do Jogo"].apply(
        lambda x: format_date(x, "MMMM", locale="pt_BR")
    ).str.capitalize()
    df["Ano"] = df["Data do Jogo"].dt.year
    
    monthly_totals = (
        df.groupby(["Mês_Ano", "Mês", "Ano"])[["Vitória", "Derrota"]]
        .sum()
        .reset_index()
        .sort_values("Mês_Ano")
    )

    melted_totals = monthly_totals.melt(
        id_vars=["Mês", "Ano"], 
        value_vars=["Vitória", "Derrota"], 
        var_name="Resultado", 
        value_name="Quantidade"
    )

    # melted_totals

    fig = alt.Chart(melted_totals).mark_bar().encode(
        x=alt.X("Mês:N", sort=list(monthly_totals["Mês"].unique())),  #ordem dos meses
        y=alt.Y("Quantidade:Q", title="Quantidade"),
        color=alt.Color("Resultado:N", scale=alt.Scale(domain=["Vitória", "Derrota"], range=["green", "red"])),
        tooltip=["Mês", "Resultado", "Quantidade"]
    ).properties(
        title="Vitórias e Derrotas por Mês"
    )
    
    st.altair_chart(fig, use_container_width=True)

def plot_grouped_bars(df):
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    df["Data do Jogo"] = pd.to_datetime(df["Data do Jogo"], format="%d/%m/%Y")

    df["Mês"] = df["Data do Jogo"].dt.strftime("%B")
    df["Ano"] = df["Data do Jogo"].dt.year

    df["Vitórias Casa"] = df.apply(lambda x: 1 if x["Vitória"] and x["Localidade"] == "Home" else 0, axis=1)
    df["Vitórias Fora"] = df.apply(lambda x: 1 if x["Vitória"] and x["Localidade"] == "Road" else 0, axis=1)
    df["Derrotas Casa"] = df.apply(lambda x: 1 if x["Derrota"] and x["Localidade"] == "Home" else 0, axis=1)
    df["Derrotas Fora"] = df.apply(lambda x: 1 if x["Derrota"] and x["Localidade"] == "Road" else 0, axis=1)

    result_df = (
        df.groupby(["Mês", "Ano"], as_index=False)[
            ["Vitórias Casa", "Vitórias Fora", "Derrotas Casa", "Derrotas Fora"]
        ]
        .sum()
    )

    result_df["mes_ano"] = pd.to_datetime(result_df["Ano"].astype(str) + "-" + result_df["Mês"], format="%Y-%B")
    result_df["Período"] = result_df["mes_ano"].dt.strftime("%b %Y")  # label

    df_melted = result_df.melt(
        id_vars=["Período", "mes_ano"],
        value_vars=["Vitórias Casa", "Vitórias Fora", "Derrotas Casa", "Derrotas Fora"],
        var_name="Resultado",
        value_name="Quantidade"
    )
    
    fig = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X("Resultado:N", title=""),
        y=alt.Y("Quantidade:Q", title="Quantidade"),
        color=alt.Color("Resultado:N", scale=alt.Scale(
            domain=["Vitórias Casa", "Vitórias Fora", "Derrotas Casa", "Derrotas Fora"],
            range=["green", "blue", "red", "sienna"]
        )),
        column=alt.Column(
            "Período:N",
            title="Mês-Ano",
            sort=list(df_melted.sort_values("mes_ano")["Período"].unique())
        ),
        tooltip=["Período", "Resultado", "Quantidade"]
    ).properties(
        width=100,
        title="Vitórias e Derrotas por Localidade"
    )

    st.altair_chart(fig, use_container_width=False)

def plot_histogram(df):
    df[['Pontos Marcados', 'Pontos Sofridos']] = df['Placar'].str.split(' : ', expand=True)
    df['Pontos Marcados'] = df['Pontos Marcados'].astype(int)
    df['Pontos Sofridos'] = df['Pontos Sofridos'].astype(int)

    hist_pontos_marcados = go.Histogram(
        x=df['Pontos Marcados'],
        nbinsx=20,
        name='Pontos Marcados',
        opacity=0.9,
        marker=dict(color='green', line=dict(color='black', width=0.5)),
        bingroup=1,
        hovertemplate="<b>Pontos Marcados:</b> %{x}<br><b>Frequência:</b> %{y}<extra></extra>"
    )

    hist_pontos_sofridos = go.Histogram(
        x=df['Pontos Sofridos'],
        nbinsx=20,
        name='Pontos Sofridos',
        opacity=0.9,
        marker=dict(color='red', line=dict(color='black', width=0.5)),
        bingroup=1,
        hovertemplate="<b>Pontos Sofridos:</b> %{x}<br><b>Frequência:</b> %{y}<extra></extra>"
    )

    fig = go.Figure(data=[hist_pontos_marcados, hist_pontos_sofridos])

    fig.update_layout(
        title="Distribuição dos Pontos Marcados e Sofridos",
        barmode='group',
        xaxis_title="Pontos",
        yaxis_title="Frequência",
        bargap=0.2,
        template='plotly_white',
        height=600,
        width=1000,
        hovermode="x unified",
        xaxis=dict(showgrid=True, zeroline=False),
        yaxis=dict(showgrid=True, zeroline=False)
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_pie_chart(df):
    resultados = {
        "Vitórias em Casa": df.apply(lambda x: 1 if x["Vitória"] and x["Localidade"] == "Home" else 0, axis=1).sum(),
        "Vitórias Fora": df.apply(lambda x: 1 if x["Vitória"] and x["Localidade"] == "Road" else 0, axis=1).sum(),
        "Derrotas em Casa": df.apply(lambda x: 1 if x["Derrota"] and x["Localidade"] == "Home" else 0, axis=1).sum(),
        "Derrotas Fora": df.apply(lambda x: 1 if x["Derrota"] and x["Localidade"] == "Road" else 0, axis=1).sum()
    }

    data = pd.DataFrame({
        "Resultado": list(resultados.keys()),
        "Quantidade": list(resultados.values())
    })

    chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Quantidade", type="quantitative"),
        color=alt.Color("Resultado:N", scale=alt.Scale(
            domain=["Vitórias em Casa", "Vitórias Fora", "Derrotas em Casa", "Derrotas Fora"],
            range=["green", "blue", "red", "brown"]
        )),
        tooltip=["Resultado", "Quantidade"]
    ).properties(
        width=800,
        height=400,
        title="Distribuição Percentual de Vitórias e Derrotas"
    )

    st.altair_chart(chart, use_container_width=False)

def plot_radar_chart(df):
    df[['Pontos Marcados', 'Pontos Sofridos']] = df['Placar'].str.split(' : ', expand=True)
    df['Pontos Marcados'] = df['Pontos Marcados'].astype(int)
    df['Pontos Sofridos'] = df['Pontos Sofridos'].astype(int)

    medias = {
        "Pontos Marcados em Casa": df[df["Localidade"] == "Home"]["Pontos Marcados"].mean(),
        "Pontos Marcados Fora": df[df["Localidade"] == "Road"]["Pontos Marcados"].mean(),
        "Pontos Sofridos em Casa": df[df["Localidade"] == "Home"]["Pontos Sofridos"].mean(),
        "Pontos Sofridos Fora": df[df["Localidade"] == "Road"]["Pontos Sofridos"].mean()
    }

    categories = list(medias.keys())
    values = list(medias.values())

    values += values[:1]
    categories += categories[:1]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                line=dict(color='royalblue'),
                name="Média de Pontos"
            )
        ]
    )

    fig.update_layout(
        title="Média de Pontos Marcados e Sofridos (Casa x Fora)",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2],  #ajuste do eixo radial
                tickfont=dict(color='black')
            )
        ),
        showlegend=False,
        height=600,
        width=800
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_line_chart(df):
    df["Data do Jogo"] = pd.to_datetime(df["Data do Jogo"], format="%d/%m/%Y")

    df["Vitória"] = df["Vitória"].apply(lambda x: 1 if x else 0)
    df["Derrota"] = df["Derrota"].apply(lambda x: 1 if x else 0)

    df['Vitórias Acumuladas'] = df['Vitória'].cumsum()
    df['Derrotas Acumuladas'] = df['Derrota'].cumsum()

    df_melted = df.melt(id_vars=["Data do Jogo"], value_vars=["Vitórias Acumuladas", "Derrotas Acumuladas"],
                        var_name="Resultado", value_name="Quantidade")

    chart = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X("Data do Jogo:T", title="Data"),
        y=alt.Y("Quantidade:Q", title="Contagem"),
        color=alt.Color("Resultado:N", scale=alt.Scale(
            domain=["Vitórias Acumuladas", "Derrotas Acumuladas"],
            range=["green", "red"]
        )),
        tooltip=["Data do Jogo", "Resultado", "Quantidade"]
    ).properties(
        title="Sequência de Vitórias e Derrotas ao Longo da Temporada",
        width=1000,
        height=600
    )

    st.altair_chart(chart, use_container_width=False)

def plot_scatter_all_teams(temporada):
    team_stats = []

    for team in teams.get_teams():
        team_id = team['id']
        team
        team_name = team['full_name']

        df = lista_jogos.get_team_data(team_id, temporada)[0]

        if df.empty:
            continue

        df[['Pontos Marcados', 'Pontos Sofridos']] = df['Placar'].str.split(' : ', expand=True)
        df['Pontos Marcados'] = pd.to_numeric(df['Pontos Marcados'], errors='coerce')
        df['Pontos Sofridos'] = pd.to_numeric(df['Pontos Sofridos'], errors='coerce')

        df = df.dropna(subset=['Pontos Marcados', 'Pontos Sofridos'])

        media_pontos_marcados = df['Pontos Marcados'].mean()
        media_pontos_sofridos = df['Pontos Sofridos'].mean()

        team_stats.append({
            'Time': team_name,
            'Média Pontos Marcados': media_pontos_marcados,
            'Média Pontos Sofridos': media_pontos_sofridos
        })

    final_df = pd.DataFrame(team_stats)

    fig = px.scatter(
        final_df,
        x='Média Pontos Marcados',
        y='Média Pontos Sofridos',
        text='Time',
        title='Média de Pontos Marcados e Sofridos por Time',
        labels={'Média Pontos Marcados': 'Pontos Marcados', 'Média Pontos Sofridos': 'Pontos Sofridos'},
        template='plotly_white',
        height=600,
        width=800
    )

    fig.update_traces(textposition='top center', marker=dict(size=12, color='royalblue'))
    fig.show()

def plot_radar_chart_defesa(df):
    columns_to_use = ['Roubos de Bola', 'Rebotes Defe', 'Bloqueios', 'Turnovers', 'Faltas']

    averages = df[columns_to_use].mean().values

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=averages,
        theta=columns_to_use,
        fill='toself',
        name='Médias por Métrica',
        marker=dict(color='royalblue')
    ))

    fig.update_layout(
        title="Gráfico Radar de Estatísticas Defensivas",
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, max(averages) * 1.2],
                tickfont=dict(color='black')
            )
        ),
        showlegend=False,
        height=600,  # altura
        width=800
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_data_chart(df):
    df['Data do Jogo'] = pd.to_datetime(df['Data do Jogo'], format='%d/%m/%Y')

    df[['Pontos', 'Pontos Adversário']] = df['Placar'].str.split(' : ', expand=True).astype(int)

    df['Cor Marcador'] = df['Vitória'].map({1: 'green', 0: 'red'})

    df['Símbolo Marcador'] = df['Localidade'].map({'Home': 'circle', 'Road': 'triangle-up'})

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Data do Jogo'],
        y=df['Pontos'],
        mode='lines+markers',
        name='Pontos do Time',
        marker=dict(
            color=df['Cor Marcador'],
            symbol=df['Símbolo Marcador'],
            size=12,
            line=dict(width=1)
        ),
        textposition="top center",
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Pontos do Time:</b> %{y}<br>" +
                      "<b>Casa/Fora:</b> %{customdata[0]}<br>" +
                      "<b>Oponente:</b> %{customdata[1]}<extra></extra>",
        customdata=df[['Localidade', 'Oponente']]
    ))

    fig.add_trace(go.Scatter(
        x=df['Data do Jogo'],
        y=df['Pontos Adversário'],
        mode='lines+markers',
        name='Pontos do Adversário',
        marker=dict(
            color='red',
            size=8,
            symbol='x'
        ),
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Pontos Adversário:</b> %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="Desempenho do Time ao Longo dos Jogos (Casa/Fora)",
        xaxis=dict(
            title="Data do Jogo",
            rangeslider=dict(visible=True),  #scroll
            type="date"
        ),
        yaxis_title="Pontos",
        template="plotly_white",
        legend_title="Legenda",
        hovermode="x unified",
        width=800, 
        height=600
    )

    st.plotly_chart(fig, use_container_width=False)

st.title("Equipes NBA")
st.subheader("Visualização das estatísticas do time")

tab1, tab2 = st.tabs(["Season 2023-24", "Season 2024-25"])

with tab1:
    df_23_24, summary_23_24, total_23_24, mean_23_24 = lista_jogos.get_team_data(1610612739, "2023-24")
    st.subheader("Gráficos da Temporada 2023-24")
    plot_bars(df_23_24)
    plot_grouped_bars(df_23_24)
    plot_histogram(df_23_24)
    plot_pie_chart(df_23_24)
    plot_radar_chart(df_23_24)
    plot_line_chart(df_23_24)
    # plot_scatter_all_teams("2023-24")
    plot_radar_chart_defesa(total_23_24)
    plot_data_chart(df_23_24)

with tab2:
    df_24_25, summary_24_25, total_24_25, mean_24_25 = lista_jogos.get_team_data(1610612739, "2024-25")
    st.subheader(" Gráficos da Temporada 2024-25")
    plot_bars(df_24_25)
    plot_grouped_bars(df_24_25)
    plot_histogram(df_24_25)
    plot_pie_chart(df_24_25)
    plot_radar_chart(df_24_25)
    plot_line_chart(df_24_25)
    # plot_scatter_all_teams("2024-25")
    plot_radar_chart_defesa(total_24_25)
    plot_data_chart(df_24_25)


# df_23_24 = pd.DataFrame({
#     "Localidade": ["Home", "Road", "Home", "Road", "Home", "Road"],
#     "Placar": ["120 : 11", "100 : 100", "110 : 9", "115 : 110", "130 : 10", "95 : 120"]
# })

# plot_radar_chart(df_23_24)    