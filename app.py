import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

# Adiciona o diretório 'src' ao PATH do Python para importar módulos
# Note: A importação do 'EnergyModel' foi removida daqui
sys.path.insert(0, './src')

from src.data_loader import load_data
from src.analytics import (
    calculate_kpis,
    plot_consumption_trend,
    plot_temperature_consumption_scatter,
    detect_anomalies,
    plot_consumption_with_anomalies,
    plot_seasonal_comparison_by_year,
    plot_time_series_decomposition
)

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Análise de Energia Cidades Globais", page_icon="💡")

# --- Função para Carregar Dados com Cache ---
@st.cache_data(ttl=3600)
def get_data():
    return load_data()

# --- Função para Treinar Modelo com Cache ---
# Esta é a seção que foi modificada
@st.cache_resource
def get_model(df, city_name):
    # Move a importação para dentro da função para evitar o erro de inicialização
    # Agora a biblioteca 'sklearn' será importada somente quando esta função for executada
    from src.models import EnergyModel

    model = EnergyModel()
    df_city = df[df['Cidade'] == city_name]
    error = model.train(df_city)
    return model, error

# --- Título e Resumo Executivo ---
st.title("💡 Análise de Padrões de Consumo de Energia em Cidades Globais")
st.markdown("---")
st.markdown("""
    **Aviso sobre os Dados de Consumo:**
    - **São Paulo:** Dados de consumo são **reais**, obtidos da Agência Nacional de Energia Elétrica (ANEEL).
    - **Berlim e Nova York:** Dados de consumo são **simulados**.
""")
st.markdown("---")

# Carregar dados
df_energia = get_data()

if df_energia.empty:
    st.error("Não foi possível carregar os dados. Certifique-se de que o pipeline de dados foi executado (`./run.sh`) e que o arquivo do banco de dados (`data/processed/energia_cidades.db`) existe.")
    st.stop()

# Obter lista de cidades
all_cities = df_energia['Cidade'].unique().tolist()
selected_cities_default = all_cities

# --- Sidebar para Seleções ---
st.sidebar.header("Configurações da Análise")
st.sidebar.write("Selecione as cidades e configure os filtros para explorar os dados.")

### NOVO: Barra de Pesquisa ###
search_query = st.sidebar.text_input("Pesquisar cidade (ex: 'São Paulo')", "")
search_query = search_query.strip().title()

# Lógica para determinar quais cidades exibir
if search_query:
    if search_query in all_cities:
        st.success(f"Cidade '{search_query}' encontrada!")
        selected_cities = [search_query]
        city_for_detailed_analysis = search_query
    else:
        st.error(f"Cidade '{search_query}' não encontrada.")
        st.info(f"Cidades válidas são: {', '.join(all_cities)}")
        st.stop() # Interrompe a execução do dashboard para evitar erros
else:
    # Se a barra de pesquisa estiver vazia, use os seletores padrão
    selected_cities = st.sidebar.multiselect(
        "Selecione as Cidades para Comparação:",
        options=all_cities,
        default=selected_cities_default
    )
    city_for_detailed_analysis = st.sidebar.selectbox(
        "Selecione uma Cidade para Análise Detalhada:",
        options=all_cities
    )

# Filtro de Ano
min_year = int(df_energia['Ano'].min()) if not df_energia.empty else 2023
max_year = int(df_energia['Ano'].max()) if not df_energia.empty else 2023
if min_year == max_year:
    st.sidebar.write(f"Dados disponíveis para o ano: **{min_year}**")
else:
    selected_year = st.sidebar.slider(
        "Selecione o Ano:",
        min_value=min_year,
        max_value=max_year,
        value=max_year
    )
    df_energia = df_energia[df_energia['Ano'] == selected_year]

# Filtro de Temperatura (slider)
temp_min = df_energia['Temperatura_C'].min() if not df_energia.empty else 0
temp_max = df_energia['Temperatura_C'].max() if not df_energia.empty else 30
temp_range_selected = st.sidebar.slider(
    "Filtrar por Faixa de Temperatura (°C):",
    min_value=float(temp_min),
    max_value=float(temp_max),
    value=(float(temp_min), float(temp_max))
)

# --- Seção de KPIs (Key Performance Indicators) ---
st.header("📊 Indicadores Chave de Performance (KPIs)")
if selected_cities:
    kpi_cols = st.columns(len(selected_cities))
    for i, city in enumerate(selected_cities):
        kpis = calculate_kpis(df_energia, city)
        with kpi_cols[i]:
            st.metric(label=f"Consumo Total Anual ({city})", value=f"{kpis['Consumo_Total_Anual']:.2f} MWh")
            st.metric(label=f"Consumo Per Capita ({city})", value=f"{kpis['Consumo_Per_Capita_Anual']:.2f} kWh/pessoa")
            st.metric(label=f"Mês de Pico ({city})", value=f"{kpis['Mes_Pico']} ({kpis['Consumo_Pico']:.2f} MWh)")
            st.metric(label=f"Mês de Vale ({city})", value=f"{kpis['Mes_Vale']} ({kpis['Consumo_Vale']:.2f} MWh)")
            st.metric(label=f"Temp. Média Anual ({city})", value=f"{kpis['Temperatura_Media_Anual']:.1f} °C")
else:
    st.info("Por favor, selecione pelo menos uma cidade para ver os KPIs.")

st.markdown("---")

# --- Seção de Tendência de Consumo Mensal (Comparativo) ---
st.header("📈 Tendência de Consumo Mensal")
st.markdown("Este gráfico mostra o consumo de energia ao longo do ano para as cidades selecionadas, permitindo uma comparação direta das tendências.")
if selected_cities:
    fig_trend = plot_consumption_trend(df_energia, selected_cities)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Selecione cidades na barra lateral para ver a tendência de consumo.")

st.markdown("---")

# --- Seção de Análise de Correlação (Consumo vs. Temperatura) ---
st.header(f"🌡️ Consumo vs. Temperatura em {city_for_detailed_analysis}")
st.markdown(f"Explore como a temperatura afeta o consumo de energia em **{city_for_detailed_analysis}**. Os pontos são coloridos por mês para identificar padrões sazonais na correlação.")
fig_scatter = plot_temperature_consumption_scatter(df_energia, city_for_detailed_analysis, temp_range=temp_range_selected)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- Seção de Análise de Sazonalidade Avançada ---
st.header(f"🗓️ Análise Sazonal Avançada em {city_for_detailed_analysis}")
st.markdown("Com dados de múltiplos anos, esta seção mostraria a evolução do padrão sazonal e a decomposição da série temporal para identificar tendência, sazonalidade e resíduos.")
fig_seasonal_year, msg_seasonal_year = plot_seasonal_comparison_by_year(df_energia, city_for_detailed_analysis)
if fig_seasonal_year:
    st.markdown("### Comparação Sazonal Mensal por Ano")
    st.plotly_chart(fig_seasonal_year, use_container_width=True)
else:
    st.info(f"Não foi possível gerar 'Comparação Sazonal Mensal por Ano' para {city_for_detailed_analysis}: {msg_seasonal_year}")

fig_decompose, msg_decompose = plot_time_series_decomposition(df_energia, city_for_detailed_analysis)
if fig_decompose:
    st.markdown("### Decomposição da Série Temporal (Tendência, Sazonalidade, Resíduos)")
    st.plotly_chart(fig_decompose, use_container_width=True)
else:
    st.info(f"Não foi possível gerar 'Decomposição da Série Temporal' para {city_for_detailed_analysis}: {msg_decompose}")

st.markdown("---")

# --- Seção de Detecção de Anomalias ---
st.header(f"🚨 Detecção de Anomalias em {city_for_detailed_analysis}")
st.markdown(f"Identificação de meses com consumo de energia atipicamente alto ou baixo em **{city_for_detailed_analysis}** (baseado em Z-score de 1.5 desvios padrão).")

df_with_anomalies, anomalies_df = detect_anomalies(df_energia, city_for_detailed_analysis)

if not df_with_anomalies.empty:
    fig_anomalies = plot_consumption_with_anomalies(df_with_anomalies, city_for_detailed_analysis, anomalies_df)
    st.plotly_chart(fig_anomalies, use_container_width=True)

    if not anomalies_df.empty:
        st.subheader("Tabela de Anomalias Detectadas")
        st.dataframe(anomalies_df.drop(columns=['Z_Score']).set_index('Data'))
        st.markdown("*(Z-Score é uma medida de quantos desvios padrão um ponto está da média. Valores absolutos altos indicam anomalias.)*")
    else:
        st.info("Nenhuma anomalia significativa detectada para esta cidade e período com o limite de 1.5 desvios padrão.")
else:
    st.warning("Dados insuficientes para detecção de anomalias.")

st.markdown("---")

# --- Seção de Modelagem Preditiva ---
st.header(f"🧠 Modelo Preditivo de Consumo para {city_for_detailed_analysis}")
st.markdown(f"Um modelo de regressão linear para estimar o consumo de energia em **{city_for_detailed_analysis}** com base na temperatura.")

model, train_error = get_model(df_energia, city_for_detailed_analysis)

if train_error:
    st.error(f"Erro ao treinar o modelo para {city_for_detailed_analysis}: {train_error}")
else:
    model_summary = model.get_summary()

    st.markdown(f"**Qualidade do Modelo (R-quadrado):** `{model_summary['r2']:.2f}`")
    st.markdown(f"**Erro Absoluto Médio (MAE):** `{model_summary['mae']:.2f} MWh` (Em média, o modelo erra em {model_summary['mae']:.2f} MWh por mês)")
    st.markdown(f"**Raiz do Erro Quadrático Médio (RMSE):** `{model_summary['rmse']:.2f} MWh`")
    
    st.markdown("---")
    st.markdown("### Interpretação dos Coeficientes")
    st.write(model_summary['interpretacao'])
    
    st.markdown("---")
    st.markdown("### Previsão Interativa")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Temperatura Mínima Observada: {temp_min:.1f}°C")
        st.write(f"Temperatura Máxima Observada: {temp_max:.1f}°C")
        
        temp_to_predict = st.slider(
            "Selecione uma Temperatura para Prever o Consumo (°C):",
            min_value=float(temp_min),
            max_value=float(temp_max),
            value=float(df_energia[df_energia['Cidade'] == city_for_detailed_analysis]['Temperatura_C'].mean()),
            step=0.1
        )
    
    with col2:
        if model.is_trained:
            predicted_consumption = model.predict(temp_to_predict)
            st.metric(label=f"Consumo Previsto para {temp_to_predict:.1f}°C", value=f"{predicted_consumption:.2f} MWh")
        else:
            st.warning("Modelo não treinado para realizar previsões.")

st.markdown("---")
st.markdown("Desenvolvido com ❤️ e Python.")