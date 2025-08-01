# Projeto: Análise de Padrões de Consumo de Energia em Cidades Globais

## 🚀 Visão Geral do Projeto

Este projeto tem como objetivo principal analisar padrões de consumo de energia elétrica em duas grandes cidades globais - **Berlim (Alemanha)** e **Nova York (EUA)** - utilizando dados simulados de consumo, temperatura e população para o ano de 2023. O foco é demonstrar habilidades completas em análise de dados, desde a coleta e limpeza até a modelagem e comunicação de resultados, tudo isso com uma **abordagem de baixo consumo de memória e execução via terminal Linux**.

### Problema de Negócio

Com a crescente demanda por energia e as preocupações com sustentabilidade, entender os fatores que influenciam o consumo energético urbano é crucial para o planejamento de políticas públicas, otimização de infraestrutura e promoção da eficiência energética.

### Objetivos

1.  **Coletar e Consolidar Dados:** Obter dados de consumo de energia, temperatura e população para as cidades selecionadas.
2.  **Limpar e Transformar Dados:** Padronizar e preparar os dados para análise, lidando com diferentes formatos e unidades.
3.  **Realizar Análise Exploratória (EDA):** Identificar tendências sazonais, picos de consumo e a relação entre consumo e temperatura.
4.  **Desenvolver um Modelo Preditivo:** Criar um modelo de regressão linear simples para prever o consumo de energia com base na temperatura.
5.  **Comunicar Insights:** Apresentar as descobertas de forma clara e concisa, com recomendações baseadas nos dados.

## ⚙️ Ferramentas e Tecnologias Utilizadas

* **Sistema Operacional:** Linux (Ubuntu/Debian)
* **Linguagem de Programação:** Python 3
* **Controle de Versão:** Git
* **Manipulação de Dados (Terminal):** `curl`, `wget`, `grep`, `awk`, `sed`, `jq`
* **Banco de Dados:** SQLite3 (para armazenamento e consultas eficientes de dados tabulares)
* **Bibliotecas Python:** `requests` (para APIs - se usado), `csv`, `json`, `sqlite3` (built-in), `numpy`, `scikit-learn` (uso minimalista)
* **Visualização:** `gnuplot` (para gráficos exportados em PNG)

## 📂 Estrutura do Projeto


## 🚀 Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd analise_energia_global
    ```
2.  **Instale as dependências Python:**
    ```bash
    pip3 install -r requirements.txt
    ```
3.  **Torne o script de execução principal executável:**
    ```bash
    chmod +x run.sh
    ```
4.  **Execute o projeto:**
    ```bash
    ./run.sh
    ```
    Este script irá sequencialmente:
    * Simular/baixar dados brutos para `data/raw/`.
    * Limpar e transformar os dados, salvando-os em `data/processed/`.
    * Combinar os dados limpos e criar/popular o banco de dados SQLite `data/processed/energia_cidades.db`.
    * Executar as análises exploratórias (EDA) para ambas as cidades, gerando gráficos PNG na pasta `plots/`.
    * Treinar e exibir os resultados dos modelos de regressão para ambas as cidades no terminal.

## 📊 Principais Descobertas (Insights Esperados)

* **Sazonalidade:** Ambas as cidades devem apresentar padrões sazonais de consumo, com picos no inverno (aquecimento) e/ou verão (ar condicionado), dependendo do clima predominante.
* **Correlação Consumo-Temperatura:** Espera-se uma correlação perceptível entre temperatura e consumo de energia. Em climas temperados, temperaturas extremas (muito frio ou muito quente) tendem a aumentar o consumo.
* **Diferenças entre Cidades:** Berlim e Nova York, por terem perfis urbanos e climáticos distintos, podem apresentar diferentes perfis de consumo per capita ou total, e sensibilidade à temperatura.

## 💡 Recomendações

Com base nos insights, possíveis recomendações incluem:

* **Campanhas de Eficiência Energética:** Focadas nos meses de pico de consumo (ex: inverno em Berlim, verão em Nova York).
* **Investimento em Infraestrutura:** Avaliar a necessidade de reforço da rede elétrica em períodos de alta demanda.
* **Incentivo a Energias Renováveis:** Promover a geração distribuída (painéis solares) para mitigar os picos.
* **Políticas de Conscientização:** Educar a população sobre o impacto do uso de energia em diferentes temperaturas.

## 🚧 Limitações e Próximos Passos

* **Dados Simulados:** A principal limitação atual são os dados simulados. Um próximo passo crucial seria integrar fontes de dados reais e mais granulares (ex: dados diários ou por hora, por setor).
* **Variáveis Adicionais:** Incorporar outras variáveis como umidade, tipo de dia (útil/fim de semana), feriados, tipo de edificação, setor (residencial, comercial, industrial) poderia refinar a análise e a modelagem.
* **Modelos Mais Complexos:** Explorar modelos de previsão de séries temporais (ARIMA, Prophet) ou machine learning mais avançados para predições mais precisas.
* **Dashboard Interativo:** Criar um dashboard simples (usando ferramentas como Plotly ou Streamlit se a memória permitir, ou até mesmo um relatório HTML gerado por script) para visualização interativa dos resultados.

---

## 🤝 Contribuições

Sinta-se à vontade para propor melhorias, adicionar mais cidades ou refinar as análises.
