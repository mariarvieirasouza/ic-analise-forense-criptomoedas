# Identificação de Mecanismos e Práticas de Cashing Out em Criptomoedas

Este repositório contém o código-fonte, dados e publicações relacionados à pesquisa de Iniciação Científica intitulada **"Identificação de Mecanismos e Práticas de Cashing Out em Criptomoedas"**. O projeto foca na análise forense de transações de Bitcoin, especificamente na identificação e estudo de mixers como **Wasabi** e **JoinMarket**, que são muito usados como métodos para lavagem de dinheiro, já que aumentam a privacidade e ocultam o rastro de fundos.

> **Pesquisa em andamento** 

As etapas em desenvolvimento atualmente são: migração para um banco de dados devido ao grande volume de transações e clsterização dos endereços para estudar os efeitos do uso de mixer nas heurísticas de clusterização.

---

## Estrutura do Repositório

* **/dados_extraidos**: Armazena os arquivos JSON brutos coletados via API, arquivos CSV resultantes das análises estatísticas e os gráficos de visualização gerados.
* **/Publicações**:
    * `Poster_WTDCC2025.pdf`: Poster apresentado no XIX Workshop de Teses e Dissertações em Ciência da Computação (WTDCC 2025 - FACOM).
    * `Resumo_WTDCC2025.pdf`: Resumo publicado nos anais do evento. [Acesse os anais aqui](https://techweek.facom.ufu.br/sites/default/files/2026-01/AnaisXIXWTDCC.pdf).
* **Scripts (Raiz)**: Conjunto de algoritmos em Python para coleta e análise.

---

## Ferramentas e Tecnologias

Para executar os scripts deste projeto, é necessário o **Python 3.x** e as seguintes bibliotecas:

* **Requisições de API:** `requests`
* **Processamento de JSON (Arquivos Grandes):** `ijson`
* **Manipulação de Dados:** `pandas`
* **Geração de Gráficos:** `matplotlib`, `seaborn`

---

## Descrição dos Scripts

### 1. Coleta de Dados
* `extrai_hashes_bloco.py`: Coleta hashes de blocos em um intervalo de tempo específico através da API da **Blockchain.com**.
* `extrai_todas_transações.py`: A partir dos hashes, baixa todas as transações de cada bloco, feito em lotes para evitar sobrecarga.

### 2. Filtragem e Identificação (Heurísticas)
* `extrai_wasabi_e_joinmarket_das_transacoes.py`: Analisa arquivos locais JSON contendo transações e aplica heurísticas para identificar transações dos mixers Wasabi (versões 1.0, 1.1 e 2.0) e JoinMarket.
* `extrai_wasabi_e_joinmarket_dos_blocos.py`: Versão otimizada que realiza a extração via API, filtrando as transações por meio das heurísticas, em lotes de blocos, e salvando apenas  transações que pertencem a um dos mixers.

### 3. Análise e Estatística
* `conta_dias.py`: Realiza a contagem de transações por dia.
* `analise_estatistica.py`: Análise estatística que gera um CSV com métricas como: valor total mixado em BTC, média de endereços de entrada/saída por transação e taxas de reuso de endereços (interno e global).
* `grafico.py`: Gera gráficos de linhas para visualizar o uso dos mixers ao longo do tempo (analisa a quantidade de transações diária por mixer).


---

## Instituição
Faculdade de Computação (FACOM) – Universidade Federal de Uberlândia (UFU)