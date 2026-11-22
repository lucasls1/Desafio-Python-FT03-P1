import requests
import time

sessao = requests.Session()

ultima_requisicao = 0

def controlar_intervalo(intervalo: float = 1.0):

    global ultima_requisicao

    agora = time.monotonic()

    tempo_decorrido = agora - ultima_requisicao

    if tempo_decorrido < intervalo:
        espera = intervalo - tempo_decorrido
        time.sleep(espera)

    ultima_requisicao = time.monotonic()

def fazer_requisicao(url: str, params: dict = None, tentativas: int = 3):

    for tentativa in range(1, tentativas + 1):

        try:
            controlar_intervalo()

            resposta = sessao.get(
                url,
                params=params,
                timeout=10
            )

            resposta.raise_for_status()

            return resposta.json()

        except requests.exceptions.RequestException as erro:

            status_code = getattr(
                getattr(erro, 'response', None),
                'status_code',
                None
            )

            # Erros HTTP permanentes: não repetir
            if status_code is not None:
                if status_code != 429 and not 500 <= status_code < 600:
                    print(f'Erro permanente: HTTP {status_code}')
                    raise

            print(f'Erro na tentativa {tentativa}: {erro}')

            if tentativa == tentativas:
                raise

            espera = 2 ** (tentativa - 1)
            if status_code == 429 and erro.response is not None:
                retry_after = erro.response.headers.get('Retry-After')

            if retry_after and retry_after.isdigit():
                espera = int(retry_after)
            print(f'Nova tentativa em {espera} segundos...')
            time.sleep(espera)