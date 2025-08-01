import json
import csv
import os

input_file = "data/raw/ny_energia_temp_pop.json"
output_file = "data/processed/ny_energia_limpo.csv"

# --- REMOVER ESTA FUNÇÃO: A temperatura já vem em Celsius da Open-Meteo API ---
# def fahrenheit_to_celsius(f):
#     return (f - 32) * 5/9

def clean_ny_data():
    print(f"Limpando dados de Nova York de {input_file} para {output_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            # Ajustando o cabeçalho para ter quebra de linha correta
            new_header = ["Cidade", "Data", "Consumo_MWh", "Temperatura_C", "Populacao_Milhoes"]
            writer.writerow(new_header)

            for entry in data:
                try:
                    ano = entry.get("ano")
                    mes = entry.get("mes")
                    consumo_mwh = entry.get("consumo_mwh")
                    # --- MUDANÇA AQUI: Ler 'temp_c' diretamente, já é Celsius ---
                    temperatura_c = entry.get("temp_c")
                    populacao_milhoes = entry.get("pop_milhoes")

                    if None in [ano, mes, consumo_mwh, temperatura_c, populacao_milhoes]: # Ajustado aqui também
                        print(f"Entrada com dados ausentes: {entry}. Pulando.")
                        continue # Adicionado 'continue' para realmente pular a entrada

                    # Formata a data para 'YYYY-MM-DD'
                    data_str = f"{ano}-{mes:02d}-01"

                    # Ajustando o writer.writerow para ter quebra de linha correta
                    writer.writerow(["Nova York", data_str, consumo_mwh, temperatura_c, populacao_milhoes])
                except (ValueError, TypeError) as e:
                    print(f"Erro de conversão de tipo ou dados inválidos na entrada: {entry}. Erro: {e}. Pulando.")
                    continue # Adicionado 'continue' para realmente pular a entrada

        print("Limpeza de dados de Nova York concluída.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado. Execute 01_download_data.py primeiro.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo '{input_file}'. Certifique-se de que é um JSON válido. Erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a limpeza dos dados de Nova York: {e}")

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    clean_ny_data()
