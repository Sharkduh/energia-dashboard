# scripts/04_model_berlim.py
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression
import os

DB_PATH = "data/processed/energia_cidades.db"

def run_berlim_model():
    print("Treinando modelo de regressão linear para Berlim...")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT Temperatura_C, Consumo_MWh FROM energia_cidades WHERE Cidade = 'Berlim' ORDER BY Data")
        data = cursor.fetchall()

        if not data:
            print("Não há dados suficientes para treinar o modelo de Berlim.")
            return

        X = np.array([d[0] for d in data]).reshape(-1, 1)
        y = np.array([d[1] for d in data])

        model = LinearRegression()
        model.fit(X, y)

        print("\n--- Resultados do Modelo de Regressão Linear - Berlim ---")
        coeficiente = model.coef_[0]
        intercepto = model.intercept_
        r_quadrado = model.score(X, y)

        print(f"Coeficiente (Impacto da Temperatura): {coeficiente:.2f} MWh/°C")
        print(f"Intercepto (Consumo Base): {intercepto:.2f} MWh")
        print(f"R-quadrado (Qualidade do Modelo): {r_quadrado:.2f}")

        # Interpretação Intuitiva
        print("\n--- Interpretação do Modelo - Berlim ---")
        if r_quadrado > 0.7:
            print("O modelo explica uma **alta proporção** da variação no consumo de energia de Berlim.")
        elif r_quadrado > 0.4:
            print("O modelo explica uma **parte razoável** da variação no consumo de energia de Berlim.")
        else:
            print("O modelo explica uma **baixa proporção** da variação, sugerindo que outros fatores (não incluídos) são mais relevantes.")

        if coeficiente > 0:
            print(f"Para cada aumento de 1°C na temperatura, o consumo de energia tende a **aumentar em {abs(coeficiente):.2f} MWh**.")
            print("Isso pode indicar uma forte dependência de sistemas de refrigeração em altas temperaturas ou, no inverno, de que temperaturas mais amenas (aumentando) diminuem o consumo de aquecimento.")
        elif coeficiente < 0:
            print(f"Para cada aumento de 1°C na temperatura, o consumo de energia tende a **diminuir em {abs(coeficiente):.2f} MWh**.")
            print("Isso sugere que temperaturas mais frias aumentam o consumo de aquecimento, e temperaturas mais quentes diminuem essa necessidade.")
        else:
            print("A temperatura não parece ter um impacto linear significativo no consumo de energia, de acordo com este modelo.")

        print(f"O consumo base estimado, quando a temperatura é 0°C, é de {intercepto:.2f} MWh.")

        # Exemplo de Previsão
        temp_exemplo_frio = 5 # Temperatura fria (ex: inverno)
        temp_exemplo_quente = 25 # Temperatura quente (ex: verão)
        consumo_previsto_frio = model.predict(np.array([[temp_exemplo_frio]]))
        consumo_previsto_quente = model.predict(np.array([[temp_exemplo_quente]]))
        print(f"\nPrevisão: Consumo para {temp_exemplo_frio}°C: {consumo_previsto_frio[0]:.2f} MWh")
        print(f"Previsão: Consumo para {temp_exemplo_quente}°C: {consumo_previsto_quente[0]:.2f} MWh")


    except sqlite3.Error as e:
        print(f"Erro no SQLite durante a modelagem de Berlim: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a modelagem de Berlim: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main_":
    run_berlim_model()
