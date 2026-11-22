
import math
import sqlite3
from pathlib import Path

import pandas as pd
import requests

from Transformacao_sql import tratamento
from Consumo_Api import consutar_cep, coordenadas, clima
from Auditoria import auditar_dados
from Transformacoes import (
    padronizar_dados,
    tratar_nulos,
    remover_duplicados,
    enriquecer_metricas
)


# 1. VALIDAÇÃO DA ENTRADA

def validar_cep(cep: str) -> str:
    """Valida e normaliza o CEP informado pelo usuário."""

    cep = cep.strip().replace('-', '')

    if not cep:
        raise ValueError('Você precisa informar um CEP.')

    if not cep.isascii() or not cep.isdigit():
        raise ValueError('O CEP deve conter apenas números de 0 a 9.')

    if len(cep) != 8:
        raise ValueError('O CEP deve possuir exatamente 8 dígitos.')

    return cep



# VALIDAÇÃO DA RESPOSTA DO VIACEP


def validar_endereco(endereco: dict) -> None:
    """Verifica se a resposta do ViaCEP é válida."""

    if endereco is None:
        raise ValueError('Não foi possível obter os dados do CEP.')

    if not isinstance(endereco, dict):
        raise TypeError('A resposta do ViaCEP possui formato inválido.')

    if endereco.get('erro'):
        raise ValueError('CEP não encontrado.')

    campos_obrigatorios = ['localidade', 'uf']

    for campo in campos_obrigatorios:
        if not endereco.get(campo):
            raise ValueError(
                f'A resposta do ViaCEP não contém o campo {campo}.'
            )


# 3. VALIDAÇÃO DAS COORDENADAS

def validar_coordenadas(local: dict) -> tuple[float, float]:
    """Valida latitude e longitude retornadas pela geocodificação."""

    if local is None:
        raise ValueError('Não foi possível localizar as coordenadas.')

    if not isinstance(local, dict):
        raise TypeError('A resposta da geocodificação é inválida.')

    if 'latitude' not in local or 'longitude' not in local:
        raise ValueError('Latitude ou longitude não foram encontradas.')

    try:
        latitude = float(local['latitude'])
        longitude = float(local['longitude'])
    except (TypeError, ValueError) as erro:
        raise ValueError('As coordenadas não são numéricas.') from erro

    if not math.isfinite(latitude) or not math.isfinite(longitude):
        raise ValueError('As coordenadas precisam ser valores finitos.')

    if not -90 <= latitude <= 90:
        raise ValueError('Latitude fora do intervalo permitido.')

    if not -180 <= longitude <= 180:
        raise ValueError('Longitude fora do intervalo permitido.')

    return latitude, longitude



#  VALIDAÇÃO DA RESPOSTA DA API DE CLIMA


def validar_clima(resposta: dict) -> dict:
    """Verifica se a resposta da API de clima contém os dados necessários."""

    if resposta is None:
        raise ValueError('A API de clima não retornou dados.')

    if not isinstance(resposta, dict):
        raise TypeError('A resposta da API de clima possui formato inválido.')

    if not isinstance(resposta.get('current'), dict):
        raise ValueError('Dados atuais do clima não encontrados.')

    if 'temperature_2m' not in resposta['current']:
        raise ValueError('Temperatura atual não encontrada na resposta.')

    if not isinstance(resposta.get('daily'), dict):
        raise ValueError('Dados da previsão diária não encontrados.')

    previsao = resposta['daily']

    campos_obrigatorios = [
        'time',
        'temperature_2m_min',
        'temperature_2m_max'
    ]

    for campo in campos_obrigatorios:
        if campo not in previsao:
            raise ValueError(
                f'A previsão diária não contém o campo {campo}.'
            )

    tamanhos = [
        len(previsao[campo])
        for campo in campos_obrigatorios
    ]

    if len(set(tamanhos)) != 1:
        raise ValueError(
            'As listas da previsão diária possuem tamanhos diferentes.'
        )

    if tamanhos[0] == 0:
        raise ValueError('A API não retornou previsões diárias.')

    return previsao


# VALIDAÇÃO DO DATAFRAME


def validar_dataframe(df: pd.DataFrame) -> None:
    """Verifica a estrutura básica do DataFrame."""

    if df is None or df.empty:
        raise ValueError('O processamento não gerou registros.')

    if not isinstance(df, pd.DataFrame):
        raise TypeError('O resultado do processamento não é um DataFrame.')

    colunas_obrigatorias = [
        'cep',
        'data',
        'temperatura',
        'temperatura_minima',
        'temperatura_maxima'
    ]

    for coluna in colunas_obrigatorias:
        if coluna not in df.columns:
            raise ValueError(
                f'A coluna obrigatória {coluna} não foi encontrada.'
            )



# FUNÇÃO PRINCIPAL


def main():

    print('\n===== PROCESSAMENTO DE DADOS CLIMÁTICOS =====')


    # Entrada e validação do CEP
   

    try:
        cep = input('Digite o CEP: ')
        cep = validar_cep(cep)

    except ValueError as erro:
        print(f'Erro na entrada: {erro}')
        return

  
    # Consulta ao ViaCEP


    try:
        print('\nConsultando endereço...')

        endereco = consutar_cep(cep)

        validar_endereco(endereco)

        print('Endereço localizado com sucesso!')

    except requests.exceptions.RequestException as erro:
        print(f'Erro de comunicação com o ViaCEP: {erro}')
        return

    except (ValueError, TypeError) as erro:
        print(f'Erro na validação do endereço: {erro}')
        return


    # Consulta e validação das coordenadas


    try:
        print('\nConsultando coordenadas...')

        local = coordenadas(
            endereco['localidade'],
            endereco['uf']
        )

        latitude, longitude = validar_coordenadas(local)

        print('Coordenadas localizadas com sucesso!')

    except requests.exceptions.RequestException as erro:
        print(f'Erro de comunicação na geocodificação: {erro}')
        return

    except (ValueError, TypeError) as erro:
        print(f'Erro na validação das coordenadas: {erro}')
        return

   
    #  Consulta e validação do clima
    

    try:
        print('\nConsultando previsão do clima...')

        resClima = clima(latitude, longitude)

        previsao = validar_clima(resClima)

        df_previsao = pd.DataFrame({
            'data': previsao['time'],
            'temperatura_minima': previsao['temperature_2m_min'],
            'temperatura_maxima': previsao['temperature_2m_max']
        })

        print('Previsão do clima recebida com sucesso!')

    except requests.exceptions.RequestException as erro:
        print(f'Erro de comunicação com a API de clima: {erro}')
        return

    except (ValueError, TypeError, KeyError) as erro:
        print(f'Erro na validação dos dados climáticos: {erro}')
        return

   
    # Persistência e consulta SQLite
   

    try:
        print('\nProcessando dados no SQLite...')

        res = tratamento(
            endereco,
            resClima,
            df_previsao
        )

        if not res:
            raise ValueError(
                'O banco de dados não retornou registros.'
            )

        df = pd.DataFrame(res)

        validar_dataframe(df)

        print('Processamento SQLite concluído!')

    except sqlite3.Error as erro:
        print(f'Erro no banco de dados SQLite: {erro}')
        return

    except (ValueError, TypeError, KeyError) as erro:
        print(f'Erro no processamento dos dados: {erro}')
        return


    #  Transformações dos dados
    

    try:
        print('\nExecutando transformações...')

        df = padronizar_dados(df)
        validar_dataframe(df)

        df = tratar_nulos(df)
        validar_dataframe(df)

        df = remover_duplicados(df)
        validar_dataframe(df)

        df = enriquecer_metricas(df)
        validar_dataframe(df)

        df['data'] = pd.to_datetime(
            df['data'],
            errors='raise'
        )

        df['ano'] = df['data'].dt.year
        df['mes'] = df['data'].dt.month

        print('Transformações concluídas!')

    except (ValueError, TypeError, KeyError) as erro:
        print(f'Erro nas transformações: {erro}')
        return

    except (pd.errors.ParserError, pd.errors.OutOfBoundsDatetime) as erro:
        print(f'Erro no processamento dos dados: {erro}')
        return

    
    #  Auditoria da qualidade dos dados
    

    try:
        print('\nExecutando auditoria de qualidade...')

        df_auditoria = auditar_dados(df)

        if not isinstance(df_auditoria, pd.DataFrame):
            raise TypeError(
                'A auditoria não retornou um DataFrame.'
            )

        if df_auditoria.empty:
            raise ValueError(
                'A auditoria não gerou resultados.'
            )

        print('Auditoria concluída!')

    except (ValueError, TypeError, KeyError) as erro:
        print(f'Erro na auditoria: {erro}')
        return

  
    #  Exportação dos arquivos
 

    try:
        print('\nExportando arquivos...')

        # Cria uma pasta para os resultados
        pasta_saida = Path('resultados')
        pasta_saida.mkdir(parents=True, exist_ok=True)

        # Exportação Parquet
        df.to_parquet(
            pasta_saida / 'dados_parquet',
            engine='pyarrow',
            compression='snappy',
            index=False,
            partition_cols=['ano', 'mes']
        )

        # Exportação da auditoria
        df_auditoria.to_csv(
            pasta_saida / 'auditoria_qualidade.csv',
            index=False,
            encoding='utf-8-sig'
        )

        # Cópia para apresentação dos dados em CSV
        df_csv = df.copy()

        colunas_temperatura = [
            'temperatura',
            'temperatura_minima',
            'temperatura_maxima',
            'amplitude_termica',
            'temperatura_media_estimada'
        ]

        for coluna in colunas_temperatura:

            if coluna not in df_csv.columns:
                raise ValueError(
                    f'Coluna {coluna} não encontrada para exportação.'
                )

            valores = pd.to_numeric(
                df_csv[coluna],
                errors='coerce'
            )

            df_csv[coluna] = valores.map(
                lambda valor: (
                    f'{valor:.2f} °C'
                    if pd.notna(valor)
                    else ''
                )
            )

        df_csv.to_csv(
            pasta_saida / 'Previsao_clima_por_cep.csv',
            index=False,
            encoding='utf-8-sig'
        )

        print('\nArquivos exportados com sucesso!')

    except ImportError as erro:
        print(
            f'Erro de dependência na exportação: {erro}. '
            'Verifique se o PyArrow está instalado.'
        )
        return

    except (OSError, ValueError, KeyError) as erro:
        print(f'Erro na exportação dos arquivos: {erro}')
        return

    except Exception as erro:
        print(f'Erro inesperado durante a exportação: {erro}')
        return


    # FINALIZAÇÃO
  

    print('\n===== PROCESSAMENTO FINALIZADO =====')
    print(f'CEP processado: {cep}')
    print(f'Registros gerados: {len(df)}')
    print(f'Arquivos salvos em: {pasta_saida.resolve()}')


if __name__ == '__main__':
    main()
