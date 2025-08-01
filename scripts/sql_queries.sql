-- scripts/sql_queries.sql
-- Parte 1: Criação e Importação do Banco de Dados

-- Cria a tabela de energia se não existir
CREATE TABLE IF NOT EXISTS energia_cidades (
    Cidade TEXT NOT NULL,
    Data DATE NOT NULL,
    Consumo_MWh REAL NOT NULL,
    Temperatura_C REAL NOT NULL,
    Populacao_Milhoes REAL NOT NULL
);

-- Apaga dados existentes para garantir um re-import limpo
DELETE FROM energia_cidades;

-- Importa os dados do CSV combinado (assumindo que o CSV tem cabeçalho)
.mode csv
.import 'data/processed/dados_combinados.csv' energia_cidades

-- Remove a linha de cabeçalho importada como dado (se houver)
DELETE FROM energia_cidades WHERE Cidade = 'Cidade' AND Data = 'Data';

-- Visualiza algumas linhas para confirmar a importação
SELECT * FROM energia_cidades LIMIT 5;

-- Mostra o esquema da tabela
.schema energia_cidades

-- --- Parte 2: Consultas de Análise Exploratória e para Insights (serão usadas nos scripts Python) ---

-- 1. Consumo Médio Mensal por Cidade e Mês
-- Usado para sazonalidade e gráficos comparativos.
-- SELECT Cidade, STRFTIME('%Y-%m', Data) AS Mes, AVG(Consumo_MWh) AS Consumo_Medio_MWh FROM energia_cidades GROUP BY Cidade, Mes ORDER BY Cidade, Mes;

-- 2. Consumo Total Anual por Cidade
-- SELECT Cidade, STRFTIME('%Y', Data) AS Ano, SUM(Consumo_MWh) AS Consumo_Total_MWh FROM energia_cidades GROUP BY Cidade, Ano ORDER BY Cidade, Ano;

-- 3. Consumo Per Capita Médio Mensal por Cidade
-- SELECT Cidade, STRFTIME('%Y-%m', Data) AS Mes, (AVG(Consumo_MWh) / AVG(Populacao_Milhoes)) AS Consumo_Per_Capita_MWh FROM energia_cidades GROUP BY Cidade, Mes ORDER BY Cidade, Mes;

-- 4. Consumo Per Capita Total Anual por Cidade
-- SELECT Cidade, STRFTIME('%Y', Data) AS Ano, (SUM(Consumo_MWh) / AVG(Populacao_Milhoes)) AS Consumo_Per_Capita_Anual_MWh FROM energia_cidades GROUP BY Cidade, Ano ORDER BY Cidade, Ano;

-- 5. Meses de Pico e Vale de Consumo por Cidade
-- Mês de Pico:
-- SELECT Cidade, STRFTIME('%m', Data) AS Mes, SUM(Consumo_MWh) AS Consumo_Total_Mes
-- FROM energia_cidades
-- GROUP BY Cidade, Mes
-- ORDER BY Cidade, Consumo_Total_Mes DESC
-- LIMIT 24; -- Pegar os 12 maiores de cada cidade (se houver dados de múltiplos anos, ajuste)

-- Mês de Vale:
-- SELECT Cidade, STRFTIME('%m', Data) AS Mes, SUM(Consumo_MWh) AS Consumo_Total_Mes
-- FROM energia_cidades
-- GROUP BY Cidade, Mes
-- ORDER BY Cidade, Consumo_Total_Mes ASC
-- LIMIT 24; -- Pegar os 12 menores de cada cidade

-- 6. Dados para Análise de Outliers (Todos os dados para processamento em Python)
-- SELECT Cidade, Data, Consumo_MWh FROM energia_cidades ORDER BY Cidade, Data;
