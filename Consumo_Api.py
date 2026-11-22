import requests as req # biblioteca de comunicação com servidores.

# função de consultar o cep na API
def consutar_cep (cep: str):

    url_api_viacep = f'https://viacep.com.br/ws/{cep}/json/'
    resposta = req.get(url_api_viacep)
    return resposta.json()

# Função que busca as coordenadas atrávez da cidade e uf que vem da api anterior
def coordenadas(cidade:str,uf:str):
     resposta = req.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": f"{cidade}, {uf}, Brazil",
            "count": 1,
            "language": "pt",
            "countryCode": "BR",
        }
     )
     res = resposta.json().get("results",[])
     return res[0] if res else None

# função para buscar dados de previsão do tempo com base nas coordenadas obtidas na função coordenadas extraindo latitude e longitude
def clima(latitude:float,longitude:float):
    resposta = req.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "daily": "temperature_2m_min,temperature_2m_max",
            "forecast_days": 7,
            "timezone": "America/Sao_Paulo",
        }
    )
    return resposta.json()