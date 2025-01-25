import pandas as pd
import requests
import streamlit as st
from nba_api.stats.static import teams

st.title("Equipes NBA")
st.subheader("Lista de todos os times da liga")

nba_df = pd.DataFrame(teams.get_teams())

url = 'https://www.basketball-reference.com/leagues/NBA_2025.html'
response = requests.get(url)
tables = pd.read_html(response.text)

def clean_team_name(name):
    return name.replace('\xa0', ' ').split(' (')[0]

def extract_standing(name):
    try:
        return int(name.replace('\xa0', ' ').split(' (')[1].replace(')', ''))
    except (IndexError, ValueError):
        return 'Não há'

eastern_conference = tables[0]
eastern_conference['Conference'] = 'Eastern'
eastern_conference['Team'] = eastern_conference['Eastern Conference'].apply(clean_team_name)
eastern_conference['Standing'] = eastern_conference['Eastern Conference'].apply(extract_standing)

western_conference = tables[1]
western_conference['Conference'] = 'Western'
western_conference['Team'] = western_conference['Western Conference'].apply(clean_team_name)
western_conference['Standing'] = western_conference['Western Conference'].apply(extract_standing)

conference_df = pd.concat([
    eastern_conference[['Team', 'Conference', 'Standing']],
    western_conference[['Team', 'Conference', 'Standing']]
])

nba_df = nba_df.rename(columns={"full_name": "Team"})
merged_df = pd.merge(nba_df, conference_df, on="Team", how="inner")

eastern_teams = merged_df[merged_df['Conference'] == 'Eastern'].reset_index(drop=True)
western_teams = merged_df[merged_df['Conference'] == 'Western'].reset_index(drop=True)

eastern_teams['id'] = eastern_teams['id'].astype(str)
eastern_teams['year_founded'] = eastern_teams['year_founded'].astype(str)

western_teams['id'] = western_teams['id'].astype(str)
western_teams['year_founded'] = western_teams['year_founded'].astype(str)

cols_order = ['id', 'Team', 'Standing', 'abbreviation', 'nickname', 'city', 'state', 'year_founded']
eastern_teams = eastern_teams[cols_order]
western_teams = western_teams[cols_order]

colunas_ptbr = {
    'id': 'ID',
    'Team': 'Time',
    'Standing': 'Classificação',
    'abbreviation': 'Abreviação',
    'nickname': 'Apelido',
    'city': 'Cidade',
    'state': 'Estado',
    'year_founded': 'Ano de Fundação'
}

eastern_teams.rename(columns=colunas_ptbr, inplace=True)
western_teams.rename(columns=colunas_ptbr, inplace=True)

tab1, tab2 = st.tabs(["Eastern Conference", "Western Conference"])

with tab1:
    st.header("Eastern Conference")
    st.dataframe(eastern_teams)
with tab2:
    st.header("Western Conference")
    st.dataframe(western_teams)
