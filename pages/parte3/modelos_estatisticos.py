import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from scipy.stats import genextreme
from pages.parte2 import dados_jogadores
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, confusion_matrix, roc_curve, auc, classification_report, roc_auc_score
from pygam import PoissonGAM, LinearGAM, s
from scipy.stats import poisson

st.title("Modelos Estatísticos")
st.subheader("Análise e predição de dados dos jogadores")

def get_player_data():
    players = pd.DataFrame([[1629636, "Darius Garland"],
    [1628386, "Jarrett Allen"],
    [1628378, "Donovan Mitchell"]], columns=["ID", "Jogador"])
    player_id = dados_jogadores.player_selectbox(players)

    df_23_24 = dados_jogadores.get_player_games(player_id, "2023-24")
    df_23_24_full = dados_jogadores.get_player_games_df(df_23_24, "2023-24")

    df_24_25 = dados_jogadores.get_player_games(player_id, "2024-25")
    df_24_25_full = dados_jogadores.get_player_games_df(df_24_25, "2024-25")

    df_full = pd.concat([df_23_24_full, df_24_25_full], ignore_index=True)

    return df_full

def analisar_dados_gumbel(df, x):
    dados = df.dropna().values

    if x == None:
        return

    if len(dados) == 0:
        return {"Erro": "Não há dados suficientes para análise."}

    try:
        c, loc, scale = genextreme.fit(dados)

    except Exception as e:
        return {"Erro ao ajustar a distribuição": str(e)}

    prob_x = genextreme.pdf(x, c, loc, scale)
    prob_abaixo_ou_igual = genextreme.cdf(x, c, loc, scale)
    prob_abaixo = prob_abaixo_ou_igual - prob_x
    prob_acima = 1 - prob_abaixo_ou_igual
    prob_exceder_ou_igual = prob_acima + prob_x

    total_dados = len(dados)
    prop_igual = np.sum(dados == x) / total_dados
    prop_menor_igual = np.sum(dados <= x) / total_dados
    prop_menor = np.sum(dados < x) / total_dados
    prop_maior = np.sum(dados > x) / total_dados
    prop_maior_igual = np.sum(dados >= x) / total_dados

    valores_abaixo = dados[dados < x]
    valores_acima = dados[dados > x]

    resultados = {
        f"Probabilidade de ser exatamente {x}": prob_x,
        f"Probabilidade de ficar abaixo  de {x}": prob_abaixo,
        f"Probabilidade de ficar abaixo ou igual a {x}": prob_abaixo_ou_igual,
        f"Probabilidade de exceder {x}": prob_acima,
        f"Probabilidade de exceder ou igualar a {x}": prob_exceder_ou_igual,
        f"Proporção de valores iguais a {x}": prop_igual,
        f"Proporção de valores menores que {x}": prop_menor,
        f"Proporção de valores menores ou iguais a {x}": prop_menor_igual,
        f"Proporção de valores maiores que {x}": prop_maior,
        f"Proporção de valores maiores ou iguais a {x}": prop_maior_igual,
        f"Valores menores que {x}": valores_abaixo.tolist(),
        f"Valores maiores que {x}": valores_acima.tolist()
    }

    return resultados, (c, loc, scale)

def plot_gumbel_distribution(dados, x, c, loc, scale):
    x_vals = np.linspace(min(dados), max(dados), 1000)
    pdf_vals = genextreme.pdf(x_vals, c, loc, scale)
    cdf_vals = genextreme.cdf(x_vals, c, loc, scale)

    plot_data = pd.DataFrame({
        "Valores": x_vals,
        "PDF": pdf_vals,
        "CDF": cdf_vals
    })

    hist_chart = alt.Chart(pd.DataFrame({"dados": dados})).mark_bar(opacity=0.4).encode(
        alt.X("dados:Q", bin=alt.Bin(maxbins=30), title="Valores"),
        alt.Y("count()", title="Frequência")
    )

    cdf_chart = alt.Chart(plot_data).mark_line(color="green").encode(
        x=alt.X("Valores", title="Valores"),
        y=alt.Y("CDF", title="Probabilidade Acumulada")
    ).properties(title="Função Distribuição Acumulada (CDF)")

    ref_line = alt.Chart(pd.DataFrame({"x": [x]})).mark_rule(color="orange").encode(
        x="x:Q"
    )

    qq_vals = np.linspace(min(dados), max(dados), len(dados))
    theoretical_quantiles = genextreme.ppf(np.linspace(0, 1, len(dados)), c, loc, scale)

    qq_plot = pd.DataFrame({"Dados": sorted(dados), "Teóricos": theoretical_quantiles})

    qq_chart = alt.Chart(qq_plot).mark_point().encode(
        x=alt.X("Teóricos", title="Quantis Teóricos"),
        y=alt.Y("Dados", title="Quantis Empíricos")
    ).properties(title="Gráfico Q-Q")

    thresholds = np.linspace(min(dados), max(dados), 100)
    exceed_probs = [np.sum(dados > t) / len(dados) for t in thresholds]

    exceed_plot = pd.DataFrame({"Threshold": thresholds, "Probabilidade": exceed_probs})

    exceed_chart = alt.Chart(exceed_plot).mark_line().encode(
        x=alt.X("Threshold", title="Limiar"),
        y=alt.Y("Probabilidade", title="Probabilidade de Excedência")
    ).properties(title="Gráfico de Excedência")


    st.altair_chart(exceed_chart, use_container_width=True)

    st.altair_chart(qq_chart, use_container_width=True)

    st.altair_chart(hist_chart + ref_line, use_container_width=True)
    st.altair_chart(cdf_chart + ref_line, use_container_width=True)

def modelo_regressao_linear_com_graficos(df, features, targets):
    X = df[features].dropna()
    Y = df[targets].loc[X.index]
    
    if X.empty or Y.empty:
        st.write("Dados insuficientes após remoção de valores ausentes.")
        return

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

    modelo = LinearRegression()
    modelo.fit(X_train, Y_train)

    previsoes = modelo.predict(X_test)
    resultados = pd.DataFrame(previsoes, columns=targets, index=X_test.index)

    resultados_comparacao = resultados.copy()
    for target in targets:
        resultados_comparacao[f"{target}_Real"] = Y_test[target]

    st.write("Previsões vs. Valores Reais:")
    st.dataframe(resultados_comparacao)

    metrics_data = []
    for target in targets:
        mae = mean_absolute_error(Y_test[target], resultados[target])
        mse = mean_squared_error(Y_test[target], resultados[target])
        rmse = np.sqrt(mse)
        r2 = r2_score(Y_test[target], resultados[target])

        metrics_data.append({
            "Target": target,
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "R²": r2
        })

    metrics_df = pd.DataFrame(metrics_data)

    st.write("Métricas para cada target:")
    st.dataframe(metrics_df)

    stats = df[targets].describe().transpose()
    stats["mediana"] = df[targets].median()
    stats["moda"] = df[targets].mode().iloc[0]
    
    st.write("Estatísticas Descritivas:")
    st.write(stats)

    probabilidades_data = []
    for target in targets:
        prob = {}
        for stat_name in stats.columns:
            valor_stat = stats.loc[target, stat_name]
            prob[f"Acima da {stat_name}"] = (resultados[target] > valor_stat).mean()
            prob[f"Abaixo da {stat_name}"] = (resultados[target] <= valor_stat).mean()
        
        probabilidades_data.append({
            "Target": target,
            "Acima da Média": prob.get("Acima da mean", 0),
            "Abaixo da Média": prob.get("Abaixo da mean", 0),
            "Acima da Mediana": prob.get("Acima da median", 0),
            "Abaixo da Mediana": prob.get("Abaixo da median", 0),
            "Acima da Moda": prob.get("Acima da moda", 0),
            "Abaixo da Moda": prob.get("Abaixo da moda", 0)
        })

    probabilidades_df = pd.DataFrame(probabilidades_data)

    st.write("Probabilidades de Previsão:")
    st.dataframe(probabilidades_df)

    plotar_graficos_regressao(modelo, X_test, Y_test, previsoes, targets)

def plotar_graficos_regressao(modelo, X_test, Y_test, previsoes, targets):
    plt.figure(figsize=(10, 6))
    coef = modelo.coef_
    for i, target in enumerate(targets):
        plt.subplot(1, len(targets), i+1)
        plt.barh(X_test.columns, coef[i])
        plt.title(f'Coeficientes de {target}')
        plt.xlabel('Valor do Coeficiente')
    plt.tight_layout()
    st.pyplot(plt)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.kdeplot(previsoes, label='Distribuição das Previsões', color='blue', shade=True)
    sns.kdeplot(Y_test.values.flatten(), label='Distribuição dos Valores Reais', color='red', shade=True)
    plt.title('Distribuição das Previsões vs Valores Reais')
    plt.xlabel('Valor')
    plt.ylabel('Densidade')
    plt.legend()
    st.pyplot(plt)
    plt.close()

    for target in targets:
        Y_pred = previsoes[:, targets.index(target)]
        Y_test_binary = (Y_test[target] > Y_test[target].mean()).astype(int)
        fpr, tpr, thresholds = roc_curve(Y_test_binary, Y_pred)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(10, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Falso Positivo')
        plt.ylabel('Verdadeiro Positivo')
        plt.title(f'Curva ROC para {target}')
        plt.legend(loc='lower right')
        st.pyplot(plt)
        plt.close()

    target = 'Pontos'
    Y_pred_binary = (previsoes[:, targets.index(target)] > Y_test[target].mean()).astype(int)
    cm = confusion_matrix(Y_test[target] > Y_test[target].mean(), Y_pred_binary)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Predito 0', 'Predito 1'], yticklabels=['Real 0', 'Real 1'])
    plt.title(f'Matriz de Confusão para {target}')
    plt.xlabel('Predição')
    plt.ylabel('Real')
    st.pyplot(plt)
    plt.close()

def regressao_logistica(df, target_value, features, target_column):
    X = df[features]
    y = (df[target_column] > target_value).astype(int)

    if len(y.unique()) < 2:
        st.write("Erro: Os dados precisam ter pelo menos duas classes distintas. Tente escolher outro valor de referência.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    modelo = LogisticRegression()
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    y_pred_proba = modelo.predict_proba(X_test)[:, 1]

    resultados_df = X_test.copy()
    resultados_df[target_column + "_real"] = y_test.values
    resultados_df[target_column + "_previsto"] = y_pred

    st.write("Resultados no conjunto de teste:")
    st.dataframe(resultados_df)
    
    st.write(f"Resultados para regressão logística prevendo {target_column} maior que {target_value}:")

    mostrar_classification_report(y_test, y_pred)

    st.write("Matriz de Confusão:")
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax)
    ax.set_xlabel('Previsto')
    ax.set_ylabel('Real')
    st.pyplot(fig)

    if len(np.unique(y_test)) > 1:
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)

        st.write(f"AUC (Área sob a Curva ROC): {roc_auc:.2f}")
        fig, ax = plt.subplots()
        ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')
        ax.set_xlabel('Falso Positivo (FPR)')
        ax.set_ylabel('Verdadeiro Positivo (TPR)')
        ax.legend(loc='lower right')
        st.pyplot(fig)

    st.write("Coeficientes do Modelo:")
    coef_df = pd.DataFrame({'Feature': features, 'Coeficiente': modelo.coef_[0]})
    fig, ax = plt.subplots()
    sns.barplot(data=coef_df, x='Coeficiente', y='Feature', palette='coolwarm', ax=ax)
    st.pyplot(fig)

def mostrar_classification_report(y_test, y_pred):
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    
    report_df = pd.DataFrame(report_dict).transpose()
    
    report_df = report_df[['precision', 'recall', 'f1-score', 'support']]
    
    st.table(report_df.style.format({'precision': '{:.2f}', 'recall': '{:.2f}', 'f1-score': '{:.2f}', 'support': '{:.0f}'}))

def prever_estatisticas(df, estatistica='Pontos_Casa', valor_desejado=None):
    df['Data do Jogo'] = pd.to_datetime(df['Data do Jogo'], format='%d/%m/%Y')

    df[['Pontos_Casa', 'Pontos_Visitante']] = df['Placar'].str.split(' : ', expand=True)
    df['Pontos_Casa'] = pd.to_numeric(df['Pontos_Casa'])
    df['Pontos_Visitante'] = pd.to_numeric(df['Pontos_Visitante'])

    y = df[estatistica]
    X = df[['Arremessos Conv', 'Arremessos Tent', 'Arremessos de 3 Conv', 'Arremessos de 3 Tent', 'Lances Livres Conv', 'Lances Livres Tent']]

    X_dense = X.to_numpy()

    poisson_gam = PoissonGAM(s(0) + s(1) + s(2) + s(3) + s(4) + s(5)).fit(X_dense, y)

    linear_gam = LinearGAM(s(0) + s(1) + s(2) + s(3) + s(4) + s(5)).fit(X_dense, y)

    y_pred_poisson = poisson_gam.predict(X_dense)
    y_pred_linear = linear_gam.predict(X_dense)

    media = y.mean()
    mediana = y.median()
    moda = y.mode()[0]
    maximo = y.max()
    minimo = y.min()

    def calcular_probabilidade(modelo, valor, tipo='acima'):
        probabilidade = modelo.predict(X_dense)
        if tipo == 'acima':
            return (probabilidade > valor).mean()
        else:
            return (probabilidade < valor).mean()

    prob_acima_media = calcular_probabilidade(poisson_gam, media, tipo='acima')
    prob_abaixo_media = calcular_probabilidade(poisson_gam, media, tipo='abaixo')

    prob_acima_mediana = calcular_probabilidade(poisson_gam, mediana, tipo='acima')
    prob_abaixo_mediana = calcular_probabilidade(poisson_gam, mediana, tipo='abaixo')

    prob_acima_moda = calcular_probabilidade(poisson_gam, moda, tipo='acima')
    prob_abaixo_moda = calcular_probabilidade(poisson_gam, moda, tipo='abaixo')

    prob_acima_maximo = calcular_probabilidade(poisson_gam, maximo, tipo='acima')
    prob_abaixo_maximo = calcular_probabilidade(poisson_gam, maximo, tipo='abaixo')

    prob_acima_minimo = calcular_probabilidade(poisson_gam, minimo, tipo='acima')
    prob_abaixo_minimo = calcular_probabilidade(poisson_gam, minimo, tipo='abaixo')

    prob_exata = None
    if valor_desejado is not None:
        if estatistica == 'Pontos_Casa' or estatistica == 'Rebotes Totais':
            prob_exata = (y_pred_poisson == valor_desejado).mean()
        else:
            prob_exata = (y_pred_linear == valor_desejado).mean()

    resultados = {
        'prob_acima_media': prob_acima_media,
        'prob_abaixo_media': prob_abaixo_media,
        'prob_acima_mediana': prob_acima_mediana,
        'prob_abaixo_mediana': prob_abaixo_mediana,
        'prob_acima_moda': prob_acima_moda,
        'prob_abaixo_moda': prob_abaixo_moda,
        'prob_acima_maximo': prob_acima_maximo,
        'prob_abaixo_maximo': prob_abaixo_maximo,
        'prob_acima_minimo': prob_acima_minimo,
        'prob_abaixo_minimo': prob_abaixo_minimo,
        'prob_exata': prob_exata
    }

    return resultados

data = get_player_data()

tab1, tab2, tab3, tab4 = st.tabs(["Método de Gumbel", "Regressão Linear", "Regressão Logística", "GAMLSS"])

with tab1:
    st.header("Método de Gumbel")

    if data is not None and not data.empty:
        colunas = list(data.columns)
        opcoes = colunas[colunas.index("Arremessos Conv"):colunas.index("Pontos") + 1]
        coluna = st.selectbox("Métrica avaliada", opcoes)

        x = st.number_input("Valor avaliado", min_value=0, value=0, step=1)

        if "%" in coluna:
            x /= 100

        resultados, params = analisar_dados_gumbel(data[coluna], x)

        if params:
            c, loc, scale = params
            st.write("Resultados:")
            for key, value in resultados.items():
                if isinstance(value, list):
                    st.write(f"{key}: {value}")
                else:
                    st.write(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")

            plot_gumbel_distribution(data[coluna].dropna().values, x, c, loc, scale)

    else:
        st.write("Nenhum dado disponível para análise.")

with tab2:
    st.header("Regressão Linear")

    if data is not None and not data.empty:
        features = ["Minutos", "Arremessos Tent", "Turnovers"]
        targets = ["Pontos", "Assistências", "Rebotes Totais"]

        modelo_regressao_linear_com_graficos(data, features, targets)

    else:
        st.write("Nenhum dado disponível para análise.")

with tab3:
    st.header("Regressão Logística")

    if data is not None and not data.empty:
        features = ["Minutos", "Arremessos Tent", "Turnovers"]
        coluna = st.selectbox("Métrica avaliada", ["Pontos", "Assistências", "Rebotes Totais"])
        x = 0

        if coluna == "Pontos":
            x = 15
        elif coluna == "Assistências":
            x = 5
        elif coluna == "Rebotes Totais":
            x = 2

        regressao_logistica(data, x, features, coluna)

    else:
        st.write("Nenhum dado disponível para análise.")

with tab4:
    st.header("Generalized Additive Models for Location Scale and Shape")

    if data is not None and not data.empty:
        data
        # aplicar_gamlss(data, feature=["Minutos","Arremessos Conv", "Arremessos de 3 Conv" ,"Lances Livres Conv", "Turnovers", "Roubos de Bola", "Bloqueios"], target='Pontos')
        resultados = prever_estatisticas(data, estatistica='Pontos_Casa', valor_desejado=30)
        for chave, valor in resultados.items():
            print(f"{chave}: {valor:.2f}")
    else:
        st.write("Nenhum dado disponível para análise.")
