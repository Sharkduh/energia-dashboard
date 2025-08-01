# src/models.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math

class EnergyModel:
    """
    Classe para encapsular o modelo de regressão linear para previsão de consumo.
    """
    def __init__(self):
        self.model = LinearRegression()
        self.coef = None
        self.intercept = None
        self.r2 = None
        self.mae = None
        self.rmse = None
        self.is_trained = False

    def train(self, df_city):
        """Treina o modelo de regressão linear."""
        if df_city.empty or len(df_city) < 2:
            self.is_trained = False
            return "Dados insuficientes para treinar o modelo."
        
        X = df_city['Temperatura_C'].values.reshape(-1, 1)
        y = df_city['Consumo_MWh'].values

        self.model.fit(X, y)
        self.coef = self.model.coef_[0]
        self.intercept = self.model.intercept_
        
        y_pred = self.model.predict(X)
        self.r2 = self.model.score(X, y)
        self.mae = mean_absolute_error(y, y_pred)
        self.rmse = math.sqrt(mean_squared_error(y, y_pred))
        self.is_trained = True
        return None

    def predict(self, temperature_c):
        """Faz uma previsão de consumo para uma dada temperatura."""
        if not self.is_trained:
            return None
        return self.model.predict(np.array([[temperature_c]]))[0]

    def get_summary(self):
        """Retorna um resumo dos resultados do modelo."""
        if not self.is_trained:
            return {
                "status": "Modelo não treinado.",
                "coeficiente": None,
                "intercepto": None,
                "r2": None,
                "mae": None,
                "rmse": None,
                "interpretacao": "Treine o modelo primeiro para ver os resultados."
            }

        interpretacao = ""
        if self.r2 > 0.7:
            interpretacao += "O modelo explica uma **alta proporção** da variação no consumo de energia."
        elif self.r2 > 0.4:
            interpretacao += "O modelo explica uma **parte razoável** da variação no consumo de energia."
        else:
            interpretacao += "O modelo explica uma **baixa proporção** da variação, sugerindo que outros fatores (não incluídos) são mais relevantes."
        
        interpretacao += f"\n\n**Impacto da Temperatura:** Para cada aumento de 1°C na temperatura, o consumo de energia tende a "
        if self.coef > 0:
            interpretacao += f"**aumentar em {abs(self.coef):.2f} MWh**."
            interpretacao += " Isso pode indicar uma forte dependência de sistemas de refrigeração em altas temperaturas ou, no inverno, temperaturas mais amenas (aumentando) diminuem o consumo de aquecimento."
        elif self.coef < 0:
            interpretacao += f"**diminuir em {abs(self.coef):.2f} MWh**."
            interpretacao += " Isso sugere que temperaturas mais frias aumentam o consumo de aquecimento, e temperaturas mais quentes diminuem essa necessidade."
        else:
            interpretacao += "a temperatura não parece ter um impacto linear significativo no consumo de energia."
        
        interpretacao += f"\n\n**Consumo Base (Intercepto):** Quando a temperatura é 0°C, o consumo base estimado é de {self.intercept:.2f} MWh."

        return {
            "status": "Modelo treinado com sucesso.",
            "coeficiente": self.coef,
            "intercepto": self.intercept,
            "r2": self.r2,
            "mae": self.mae,
            "rmse": self.rmse,
            "interpretacao": interpretacao
        }

if __name__ == '__main__':
    # Exemplo de uso (para teste da modularização)
    from data_loader import load_data
    df = load_data()
    if not df.empty:
        berlim_data = df[df['Cidade'] == 'Berlim']
        model_berlim = EnergyModel()
        status = model_berlim.train(berlim_data)
        if status:
            print(f"Erro ao treinar modelo de Berlim: {status}")
        else:
            print("\nResumo do Modelo - Berlim:")
            print(model_berlim.get_summary()["interpretacao"])
            print(f"Previsão para 10°C: {model_berlim.predict(10):.2f} MWh")

        ny_data = df[df['Cidade'] == 'Nova York']
        model_ny = EnergyModel()
        status = model_ny.train(ny_data)
        if status:
            print(f"Erro ao treinar modelo de Nova York: {status}")
        else:
            print("\nResumo do Modelo - Nova York:")
            print(model_ny.get_summary()["interpretacao"])
            print(f"Previsão para 25°C: {model_ny.predict(25):.2f} MWh")
