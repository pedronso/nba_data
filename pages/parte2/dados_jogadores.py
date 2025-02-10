import pandas as pd
import streamlit as st
import requests
from pages.parte1 import lista_jogos
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import playercareerstats

def get_players(team_id):
    team_roster = commonteamroster.CommonTeamRoster(team_id=team_id)
    players_data = team_roster.get_data_frames()[0]

    url = 'https://www.basketball-reference.com/contracts/CLE.html'
    response = requests.get(url)
    tables = pd.read_html(response.text)
    salaries = tables[0]
    salaries.columns = salaries.columns.get_level_values(1)

    salaries_short = salaries.loc[0:16, ['Player', '2024-25']]

    full_data = pd.merge(players_data, salaries_short, left_on='PLAYER', right_on ='Player', how='left')
    full_data['2024-25'] = full_data.apply(lambda row: 'Rookie' if row['EXP'] == 'R' and pd.isna(row['2024-25']) else row['2024-25'], axis=1)

    df = full_data.drop(columns=["TeamID", "SEASON", "LeagueID", "NICKNAME", "PLAYER_SLUG", "Player", "BIRTH_DATE"])

    translation_dict = {
        "PLAYER": "Jogador",
        "NUM": "Número",
        "POSITION": "Posição",
        "HEIGHT": "Altura",
        "WEIGHT": "Peso",
        "BIRTH_DATE": "Data de Nascimento",
        "AGE": "Idade",
        "EXP": "Experiência",
        "SCHOOL": "Universidade",
        "PLAYER_ID": "ID",
        "HOW_ACQUIRED": "Como foi Adquirido",
        "2024-25": "Salário 2024-25"
    }

    df = df.rename(columns=translation_dict)

    new_column_order = [
        'ID', 'Jogador', 'Número', 'Altura', 'Peso', 'Idade',
        'Experiência', 'Posição', 'Universidade', 'Salário 2024-25', 'Como foi Adquirido'
    ]

    df = df[new_column_order]

    return df

def get_player_games(player_id, season):
    gamelog = playergamelog.PlayerGameLog(player_id, season)
    df = gamelog.get_data_frames()[0]

    return df

def player_selectbox(df_p):
    players = ["Donovan Mitchell", "Jarrett Allen", "Darius Garland"]

    df_p["Jogador"] = df_p["Jogador"].apply(
        lambda x: x + " ⭐" if x in players else x
    )

    player = st.selectbox(
        "Selecione um jogador:",
        df_p["Jogador"],
    )

    jogador_id = df_p.loc[df_p["Jogador"] == player, "ID"].values
    if jogador_id.size > 0:
        return jogador_id[0]
    else:
        st.warning("Jogador não encontrado.")
        return None

def get_player_games_df(df_g, season):
    df_g["Victory"] = df_g["WL"] == "W"
    df_g["Defeat"] = df_g["WL"] == "L"

    df_j = lista_jogos.get_team_data(1610612739, season)[0]
    df_j = df_j[["ID do Jogo" , "Placar", "Localidade", "Oponente", "Data do Jogo"]]

    full_data = pd.merge(df_j, df_g, left_on='ID do Jogo', right_on ='Game_ID', how='right')    
    full_data = full_data.drop(columns=["SEASON_ID","Player_ID","Game_ID","GAME_DATE","MATCHUP","WL","PLUS_MINUS","VIDEO_AVAILABLE"])

    colunas_ptbr = {
        "Victory": "Vitória",
        "Defeat": "Derrota",
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
        "STL": "Roubos de Bola",
        "BLK": "Bloqueios",
        "TOV": "Turnovers",
        "BLKA": "Bloqueios Sofr",
        "PF": "Faltas",
        "PTS": "Pontos",
    }

    nova_ordem = ["ID do Jogo", "Data do Jogo", "Localidade", "Oponente", "Vitória", "Derrota", "Placar", "Minutos", "Arremessos Conv", "Arremessos Tent", "Arremessos %", "Arremessos de 3 Conv", "Arremessos de 3 Tent", "Arremessos de 3 %", "Lances Livres Conv", "Lances Livres Tent", "Lances Livres %", "Rebotes Ofen", "Rebotes Defe", "Rebotes Totais", "Assistências", "Turnovers", "Roubos de Bola", "Bloqueios", "Faltas", "Pontos"]

    full_data = full_data.rename(columns=colunas_ptbr)
    full_data = full_data[nova_ordem]

    return full_data

def player_stats(df_filtrado):
    df_mean = df_filtrado[["Pontos", "Rebotes Totais", "Assistências"]].mean()
    df_median = df_filtrado[["Pontos", "Rebotes Totais", "Assistências"]].median()
    df_mode = df_filtrado[["Pontos", "Rebotes Totais", "Assistências"]].mode()

    if not df_mode.empty:
        df_mode = df_mode.iloc[0]
    else:
        st.warning("Não foi possível calcular a moda. Não há valores repetidos nas colunas selecionadas.")
    
    frequencia_moda = df_filtrado[["Pontos", "Rebotes Totais", "Assistências"]].apply(lambda x: (x == df_mode[x.name]).sum())

    df_f_alinhado, df_median_alinhado = df_filtrado.align(df_median, axis=1, join='inner')
    abaixo_mediana = (df_f_alinhado < df_median_alinhado).mean() * 100

    df_f_alinhado, df_mode_alinhado = df_filtrado.align(df_mode, axis=1, join='inner')
    abaixo_moda = (df_f_alinhado < df_mode_alinhado).mean() * 100

    df_std = df_filtrado[["Pontos", "Rebotes Totais", "Assistências"]].std()

    resultados = pd.DataFrame({
        "Média": df_mean,
        "Mediana": df_median,
        "Moda": df_mode,
        "Freq Moda": frequencia_moda,
        "Desvio Padrão": df_std,
        "% Abaixo da Média": (df_filtrado[["Pontos", "Rebotes Totais", "Assistências"]] < df_mean).mean() * 100,
        "% Abaixo da Mediana": abaixo_mediana,
        "% Abaixo da Moda": abaixo_moda
    })

    return resultados

def player_career_stats(player_id, full_data):
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_data = career_stats.get_data_frames()[0]

    total_games_career = career_data['GP'].sum()
    total_points_career = career_data['PTS'].sum()
    total_assists_career = career_data['AST'].sum()
    total_rebounds_career = career_data['REB'].sum()

    avg_points_career = total_points_career / total_games_career if total_games_career > 0 else 0
    avg_assists_career = total_assists_career / total_games_career if total_games_career > 0 else 0
    avg_rebounds_career = total_rebounds_career / total_games_career if total_games_career > 0 else 0
    total_minutes_career = career_data['MIN'].sum()

    total_games_season = full_data.shape[0]
    total_points_season = full_data['Pontos'].sum()
    total_assists_season = full_data['Assistências'].sum()
    total_rebounds_season = full_data['Rebotes Totais'].sum()

    avg_points_season = full_data['Pontos'].mean()
    avg_assists_season = full_data['Assistências'].mean()
    avg_rebounds_season = full_data['Rebotes Totais'].mean()
    total_minutes_season = full_data['Minutos'].sum()

    comparative_stats = pd.DataFrame({
        'Estatística': ['Total de Jogos', 'Total de Pontos', 'Média de Pontos', 'Total de Assistências', 'Média de Assistências', 'Total de Rebotes','Média de Rebotes', 'Minutos em Quadra'],
        'Carreira': [total_games_career, total_points_career, avg_points_career, total_assists_career, avg_assists_career, total_rebounds_career, avg_rebounds_career, total_minutes_career],
        'Temporada Atual': [total_games_season, total_points_season, avg_points_season, total_assists_season, avg_assists_season, total_rebounds_season, avg_rebounds_season, total_minutes_season]
    }).set_index('Estatística')

    comparative_stats_transposed = comparative_stats.T

    return comparative_stats_transposed

st.title("Jogadores NBA")
st.subheader("Dados dos jogadores do time")

tab1, tab2 = st.tabs(["Lista de Jogadores", "Partidas dos Jogadores"])

with tab1:
    st.header("Escalação do Cleveland Cavaliers")
    df_p = get_players(1610612739)
    st.dataframe(df_p, hide_index=True)

with tab2:
    st.header("Partidas dos Jogadores")
    player_id = player_selectbox(df_p)
    df_g = get_player_games(player_id, "2024-25")
    with st.expander("Filtros", icon="🔎"):
        full_data = get_player_games_df(df_g, "2024-25")

        localidade_opcoes = full_data["Localidade"].unique()
        localidade_selecionada = st.multiselect("Filtrar por Localidade", localidade_opcoes, default=localidade_opcoes)

        oponente_opcoes = full_data["Oponente"].unique()
        oponente_selecionado = st.multiselect("Filtrar por Oponente", oponente_opcoes, default=oponente_opcoes)

        opcoes_resultado = ["Ambos", "Vitória", "Derrota"]
        resultado_selecionado = st.selectbox("Filtrar por Resultado", opcoes_resultado)

        df_filtrado = full_data[(full_data["Localidade"].isin(localidade_selecionada)) & (full_data["Oponente"].isin(oponente_selecionado))]

        if resultado_selecionado == "Vitória":
            df_filtrado = df_filtrado[df_filtrado["Vitória"]]
        elif resultado_selecionado == "Derrota":
            df_filtrado = df_filtrado[df_filtrado["Derrota"]]

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        st.dataframe(df_filtrado, hide_index=True)
        num_jogos = df_filtrado.shape[0]
        st.write(f'{num_jogos} jogo{"s" if num_jogos != 1 else ""}')

        try:
            st.subheader("Métricas Estatísticas")
            st.write(player_stats(df_filtrado))

            st.subheader("Temporada Atual vs Carreira")
            st.write(player_career_stats(player_id, full_data))
        
        except Exception as e:
            st.error(f"Erro ao calcular as estatísticas: {e}")


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