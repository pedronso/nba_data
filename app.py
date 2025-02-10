import streamlit as st

st.set_page_config(page_title="Data manager", page_icon=":basketball:") 

pages = {
    "🎖️ Parte 1 - Equipes NBA": [    
        st.Page("./pages/parte1/lista_times.py", title="Times da Liga", icon=""),
        st.Page("./pages/parte1/lista_jogos.py", title="Jogos do Time", icon=""),
        st.Page("./pages/parte1/graficos_time.py", title="Gráficos do Time", icon=""),
    ],
    "🤾 Parte 2 - Jogadores NBA": [ 
        st.Page("./pages/parte2/dados_jogadores.py", title="Dados dos Jogadores", icon=""),
        st.Page("./pages/parte2/graficos_jogadores.py", title="Gráficos dos Jogadores", icon="")
    ],
    "🤖 Parte 3 - Estatísticas e Aprendizado de Máquina": [
        st.Page("./pages/parte3/modelos_estatisticos.py", title="Modelos Estatísticos", icon="")
    ]
}
pg = st.navigation(pages)
pg.run()