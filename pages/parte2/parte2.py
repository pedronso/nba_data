import pandas as pd
import streamlit as st
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import teamgamelog


st.title("Página 2")
st.write("Conteúdo da Página 2")

# Nikola Jokić
career = playercareerstats.PlayerCareerStats(player_id='203999') 

# pandas data frames (optional: pip install pandas)
career.get_data_frames()[0]

# json
career.get_json()

# dictionary
career.get_dict()

# ID do time (exemplo: Los Angeles Lakers)
team_id = 1610612747  

# Temporada (exemplo: 2023-24)
season = '2023-24'

# Obter o log de jogos
game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)

# Transformar os dados em DataFrame
df = game_log.get_data_frames()[0]