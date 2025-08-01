# scripts/03_eda_comparativa.py
import sqlite3
import os

DB_PATH = "data/processed/energia_cidades.db"
PLOTS_DIR = "plots"

def run_comparative_eda():
    print("Executando EDA Comparativa entre Berlim e Nova York...")
    os.makedirs(PLOTS_DIR, exist_ok=True) # Garante que a pasta 'plots' existe

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Gráfico Comparativo de Consumo Mensal
        print("\n--- Gerando Gráfico Comparativo de Consumo Mensal ---")
        cursor.execute("SELECT Data, Consumo_MWh FROM energia_cidades WHERE Cidade = 'Berlim' ORDER BY Data")
        berlim_data = cursor.fetchall()
        cursor.execute("SELECT Data, Consumo_MWh FROM energia_cidades WHERE Cidade = 'Nova York' ORDER BY Data")
        ny_data = cursor.fetchall()

        with open(f"{PLOTS_DIR}/comparativo_consumo_mensal_berlim.txt", "w") as f:
            for row in berlim_data:
                f.write(f"{row[0]} {row[1]}\n")
        with open(f"{PLOTS_DIR}/comparativo_consumo_mensal_ny.txt", "w") as f:
            for row in ny_data:
                f.write(f"{row[0]} {row[1]}\n")

        gnuplot_script_comparativo = f"""
        set terminal pngcairo size 1000,500 font "arial,10"
        set output '{PLOTS_DIR}/comparativo_consumo_mensal.png'
        set title 'Consumo Mensal de Energia: Berlim vs. Nova York (2023)'
        set xlabel 'Mês'
        set ylabel 'Consumo (MWh)'
        set xdata time
        set timefmt "%Y-%m-%d"
        set format x "%b"
        set grid
        set border 3
        set style data linespoints
        plot '{PLOTS_DIR}/comparativo_consumo_mensal_berlim.txt' using 1:2 title 'Berlim' linecolor rgb 'blue', \\
             '{PLOTS_DIR}/comparativo_consumo_mensal_ny.txt' using 1:2 title 'Nova York' linecolor rgb 'red'
        """
        with open(f"{PLOTS_DIR}/comparativo_consumo_mensal.gp", "w") as f:
            f.write(gnuplot_script_comparativo)
        os.system(f"gnuplot {PLOTS_DIR}/comparativo_consumo_mensal.gp")
        print(f"Gráfico comparativo de consumo mensal salvo em {PLOTS_DIR}/comparativo_consumo_mensal.png")

        # 2. Gráfico Comparativo de Consumo Anual Total (Barras)
        print("\n--- Gerando Gráfico Comparativo de Consumo Anual Total ---")
        cursor.execute("""
            SELECT Cidade, SUM(Consumo_MWh) AS Consumo_Total_MWh
            FROM energia_cidades
            GROUP BY Cidade
            ORDER BY Consumo_Total_MWh DESC
        """)
        anual_total_data = cursor.fetchall()

        with open(f"{PLOTS_DIR}/comparativo_anual_total.txt", "w") as f:
            for i, row in enumerate(anual_total_data):
                f.write(f"{i} {row[1]} \"{row[0]}\"\n") # gnuplot precisa de índice numérico para barras

        gnuplot_script_barras = f"""
        set terminal pngcairo size 800,450 font "arial,10"
        set output '{PLOTS_DIR}/comparativo_anual_total.png'
        set title 'Consumo Anual Total de Energia (2023)'
        set ylabel 'Consumo (MWh)'
        set style data histogram
        set style fill solid 1.0 border -1
        set boxwidth 0.9
        set xtics format ""
        set xtics nomirror
        plot '{PLOTS_DIR}/comparativo_anual_total.txt' using 2:xtic(3) title 'Consumo Total'
        """
        with open(f"{PLOTS_DIR}/comparativo_anual_total.gp", "w") as f:
            f.write(gnuplot_script_barras)
        os.system(f"gnuplot {PLOTS_DIR}/comparativo_anual_total.gp")
        print(f"Gráfico comparativo de consumo anual total salvo em {PLOTS_DIR}/comparativo_anual_total.png")

        # 3. Gráfico Comparativo de Consumo Per Capita Anual (Barras)
        print("\n--- Gerando Gráfico Comparativo de Consumo Per Capita Anual ---")
        cursor.execute("""
            SELECT Cidade, (SUM(Consumo_MWh) / AVG(Populacao_Milhoes)) AS Consumo_Per_Capita_Anual_MWh
            FROM energia_cidades
            GROUP BY Cidade
            ORDER BY Consumo_Per_Capita_Anual_MWh DESC
        """)
        per_capita_data = cursor.fetchall()

        with open(f"{PLOTS_DIR}/comparativo_per_capita_anual.txt", "w") as f:
            for i, row in enumerate(per_capita_data):
                # Converte para kWh/pessoa para melhor legibilidade
                f.write(f"{i} {row[1]/1000000 * 1000} \"{row[0]}\"\n")

        gnuplot_script_per_capita = f"""
        set terminal pngcairo size 800,450 font "arial,10"
        set output '{PLOTS_DIR}/comparativo_per_capita_anual.png'
        set title 'Consumo Anual de Energia Per Capita (2023)'
        set ylabel 'Consumo (kWh/pessoa)'
        set style data histogram
        set style fill solid 1.0 border -1
        set boxwidth 0.9
        set xtics format ""
        set xtics nomirror
        plot '{PLOTS_DIR}/comparativo_per_capita_anual.txt' using 2:xtic(3) title 'Consumo Per Capita'
        """
        with open(f"{PLOTS_DIR}/comparativo_per_capita_anual.gp", "w") as f:
            f.write(gnuplot_script_per_capita)
        os.system(f"gnuplot {PLOTS_DIR}/comparativo_per_capita_anual.gp")
        print(f"Gráfico comparativo de consumo per capita anual salvo em {PLOTS_DIR}/comparativo_per_capita_anual.png")

    except sqlite3.Error as e:
        print(f"Erro no SQLite durante a EDA comparativa: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a EDA comparativa: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_comparative_eda()
