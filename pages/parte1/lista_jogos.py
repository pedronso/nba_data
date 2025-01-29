import pandas as pd
import streamlit as st
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.static import teams

def get_opponent_name(opp, team_mapping):
    opponent = opp.replace("@", "vs.").split(" vs. ")[1]
    return team_mapping.get(opponent, opponent)

def get_team_data(team_id, season):
    games_home = teamgamelogs.TeamGameLogs(
        team_id_nullable=team_id, 
        season_nullable=season, 
        location_nullable="Home"
    )
    df_home = games_home.get_data_frames()[0]
    df_home["Local"] = "Home"

    games_road = teamgamelogs.TeamGameLogs(
        team_id_nullable=team_id, 
        season_nullable=season, 
        location_nullable="Road"
    )
    df_road = games_road.get_data_frames()[0]
    df_road["Local"] = "Road"

    df = pd.concat([df_home, df_road], ignore_index=True)

    df["Victory"] = df["WL"] == "W"
    df["Defeat"] = df["WL"] == "L"

    df["Score"] = df['PTS'].astype(str) + ' : ' + (df['PTS']-df['PLUS_MINUS']).astype(int).astype(str)

    home_victories = df[(df["Local"] == "Home") & (df["Victory"])]
    road_victories = df[(df["Local"] == "Road") & (df["Victory"])]
    home_defeats = df[(df["Local"] == "Home") & (df["Defeat"])]
    road_defeats = df[(df["Local"] == "Road") & (df["Defeat"])]

    colunas = list(df.columns)
    colunas_desejadas = list(df.columns)[colunas.index("MIN"):colunas.index("PTS") + 1]
    nova_ordem = ["GAME_ID", "GAME_DATE", "Local", "MATCHUP", "Victory", "Defeat", "Score"] + colunas_desejadas

    colunas_ptbr = {
        "GAME_ID": "ID do Jogo",
        "GAME_DATE": "Data do Jogo",
        "Local": "Localidade",
        "MATCHUP": "Oponente",
        "Victory": "Vitória",
        "Defeat": "Derrota",
        "Score": "Placar",
        "MIN": "Minutos",
        "FGM": "Arremessos Conv",
        "FGA": "Arremessos Tent",
        "FG_PCT": "Arremessos %",
        "FG3M": "Arremessos de 3 Conv",
        "FG3A": "Arremessos de 3 Tent",
        "FG3_PCT": "Arremessos de 3 %",
        "FTM": "Lances Livres Conv",
        "FTA": "Lances Livres Tent",
        "FT_PCT": "Lances Livres %",
        "OREB": "Rebotes Ofen",
        "DREB": "Rebotes Defe",
        "REB": "Rebotes Totais",
        "AST": "Assistências",
        "TOV": "Turnovers",
        "STL": "Roubos de Bola",
        "BLK": "Bloqueios",
        "BLKA": "Bloqueios Sofr",
        "PF": "Faltas",
        "PFD": "Faltas Sofr",
        "PTS": "Pontos",
    }

    df = df[nova_ordem].rename(columns=colunas_ptbr)
    df['Data do Jogo'] = pd.to_datetime(df['Data do Jogo']).dt.strftime('%d/%m/%Y')
    team_mapping = {team['abbreviation']: team['full_name'] for team in teams.get_teams()}
    df['Oponente'] = df['Oponente'].apply(get_opponent_name, args=(team_mapping,))

    summary = {
        "Total de Vitórias": df["Vitória"].sum(),
        "Total de Vitórias em Casa": home_victories.shape[0],
        "Total de Vitórias fora de Casa": road_victories.shape[0],
        "Total de Derrotas": df["Derrota"].sum(),
        "Total de Derrotas em Casa": home_defeats.shape[0],
        "Total de Derrotas fora de Casa": road_defeats.shape[0],
    }

    summary_df = pd.DataFrame([summary])

    cols_to_sum = [
        'Arremessos Conv', 'Arremessos Tent', 'Arremessos de 3 Conv', 'Arremessos de 3 Tent', 'Lances Livres Conv',
        'Lances Livres Tent', 'Rebotes Ofen', 'Rebotes Defe', 'Rebotes Totais', 'Assistências','Turnovers', 
        'Roubos de Bola', 'Bloqueios', 'Bloqueios Sofr', 'Faltas', 'Faltas Sofr', 'Pontos',
    ]

    cols_avg = ['Arremessos %', 'Arremessos de 3 %', 'Lances Livres %']

    df_totals = df[cols_to_sum].sum().to_frame().T
    df_mean = df[cols_avg].mean().to_frame().T

    return df, summary_df, df_totals, df_mean

st.title("Equipes NBA")
st.subheader("Lista de todos os jogos do time")

tab1, tab2 = st.tabs(["Season 2023-24", "Season 2024-25"])

with tab1:
    st.header("Season 2023-24")
    df_23_24, summary_23_24, total_23_24, mean_23_24 = get_team_data(1610612739, "2023-24")
    with st.expander("Resumo da Temporada 2023-24", icon="🔎"):
        st.write("Totais")
        st.dataframe(summary_23_24, hide_index=True)
        st.dataframe(total_23_24, hide_index=True)
        st.write("Médias")
        st.dataframe(mean_23_24, hide_index=True)
    st.subheader("Lista dos jogos")
    st.dataframe(df_23_24)

with tab2:
    st.header("Season 2024-25")
    df_24_25, summary_24_25, total_24_25, mean_24_25 = get_team_data(1610612739, "2024-25")
    with st.expander(" Resumo da Temporada 2024-25", icon="🔎"):
        st.write("Totais")
        st.dataframe(summary_24_25, hide_index=True)
        st.dataframe(total_24_25, hide_index=True)
        st.write("Médias")
        st.dataframe(mean_24_25, hide_index=True)
    st.subheader("Lista dos jogos")
    st.dataframe(df_24_25)

# # Nikola Jokić
# career = playercareerstats.PlayerCareerStats(player_id='203999') 

# # pandas data frames (optional: pip install pandas)
# career.get_data_frames()[0]

# # json
# career.get_json()

# # dictionary
# career.get_dict()

# # ID do time (exemplo: Los Angeles Lakers)
# team_id = 1610612747  

# # Temporada (exemplo: 2023-24)
# season = '2023-24'

# # Obter o log de jogos
# game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)

# # Transformar os dados em DataFrame
# df = game_log.get_data_frames()[0]