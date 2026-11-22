# 🌦️ ETL de Dados Climáticos por CEP

Projeto desenvolvido em Python para consumir APIs públicas, obter informações de endereço e previsão do tempo a partir de um CEP, realizar transformações e validações dos dados, armazená-los temporariamente em SQLite e exportar os resultados em CSV e Parquet.

O projeto aplica conceitos de **ETL (Extract, Transform, Load)**, integração de APIs, tratamento de erros, qualidade de dados e organização de pipelines de processamento.

## 🎯 Objetivo do projeto

Desenvolver um pipeline de dados capaz de:

- Receber um CEP informado pelo usuário.
- Consultar informações de endereço por meio da API ViaCEP.
- Identificar as coordenadas geográficas da cidade utilizando a API Open-Meteo Geocoding.
- Consultar a temperatura atual e a previsão diária para os próximos 7 dias.
- Armazenar e relacionar os dados utilizando SQLite.
- Padronizar e transformar os dados com Pandas.
- Tratar valores nulos e registros duplicados.
- Calcular métricas derivadas de temperatura.
- Executar auditorias de qualidade dos dados.
- Exportar os resultados nos formatos CSV e Parquet.

## 🏗️ Arquitetura do projeto

O projeto foi organizado em módulos, separando as responsabilidades de consumo de APIs, processamento, armazenamento, transformação e auditoria.

```text
projeto-etl-clima/
│
├── App.py
│
├── Consumo_Api.py
│
├── requisicoes.py
│
├── Transformacao_sql.py
│
├── Transformacoes.py
│
├── Auditoria.py
│
├── requirements.txt
│
└── resultados/
    ├── auditoria_qualidade.csv
    ├── Previsao_clima_por_cep.csv
    └── dados_parquet/
```

### Responsabilidade dos módulos

| Arquivo | Responsabilidade |
|---|---|
| `App.py` | Orquestra o pipeline ETL e executa as validações e etapas do processamento. |
| `Consumo_Api.py` | Realiza as consultas às APIs ViaCEP e Open-Meteo. |
| `requisicoes.py` | Centraliza as requisições HTTP, controle de intervalo, timeout e retentativas. |
| `Transformacao_sql.py` | Cria tabelas SQLite, insere os dados e realiza o relacionamento entre endereço e previsão. |
| `Transformacoes.py` | Executa padronização, tratamento de nulos, remoção de duplicados e enriquecimento de métricas. |
| `Auditoria.py` | Verifica schema, completude, unicidade e consistência dos dados. |
| `requirements.txt` | Lista as dependências necessárias para executar o projeto. |

## 🔄 Fluxo de processamento ETL

O pipeline segue as etapas abaixo:

1. **Extract – Extração**
   - Recebe o CEP informado pelo usuário.
   - Consulta a API ViaCEP para obter o endereço.
   - Consulta a API Open-Meteo Geocoding para obter latitude e longitude.
   - Consulta a API Open-Meteo Forecast para obter dados climáticos.

2. **Load – Armazenamento inicial**
   - Cria as tabelas `endereco` e `previsao` no SQLite.
   - Insere os dados de endereço e previsão.
   - Realiza um `INNER JOIN` utilizando o CEP como chave de relacionamento.

3. **Transform – Transformação**
   - Padroniza tipos de dados.
   - Converte datas e temperaturas.
   - Remove registros sem informações essenciais.
   - Preenche campos textuais ausentes.
   - Remove registros duplicados considerando CEP e data.
   - Calcula métricas derivadas de temperatura.

4. **Data Quality – Auditoria**
   - Verifica os tipos de dados esperados.
   - Identifica valores nulos.
   - Verifica unicidade.
   - Identifica inconsistências entre temperaturas mínima e máxima.

5. **Export – Exportação**
   - Gera arquivos CSV para consulta.
   - Gera arquivos Parquet com particionamento por ano e mês.

## 🌐 APIs utilizadas

### ViaCEP

Utilizada para consultar informações de endereço a partir do CEP.

Documentação: https://viacep.com.br/

### Open-Meteo Geocoding API

Utilizada para localizar latitude e longitude com base na cidade e na unidade federativa.

Documentação: https://open-meteo.com/en/docs/geocoding-api

### Open-Meteo Forecast API

Utilizada para obter:

- Temperatura atual.
- Temperatura mínima diária.
- Temperatura máxima diária.
- Previsão para 7 dias.

Documentação: https://open-meteo.com/en/docs

## 🛡️ Controle de requisições e tratamento de erros

O módulo `requisicoes.py` centraliza a comunicação HTTP e implementa:

- Sessão compartilhada com `requests.Session()`.
- Controle de intervalo entre requisições.
- Timeout de 10 segundos.
- Até 3 tentativas de requisição.
- Backoff exponencial entre tentativas.
- Tratamento diferenciado para erros HTTP permanentes e temporários.
- Leitura do cabeçalho `Retry-After` para respostas HTTP 429, quando informado em segundos.

No `App.py`, também são realizadas validações para evitar o processamento de dados inválidos, incluindo:

- Validação do formato do CEP.
- Validação da resposta do ViaCEP.
- Validação dos limites de latitude e longitude.
- Verificação dos campos obrigatórios da previsão climática.
- Validação da estrutura do DataFrame.
- Tratamento de erros nas operações SQLite, transformações, auditoria e exportação.

## 📊 Transformações e métricas

O projeto realiza o enriquecimento dos dados climáticos com métricas calculadas a partir das temperaturas mínima e máxima.

### Amplitude térmica

Diferença entre a temperatura máxima e a mínima.

### Temperatura média estimada

Estimativa calculada a partir das temperaturas mínima e máxima.

Essas métricas são utilizadas para enriquecer a base de dados e permitir análises posteriores.

## 🔎 Auditoria de qualidade dos dados

O módulo `Auditoria.py` realiza verificações para avaliar a qualidade da base processada.

| Verificação | Objetivo |
|---|---|
| Schema | Verificar se as colunas possuem os tipos esperados. |
| Completude | Identificar valores nulos e calcular a proporção de ausência. |
| Unicidade | Verificar registros duplicados considerando CEP e data. |
| Range Check | Identificar inconsistências em que a temperatura mínima é superior à máxima. |

O resultado da auditoria é exportado em CSV, permitindo consultar os problemas identificados e o status de cada verificação.

## 📁 Arquivos gerados

Ao concluir o processamento, o projeto cria a pasta `resultados/`.

### Previsao_clima_por_cep.csv

Contém os dados de endereço e previsão climática após as transformações.

As colunas de temperatura são formatadas com duas casas decimais e a unidade °C.

### auditoria_qualidade.csv

Contém os resultados das verificações de qualidade dos dados, incluindo problemas encontrados e status das validações.

### dados_parquet/

Armazena os dados processados no formato Parquet, utilizando compressão Snappy e particionamento por ano e mês.

Exemplo da organização:

```text
dados_parquet/
├── ano=2026/
│   ├── mes=11/
│   └── mes=12/
└── ano=2027/
    └── mes=1/
```

O formato Parquet facilita o armazenamento e o consumo dos dados em ferramentas de análise.

## ⚙️ Tecnologias utilizadas

- **Python:** linguagem principal.
- **Pandas:** manipulação, transformação e análise dos dados.
- **Requests:** consumo das APIs HTTP.
- **SQLite:** armazenamento relacional temporário.
- **PyArrow:** geração dos arquivos Parquet.
- **APIs REST:** integração com serviços externos.

## 🚀 Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/lucasls1/Desafio-Python-FT03-P1.git
```

### 2. Acessar a pasta

```bash
cd SEU-REPOSITORIO
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Executar o projeto

```bash
python App.py
```

### 5. Informar o CEP

Após executar o programa, informe um CEP brasileiro quando solicitado.

```text
Digite o CEP: 70040902
```

O sistema realizará as consultas, processará os dados e gerará os arquivos na pasta `resultados/`.

## 📦 Dependências

As dependências estão especificadas em `requirements.txt`:

```text
requests>=2.32,<3
pandas>=3.0.6,<4
pyarrow>=26,<27
```

## 💡 Conceitos aplicados

Este projeto permite demonstrar conhecimentos práticos em:

- Engenharia de Dados.
- Processos ETL.
- Integração e consumo de APIs REST.
- Manipulação de dados com Pandas.
- Modelagem e consultas SQL.
- Banco de dados SQLite.
- Tratamento de dados ausentes.
- Padronização e transformação de dados.
- Deduplicação de registros.
- Engenharia de atributos (*Feature Engineering*).
- Auditoria e qualidade de dados (*Data Quality*).
- Tratamento de exceções.
- Rate Limiting e Retry.
- Armazenamento em CSV e Parquet.
- Organização modular de aplicações Python.

## 📌 Considerações finais

Este projeto foi desenvolvido como parte de um processo de aprendizado prático em Python e Engenharia de Dados, buscando aplicar conceitos utilizados em pipelines de processamento e integração de dados.

A proposta é demonstrar não apenas a extração de informações de diferentes fontes, mas também a importância da validação, transformação, qualidade e organização dos dados antes de sua disponibilização para análises.

---

**Desenvolvido com Python | Projeto de Engenharia de Dados**