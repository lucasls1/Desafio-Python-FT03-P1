# Clima por CEP — etapa 1

Este primeiro passo consulta a API ViaCEP e mostra cidade e estado. Depois,
vamos usar a cidade e o estado para consultar a geocodificação e a previsão
do tempo no Open-Meteo.

## Preparar

No terminal, entre nesta pasta e instale a dependência:

```bash
python -m pip install -r requirements.txt
```

## Executar

```bash
python App.py
```

Informe um CEP de oito números, por exemplo `01001-000`. A consulta exige
conexão com a internet.

## Como as APIs são conectadas

1. ViaCEP retorna `localidade` e `uf` para o CEP.
2. Open-Meteo Geocoding converte cidade e estado em latitude e longitude.
3. Open-Meteo Forecast recebe as coordenadas e retorna a temperatura atual.

No código, `params={...}` deixa o `requests` montar os parâmetros da URL com
o formato correto.

Documentação: [ViaCEP](https://viacep.com.br/), [geocodificação Open-Meteo](https://open-meteo.com/en/docs/geocoding-api) e [previsão Open-Meteo](https://open-meteo.com/en/docs).

## Persistencia
Como funciona
A função tratamento(dados, dados_clima, df_previsao) recebe:
- dados: dicionário com informações do CEP, incluindo cep, logradouro, bairro, localidade, estado, regiao, uf e ddd.
- dados_clima: dicionário de clima que contenha current.temperature_2m.
- df_previsao: DataFrame do pandas com as colunas data, temperatura_minima e temperatura_maxima.
A função cria as tabelas endereco e previsao, insere os dados e relaciona as tabelas pelo CEP. O resultado é uma lista de dicionários, com uma linha para cada data de previsão.
Observações
- O banco é criado com :memory:; os dados existem apenas durante a execução do processo e não são salvos em arquivo.
- Como as tabelas têm chave primária fixa, uma segunda chamada à função na mesma conexão pode falhar ao tentar criá-las novamente.
- O bloco finally está vazio (...), então não executa uma limpeza adicional. Se a conexão não for mais necessária, ela pode ser fechada com conn.close().