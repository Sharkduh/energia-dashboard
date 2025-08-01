import os
import csv
import json
import requests
import pandas as pd
from datetime import datetime
import io
import time

# --- Configurações da API ---
# Adicionando uma cidade brasileira para usar dados da ANEEL
CITIES_COORDS = {
    "Berlim": {"latitude": 52.52, "longitude": 13.41},
    "Nova York": {"latitude": 40.71, "longitude": -74.01},
    "Sao Paulo": {"latitude": -23.55, "longitude": -46.63}
}

# Período de dados (exemplo para 2023)
START_DATE = "2023-01-01"
END_DATE = "2023-12-31"

def get_population_data(city_name):
    """
    Função para simular dados de população.
    """
    if city_name == "Berlim":
        return 3.75 # Milhões
    elif city_name == "Nova York":
        return 8.4 # Milhões
    elif city_name == "Sao Paulo":
        return 12.33 # Milhões (dado de 2023, IBGE)
    return None

def fetch_open_meteo_temperature(city_name, start_date, end_date, retries=3, delay=5):
    """
    Busca dados de temperatura média diária da API Open-Meteo com re-tentativas.
    """
    coords = CITIES_COORDS.get(city_name)
    if not coords:
        print(f"Coordenadas não encontradas para {city_name}")
        return None

    api_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_mean",
        "timezone": "auto"
    }
    s = requests.Session()
    for i in range(retries):
        try:
            response = s.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("daily")
        except requests.exceptions.RequestException as e:
            print(f"Tentativa {i+1}/{retries}: Erro na requisição para Open-Meteo: {e}. Re-tentando...")
            time.sleep(delay)
    print(f"Falha ao buscar dados de temperatura para {city_name} após {retries} tentativas.")
    return None

def fetch_aneel_data():
    """
    Baixa e processa dados de consumo de energia da ANEEL para o ano de 2023.
    """
    print("Buscando dados de consumo de energia da ANEEL...")
    # URL para o CSV de 2023. Essa URL pode mudar a cada ano, então seria necessário
    # verificar no site da ANEEL se a URL está atualizada.
    url_aneel_2023 = "https://dadosabertos.aneel.gov.br/dataset/c2759976-b63e-4623-a50d-6e06b9973801/resource/903e0921-26c3-4d69-8d15-05e80811e72d/download/consumo-de-energia-eletrica-por-classe-2023.csv"
    
    try:
        df_aneel = pd.read_csv(url_aneel_2023, sep=';', encoding='latin1')
        print("Dados da ANEEL baixados com sucesso.")
        
        # Filtra para o município de São Paulo e agrega por mês
        df_sp = df_aneel[df_aneel['Municipio'] == 'SAO PAULO']
        if df_sp.empty:
            print("Município de São Paulo não encontrado nos dados da ANEEL.")
            return None
        
        # Ajusta a data para o formato correto
        df_sp['MÊS_REFERENCIA'] = pd.to_datetime(df_sp['MÊS_REFERENCIA'], format='%Y-%m-%d')
        
        # Consumo total mensal para São Paulo
        monthly_consumption = df_sp.groupby(df_sp['MÊS_REFERENCIA'].dt.to_period('M'))['CONSUMO_MMWH'].sum()
        
        # Mudar MWh para MWh
        # 1 MWh = 1.000 KWh
        # 1 GWh = 1.000.000 kWh
        # 1 kWh = 1000 MWh
        # De mil MWh, então é preciso multiplicar por 1000 para MWh
        # Consumo_MMWH = consumo em mil MWh, então para MWh é CONSUMO_MMWH * 1000
        # O site da ANEEL usa MWh, então a coluna `CONSUMO_MMWH` está em Mil MWh, ou seja, 1.000 MWh
        # Corrigindo a conversão para MWh
        monthly_consumption_mwh = monthly_consumption.astype(float) * 1000 
        
        df_monthly_sp = pd.DataFrame(monthly_consumption_mwh)
        df_monthly_sp = df_monthly_sp.reset_index()
        df_monthly_sp['MÊS_REFERENCIA'] = df_monthly_sp['MÊS_REFERENCIA'].dt.to_timestamp()
        df_monthly_sp['Ano'] = df_monthly_sp['MÊS_REFERENCIA'].dt.year
        df_monthly_sp['Mes'] = df_monthly_sp['MÊS_REFERENCIA'].dt.month
        
        # Colunas finais: ['Ano', 'Mes', 'Consumo_MWh']
        return df_monthly_sp[['Ano', 'Mes', 'CONSUMO_MMWH']]
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar dados da ANEEL: {e}")
        return None
    except Exception as e:
        print(f"Erro ao processar dados da ANEEL: {e}")
        return None

def generate_monthly_data(city_name, temp_data, aneel_data=None):
    """
    Agrega dados diários de temperatura para uma média mensal
    e combina com consumo de energia (real ou simulado) e população.
    """
    monthly_data = {}
    
    if temp_data and "time" in temp_data and "temperature_2m_mean" in temp_data:
        for i in range(len(temp_data["time"])):
            date_str = temp_data["time"][i]
            temp = temp_data["temperature_2m_mean"][i]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {"temps": []}
            if temp is not None:
                monthly_data[month_key]["temps"].append(temp)
    
    output_rows = []
    pop_milhoes = get_population_data(city_name)
    
    # Adicionando um campo para indicar a fonte dos dados
    source = "Simulado"
    
    # Dados de consumo SIMULADOS (Mude esta seção se encontrar dados reais)
    if city_name == "Berlim":
        simulated_consumption = [1500, 1450, 1300, 1100, 950, 800, 850, 900, 1050, 1200, 1350, 1600]
    elif city_name == "Nova York":
        simulated_consumption = [6500, 6200, 5800, 5300, 5100, 5400, 6000, 5900, 5500, 5200, 5500, 6300]
    else:
        simulated_consumption = None
    
    current_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date_obj = datetime.strptime(END_DATE, "%Y-%m-%d")
    
    month_idx = 0
    while current_date <= end_date_obj:
        year = current_date.year
        month = current_date.month
        month_key = current_date.strftime("%Y-%m")
        
        avg_temp = None
        if month_key in monthly_data and monthly_data[month_key]["temps"]:
            avg_temp = sum(monthly_data[month_key]["temps"]) / len(monthly_data[month_key]["temps"])
        
        if avg_temp is None:
            if city_name == "Berlim": avg_temp = 10.0
            elif city_name == "Nova York": avg_temp = 15.0
            else: avg_temp = 23.0 # Para São Paulo
            
        consumo_mes = None
        if city_name == "Sao Paulo" and aneel_data is not None:
            source = "Real (ANEEL)"
            # Converte a data para comparar com os dados da ANEEL
            aneel_month_data = aneel_data[(aneel_data['Ano'] == year) & (aneel_data['Mes'] == month)]
            if not aneel_month_data.empty:
                consumo_mes = aneel_month_data['CONSUMO_MMWH'].iloc[0] * 1000 # Convertendo para MWh
            else:
                # Caso não haja dados da ANEEL para o mês, usamos um valor simulado
                # AVISO: A ANEEL já tem dados completos para o ano de 2023. Isso seria mais útil no futuro.
                # Para São Paulo, a sazonalidade é mais ligada a refrigeração (verão) e chuva/aquecimento (inverno)
                simulated_consumption_sp = [8000, 7800, 7500, 7000, 6500, 6000, 6200, 6800, 7200, 7400, 7600, 8200]
                consumo_mes = simulated_consumption_sp[month_idx % 12]
        else:
            source = "Simulado"
            if simulated_consumption:
                consumo_mes = simulated_consumption[month_idx % 12]
        
        if consumo_mes is not None:
            row = {
                "ano": year,
                "mes": month,
                "consumo_mwh": consumo_mes,
                "temp_c": avg_temp,
                "pop_milhoes": pop_milhoes,
                "fonte_consumo": source
            }
            output_rows.append(row)
        
        # Avança para o próximo mês
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)
        
        month_idx += 1
        if current_date.year > int(END_DATE.split('-')[0]):
            break

    return output_rows

def main():
    os.makedirs("data/raw", exist_ok=True)
    
    # Coleta de dados da ANEEL para São Paulo
    aneel_data = fetch_aneel_data()
    
    # Agora, itera sobre as cidades para buscar temperatura e gerar os dados
    all_final_data = []
    for city_name in CITIES_COORDS.keys():
        print(f"Processando dados para {city_name}...")
        temp_data = fetch_open_meteo_temperature(city_name, START_DATE, END_DATE)
        final_data = generate_monthly_data(city_name, temp_data, aneel_data if city_name == "Sao Paulo" else None)
        
        if final_data:
            all_final_data.extend(final_data)
            print(f"Dados de {city_name} gerados com sucesso.")
        else:
            print(f"Não foi possível gerar dados para {city_name}.")
    
    if all_final_data:
        # Salva todos os dados em um único JSON para simplificar
        file_path_all = "data/raw/dados_cidades_energia.json"
        with open(file_path_all, 'w') as f:
            json.dump(all_final_data, f, indent=4)
        print(f"Todos os dados (Berlim, Nova York e Sao Paulo) salvos em {file_path_all}")
    
    print("Coleta e Geração de dados concluída!")

if __name__ == "__main__":
    main()
