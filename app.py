import streamlit as st

st.set_page_config(page_title="Data manager", page_icon=":basketball:") 

pages = {
    "🎖️ Parte 1 - Equipes NBA": [    
        st.Page("./pages/parte1/lista_times.py", title="Lista dos Times da Liga", icon="")
    ],
    "🤾 Parte 2 - Jogadores NBA": [ 
        st.Page("./pages/parte2/parte2.py", title="Parte 2", icon="")
    ],
    "🤖 Parte 3 - Estatísticas e Aprendizado de Máquina": [
        st.Page("./pages/parte3/parte3.py", title="Parte 3", icon="")
    ]
}
pg = st.navigation(pages)
pg.run()