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

