#!/bin/bash

echo "Iniciando o Projeto de Análise de Consumo de Energia..."
echo "-----------------------------------------------------"

# Remove arquivos de saída anteriores para um re-run limpo
echo "Removendo arquivos de saída anteriores..."
rm -rf data/processed/*.csv data/processed/*.db data/raw/*.json data/raw/*.csv plots/
echo "-----------------------------------------------------"

# 1. Coleta de Dados (agora com API real para temperatura e dados ANEEL)
echo "Passo 1: Coletando dados brutos..."
python3 scripts/01_download_data.py
if [ $? -ne 0 ]; then echo "Erro no Passo 1. Abortando."; exit 1; fi
echo "-----------------------------------------------------"

# 2. Limpeza e Carregamento no DB (agora em um único script)
echo "Passo 2: Limpando e carregando dados combinados no banco de dados SQLite..."
python3 scripts/02_clean_transform_all.py
if [ $? -ne 0 ]; then echo "Erro no Passo 2. Abortando."; exit 1; fi
echo "-----------------------------------------------------"

echo "Preparação de dados concluída. O banco de dados está pronto para ser usado pelo dashboard."
echo "Para executar o dashboard interativo, utilize:"
echo "streamlit run app.py"
