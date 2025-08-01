# scripts/03_eda_ny.py
import sqlite3
import os
import asciichartpy # Nova importação
import numpy as np # Para cálculo de desvio padrão

DB_PATH = "data/processed/energia_cidades.db"
PLOTS_DIR = "plots"

def run_ny_eda():
    print("Executando EDA para Nova York...")
    os.makedirs(PLOTS_DIR, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Consumo Mensal ao longo do tempo (mantido para gnuplot)
        print("\n--- Consumo Mensal de Energia em Nova York ---")
        cursor.execute("SELECT Data, Consumo_MWh FROM energia_cidades WHERE Cidade = 'Nova York' ORDER BY Data")
        data_for_plot = cursor.fetchall()

        with open(f"{PLOTS_DIR}/ny_consumo_mensal.txt", "w") as f:
            for row in data_for_plot:
                f.write(f"{row[0]} {row[1]}\n")

        gnuplot_script = f"""
        set terminal pngcairo size 800,450 font "arial,10"
        set output '{PLOTS_DIR}/ny_consumo_mensal.png'
        set title 'Consumo Mensal de Energia - Nova York (2023)'
        set xlabel 'Mês'
        set ylabel 'Consumo (MWh)'
        set xdata time
        set timefmt "%Y-%m-%d"
        set format x "%b"
        set grid
        set border 3
        set style data linespoints
        plot '{PLOTS_DIR}/ny_consumo_mensal.txt' using 1:2 title 'Consumo'
        """
        with open(f"{PLOTS_DIR}/ny_consumo_mensal.gp", "w") as f:
            f.write(gnuplot_script)
        os.system(f"gnuplot {PLOTS_DIR}/ny_consumo_mensal.gp")
        print(f"Gráfico de consumo mensal de Nova York salvo em {PLOTS_DIR}/ny_consumo_mensal.png")

        # 2. Consumo vs. Temperatura (mantido para gnuplot)
        print("\n--- Consumo vs. Temperatura em Nova York ---")
        cursor.execute("SELECT Temperatura_C, Consumo_MWh FROM energia_cidades WHERE Cidade = 'Nova York' ORDER BY Temperatura_C")
        data_for_plot_temp = cursor.fetchall()

        with open(f"{PLOTS_DIR}/ny_consumo_temperatura.txt", "w") as f:
            for row in data_for_plot_temp:
                f.write(f"{row[0]} {row[1]}\n")

        gnuplot_script_temp = f"""
        set terminal pngcairo size 800,450 font "arial,10"
        set output '{PLOTS_DIR}/ny_consumo_temperatura.png'
        set title 'Consumo de Energia vs. Temperatura - Nova York'
        set xlabel 'Temperatura (°C)'
        set ylabel 'Consumo (MWh)'
        set grid
        set border 3
        set style data points
        plot '{PLOTS_DIR}/ny_consumo_temperatura.txt' using 1:2 title 'Consumo'
        """
        with open(f"{PLOTS_DIR}/ny_consumo_temperatura.gp", "w") as f:
            f.write(gnuplot_script_temp)
        os.system(f"gnuplot {PLOTS_DIR}/ny_consumo_temperatura.gp")
        print(f"Gráfico de consumo vs. temperatura de Nova York salvo em {PLOTS_DIR}/ny_consumo_temperatura.png")

        # --- NOVAS ANÁLISES PARA INTUITIVIDADE ---

        # 3. Estatísticas Descritivas (Aprimorado)
        print("\n--- Estatísticas Descritivas - Nova York ---")
        cursor.execute("SELECT AVG(Consumo_MWh), MIN(Consumo_MWh), MAX(Consumo_MWh), SUM(Consumo_MWh) FROM energia_cidades WHERE Cidade = 'Nova York'")
        stats = cursor.fetchone()
        print(f"Média Consumo: {stats[0]:.2f} MWh")
        print(f"Mínimo Consumo: {stats[1]:.2f} MWh")
        print(f"Máximo Consumo: {stats[2]:.2f} MWh")
        print(f"Total Anual: {stats[3]:.2f} MWh")

        # 4. Consumo Per Capita
        print("\n--- Consumo Per Capita - Nova York ---")
        cursor.execute("SELECT (SUM(Consumo_MWh) / AVG(Populacao_Milhoes)) AS Consumo_Per_Capita_Anual_MWh FROM energia_cidades WHERE Cidade = 'Nova York'")
        consumo_per_capita = cursor.fetchone()[0]
        consumo_per_capita_por_pessoa = consumo_per_capita / 1000000 # MWh por pessoa ao ano
        print(f"Consumo Total Anual Per Capita: {consumo_per_capita_por_pessoa:.4f} MWh/pessoa")
        print(f"Consumo Total Anual Per Capita (em kWh/pessoa): {consumo_per_capita_por_pessoa * 1000:.2f} kWh/pessoa")

        # 5. Meses de Pico e Vale de Consumo
        print("\n--- Meses de Pico e Vale de Consumo - Nova York ---")
        cursor.execute("""
            SELECT STRFTIME('%m', Data) AS Mes_Num, SUM(Consumo_MWh) AS Consumo_Total_Mes
            FROM energia_cidades
            WHERE Cidade = 'Nova York'
            GROUP BY Mes_Num
            ORDER BY Consumo_Total_Mes DESC
            LIMIT 1
        """)
        pico = cursor.fetchone()
        mes_pico = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"][int(pico[0])-1]
        print(f"Mês de Pico: {mes_pico} ({pico[1]:.2f} MWh)")

        cursor.execute("""
            SELECT STRFTIME('%m', Data) AS Mes_Num, SUM(Consumo_MWh) AS Consumo_Total_Mes
            FROM energia_cidades
            WHERE Cidade = 'Nova York'
            GROUP BY Mes_Num
            ORDER BY Consumo_Total_Mes ASC
            LIMIT 1
        """)
        vale = cursor.fetchone()
        mes_vale = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"][int(vale[0])-1]
        print(f"Mês de Vale: {mes_vale} ({vale[1]:.2f} MWh)")

        # 6. Detecção Simples de Anomalias (usando Z-score para Consumo)
        print("\n--- Detecção de Anomalias - Nova York ---")
        cursor.execute("SELECT Data, Consumo_MWh FROM energia_cidades WHERE Cidade = 'Nova York' ORDER BY Data")
        consumos = [row[1] for row in cursor.fetchall()]
        datas = [row[0] for row in cursor.fetchall()]

        if len(consumos) > 1:
            media = np.mean(consumos)
            desvio_padrao = np.std(consumos)
            limite_superior = media + 1.5 * desvio_padrao
            limite_inferior = media - 1.5 * desvio_padrao

            anomalias_encontradas = False
            for i, consumo in enumerate(consumos):
                if consumo > limite_superior:
                    print(f"Anomalia (Alto): {datas[i]} com Consumo de {consumo:.2f} MWh (Acima de {limite_superior:.2f})")
                    anomalias_encontradas = True
                elif consumo < limite_inferior:
                    print(f"Anomalia (Baixo): {datas[i]} com Consumo de {consumo:.2f} MWh (Abaixo de {limite_inferior:.2f})")
                    anomalias_encontradas = True
            if not anomalias_encontradas:
                print("Nenhuma anomalia significativa detectada com base nos limites definidos (1.5 desvios padrão).")
        else:
            print("Não há dados suficientes para detectar anomalias.")

        # 7. Mini-Gráfico ASCII de Consumo Mensal
        print("\n--- Visão Rápida: Consumo Mensal - Nova York (ASCII) ---")
        if len(consumos) > 1:
            consumos_ascii = consumos[-12:]
            chart = asciichartpy.plot(consumos_ascii, {'height': 10, 'offset': 3})
            print(chart)
            meses_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            print(f"Meses: {', '.join(meses_labels[-len(consumos_ascii):])}")
        else:
            print("Dados insuficientes para gráfico ASCII.")

    except sqlite3.Error as e:
        print(f"Erro no SQLite para Nova York: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a EDA de Nova York: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_ny_eda()
