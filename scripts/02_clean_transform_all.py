import json
import csv
import os
import sqlite3

input_file = "data/raw/dados_cidades_energia.json"
output_db = "data/processed/energia_cidades.db"

def clean_and_load_data():
    """
    Limpa os dados do JSON e os carrega para o banco de dados SQLite.
    """
    print(f"Limpando dados de {input_file} e carregando para o DB '{output_db}'...")
    
    if not os.path.exists(os.path.dirname(output_db)):
        os.makedirs(os.path.dirname(output_db), exist_ok=True)

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        conn = sqlite3.connect(output_db)
        cursor = conn.cursor()
        
        # Cria a tabela no banco de dados
        cursor.execute("DROP TABLE IF EXISTS energia_cidades")
        cursor.execute("""
            CREATE TABLE energia_cidades (
                Cidade TEXT,
                Data TEXT,
                Consumo_MWh REAL,
                Temperatura_C REAL,
                Populacao_Milhoes REAL,
                Fonte_Consumo TEXT
            )
        """)
        
        for entry in data:
            try:
                cidade = entry.get("cidade")
                ano = entry.get("ano")
                mes = entry.get("mes")
                consumo_mwh = entry.get("consumo_mwh")
                temp_c = entry.get("temp_c")
                populacao_milhoes = entry.get("pop_milhoes")
                fonte_consumo = entry.get("fonte_consumo")

                # Converte para string no formato YYYY-MM-DD
                data_str = f"{ano}-{mes:02d}-01"

                cursor.execute("""
                    INSERT INTO energia_cidades (Cidade, Data, Consumo_MWh, Temperatura_C, Populacao_Milhoes, Fonte_Consumo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cidade, data_str, consumo_mwh, temp_c, populacao_milhoes, fonte_consumo))
            except (ValueError, TypeError) as e:
                print(f"Erro de conversão de tipo ou dados inválidos na entrada: {entry}. Erro: {e}. Pulando.")
                continue
        
        conn.commit()
        conn.close()
        print("Limpeza de dados e carga no banco de dados concluída.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado. Execute 01_download_data.py primeiro.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo '{input_file}'. Erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    clean_and_load_data()
