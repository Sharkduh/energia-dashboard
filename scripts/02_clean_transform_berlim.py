# scripts/02_clean_transform_berlim.py
import csv
import os

input_file = "data/raw/berlim_energia_temp_pop.csv"
output_file = "data/processed/berlim_energia_limpo.csv"

def clean_berlim_data():
    print(f"Limpando dados de Berlim de {input_file} para {output_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader) # Pula o cabeçalho

            # Mapeamento do cabeçalho
            col_idx = {name: i for i, name in enumerate(header)}

            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                # Novo cabeçalho unificado para o banco de dados
                new_header = ["Cidade", "Data", "Consumo_MWh", "Temperatura_C", "Populacao_Milhoes"]
                writer.writerow(new_header)

                for row in reader:
                    try:
                        ano = int(row[col_idx["Ano"]])
                        mes = int(row[col_idx["Mes"]])
                        # Consumo agora já é MWh direto do 01_download_data.py
                        consumo_mwh = float(row[col_idx["Consumo_MWh"]]) 
                        temperatura_c = float(row[col_idx["Temperatura_C"]])
                        populacao_milhoes = float(row[col_idx["Populacao_Milhoes"]])

                        # Formata a data para YYYY-MM-DD
                        data_str = f"{ano}-{mes:02d}-01"

                        writer.writerow(["Berlim", data_str, consumo_mwh, temperatura_c, populacao_milhoes])
                    except (ValueError, IndexError, KeyError) as e:
                        print(f"Erro ao processar linha: {row}. Erro: {e}. Pulando.")
                        continue
        print("Limpeza de dados de Berlim concluída.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado. Execute 01_download_data.py primeiro.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a limpeza dos dados de Berlim: {e}")

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    clean_berlim_data()
