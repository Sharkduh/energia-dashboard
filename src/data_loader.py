# src/data_loader.py
import sqlite3
import pandas as pd
import os

DB_PATH = "data/processed/energia_cidades.db"

def load_data():
    """Carrega os dados da tabela energia_cidades do SQLite para um DataFrame Pandas."""
    if not os.path.exists(DB_PATH):
        print(f"Erro: Banco de dados não encontrado em {DB_PATH}. Execute './run.sh' primeiro.")
        return pd.DataFrame()
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Carrega a nova coluna 'Fonte_Consumo'
        df = pd.read_sql_query("SELECT * FROM energia_cidades", conn)
        df['Data'] = pd.to_datetime(df['Data'])
        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        return df
    except sqlite3.Error as e:
        print(f"Erro ao carregar dados do banco de dados: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
