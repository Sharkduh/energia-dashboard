# src/analytics.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import seasonal_decompose # Para decomposição STL

def calculate_kpis(df, city):
    """Calcula KPIs chave para uma cidade específica."""
    df_city = df[df['Cidade'] == city]
    
    if df_city.empty:
        return {
            "Consumo_Total_Anual": 0,
            "Consumo_Per_Capita_Anual": 0,
            "Mes_Pico": "N/A",
            "Consumo_Pico": 0,
            "Mes_Vale": "N/A",
            "Consumo_Vale": 0,
            "Temperatura_Media_Anual": 0
        }

    total_consumo = df_city['Consumo_MWh'].sum()
    avg_pop = df_city['Populacao_Milhoes'].mean()
    consumo_per_capita = (total_consumo / (avg_pop * 1_000_000)) * 1000 if avg_pop > 0 else 0 # kWh/pessoa

    # Sazonalidade (mês de pico/vale)
    monthly_summary = df_city.groupby(df_city['Data'].dt.month)['Consumo_MWh'].sum()
    mes_pico_num = monthly_summary.idxmax()
    consumo_pico = monthly_summary.max()
    mes_vale_num = monthly_summary.idxmin()
    consumo_vale = monthly_summary.min()

    meses_map = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    avg_temp = df_city['Temperatura_C'].mean()

    return {
        "Consumo_Total_Anual": total_consumo,
        "Consumo_Per_Capita_Anual": consumo_per_capita,
        "Mes_Pico": meses_map.get(mes_pico_num, "N/A"),
        "Consumo_Pico": consumo_pico,
        "Mes_Vale": meses_map.get(mes_vale_num, "N/A"),
        "Consumo_Vale": consumo_vale,
        "Temperatura_Media_Anual": avg_temp
    }

def plot_consumption_trend(df, selected_cities):
    """Cria um gráfico de linha interativo do consumo mensal para cidades selecionadas."""
    df_plot = df[df['Cidade'].isin(selected_cities)].copy()
    
    # Garantir que a data é tratada como datetime e usada como índice para Plotly
    df_plot = df_plot.sort_values(by='Data')

    fig = px.line(df_plot, x='Data', y='Consumo_MWh', color='Cidade',
                  title='Consumo Mensal de Energia',
                  labels={'Data': 'Data', 'Consumo_MWh': 'Consumo (MWh)'},
                  line_shape="linear") # ou "spline" para suavizar

    fig.update_layout(hovermode="x unified", legend_title_text="Cidade")
    fig.update_traces(mode='lines+markers') # Para mostrar os pontos mensais

    return fig

def plot_temperature_consumption_scatter(df, city, temp_range=None):
    """Cria um gráfico de dispersão interativo de Consumo vs. Temperatura."""
    df_city = df[df['Cidade'] == city].copy()

    if temp_range:
        df_city = df_city[(df_city['Temperatura_C'] >= temp_range[0]) & (df_city['Temperatura_C'] <= temp_range[1])]

    fig = px.scatter(df_city, x='Temperatura_C', y='Consumo_MWh',
                     color=df_city['Data'].dt.month.map({
                         1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                         7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'
                     }), # Colorir por mês/estação
                     title=f'Consumo de Energia vs. Temperatura em {city}',
                     labels={'Temperatura_C': 'Temperatura (°C)', 'Consumo_MWh': 'Consumo (MWh)', 'color': 'Mês'},
                     trendline="ols", # Adiciona uma linha de regressão OLS (Ordinary Least Squares)
                     hover_data={'Data': '|%Y-%m-%d', 'Consumo_MWh': ':.2f', 'Temperatura_C': ':.2f'})
    
    fig.update_layout(hovermode="closest")
    return fig

def detect_anomalies(df, city, threshold_std=1.5):
    """
    Detecta anomalias no consumo de uma cidade usando o método Z-score.
    Retorna o DataFrame original com uma coluna 'Is_Anomaly' e um DataFrame de anomalias.
    """
    df_city = df[df['Cidade'] == city].copy()

    if df_city.empty or len(df_city) < 2:
        return df_city.assign(Is_Anomaly=False), pd.DataFrame()

    mean_consumo = df_city['Consumo_MWh'].mean()
    std_consumo = df_city['Consumo_MWh'].std()

    if std_consumo == 0: # Evitar divisão por zero se todos os valores forem iguais
        df_city['Is_Anomaly'] = False
        return df_city, pd.DataFrame()

    df_city['Z_Score'] = (df_city['Consumo_MWh'] - mean_consumo) / std_consumo
    df_city['Is_Anomaly'] = np.abs(df_city['Z_Score']) > threshold_std

    anomalies_df = df_city[df_city['Is_Anomaly']].copy()
    anomalies_df['Tipo_Anomalia'] = np.where(anomalies_df['Z_Score'] > threshold_std, 'Alto', 'Baixo')
    anomalies_df = anomalies_df[['Data', 'Consumo_MWh', 'Temperatura_C', 'Tipo_Anomalia', 'Z_Score']]

    return df_city, anomalies_df

def plot_consumption_with_anomalies(df, city, anomalies_df):
    """Cria um gráfico de linha com anomalias marcadas."""
    df_city = df[df['Cidade'] == city].copy()

    fig = px.line(df_city, x='Data', y='Consumo_MWh',
                  title=f'Consumo Mensal de Energia com Anomalias - {city}',
                  labels={'Data': 'Data', 'Consumo_MWh': 'Consumo (MWh)'})
    
    if not anomalies_df.empty:
        fig.add_trace(go.Scatter(
            x=anomalies_df['Data'],
            y=anomalies_df['Consumo_MWh'],
            mode='markers',
            name='Anomalia',
            marker=dict(color='red', size=10, symbol='circle'),
            hoverinfo='text',
            text=[f"Anomalia {row['Tipo_Anomalia']}: {row['Consumo_MWh']:.2f} MWh ({row['Z_Score']:.2f} Z-Score)" 
                  for idx, row in anomalies_df.iterrows()]
        ))
    
    fig.update_layout(hovermode="x unified")
    return fig

def plot_seasonal_comparison_by_year(df, city):
    """Cria um gráfico de linha de sazonalidade por ano (requer múltiplos anos de dados)."""
    df_city = df[df['Cidade'] == city].copy()
    
    if df_city['Ano'].nunique() < 2:
        return None, "Não há dados suficientes (múltiplos anos) para esta análise de sazonalidade por ano."

    df_city['Mes_Nome'] = df_city['Data'].dt.strftime('%b') # Ex: Jan, Fev
    df_city['Dia_Mes_fake'] = df_city['Data'].dt.strftime('%m-%d') # Para manter ordem correta no eixo X

    fig = px.line(df_city, x='Dia_Mes_fake', y='Consumo_MWh', color='Ano',
                  title=f'Padrão Sazonal Mensal de Consumo - {city} por Ano',
                  labels={'Dia_Mes_fake': 'Mês', 'Consumo_MWh': 'Consumo (MWh)', 'Ano': 'Ano'},
                  line_shape="linear")
    
    # Assegura que o eixo X é ordenado por mês
    fig.update_xaxes(categoryorder='array', categoryarray=[f'{i:02d}-01' for i in range(1,13)])
    fig.update_layout(hovermode="x unified", legend_title_text="Ano")
    
    return fig, None

def plot_time_series_decomposition(df, city):
    """Realiza e plota a decomposição de série temporal (tendência, sazonalidade, resíduos)."""
    df_city = df[df['Cidade'] == city].set_index('Data').sort_index()
    if df_city.empty or len(df_city) < 24: # Pelo menos 2 anos para sazonalidade anual
        return None, "Dados insuficientes para decomposição de série temporal (mínimo de 24 meses recomendado)."

    # Assegura que a frequência é mensal
    df_city = df_city['Consumo_MWh'].asfreq('MS') 
    
    # Preenche NaNs se houver lacunas (necessário para decomposição)
    df_city = df_city.fillna(df_city.mean())

    try:
        # Usa um modelo aditivo (tendência + sazonalidade + resíduos)
        # Period = 12 para sazonalidade anual (12 meses)
        decomposition = seasonal_decompose(df_city, model='additive', period=12, extrapolate_trend='freq')

        fig = go.Figure()

        # Componente Original
        fig.add_trace(go.Scatter(x=df_city.index, y=df_city, mode='lines', name='Original',
                                 line=dict(color='blue')))
        # Componente de Tendência
        fig.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend, mode='lines', name='Tendência',
                                 line=dict(color='orange', width=2)))
        # Componente Sazonal
        fig.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, mode='lines', name='Sazonalidade',
                                 line=dict(color='green', dash='dash')))
        # Componente de Resíduos
        fig.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid, mode='lines', name='Resíduos',
                                 line=dict(color='red', dash='dot')))

        fig.update_layout(
            title=f'Decomposição da Série Temporal de Consumo - {city}',
            xaxis_title='Data',
            yaxis_title='Consumo (MWh)',
            hovermode="x unified",
            height=600 # Ajusta a altura para melhor visualização dos 4 gráficos
        )
        return fig, None
    except Exception as e:
        return None, f"Erro ao realizar decomposição da série temporal: {e}"
