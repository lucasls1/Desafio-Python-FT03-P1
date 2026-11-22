import pandas as pd

def padronizar_dados(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Padroniza CEP
    df['cep'] = df['cep'].astype('string')

    # Padroniza data
    df['data'] = pd.to_datetime(df['data'])

    # Padroniza temperaturas
    df['temperatura_minima'] = pd.to_numeric(
        df['temperatura_minima'], errors='coerce'
    )

    df['temperatura_maxima'] = pd.to_numeric(
        df['temperatura_maxima'], errors='coerce'
    )
    return df

def tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    print('Nulos antes do tratamento:')
    print(df.isnull().sum())
    # Remove registros sem informações essenciais
    df = df.dropna(subset=['cep', 'data'])
    # Preenche campos textuais ausentes
    colunas_texto = ['logradouro', 'bairro', 'localidade', 'estado', 'regiao', 'uf']

    for coluna in colunas_texto:
        df[coluna] = df[coluna].fillna('Não informado')
        print('Nulos depois do tratamento:')
        print(df.isnull().sum())

    return df

def remover_duplicados(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    total_antes = len(df)

    df = df.drop_duplicates(
        subset=['cep', 'data'],
        keep='first'
    )

    total_depois = len(df)

    removidos = total_antes - total_depois

    print(f'Registros antes: {total_antes}')
    print(f'Registros depois: {total_depois}')
    print(f'Duplicados removidos: {removidos}')

    return df

def enriquecer_metricas(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Calcula amplitude térmica
    df['amplitude_termica'] = (
        df['temperatura_maxima'] - df['temperatura_minima']
    ).round(2)

    # Calcula temperatura média estimada
    df['temperatura_media_estimada'] = (
        df['temperatura_maxima'] + df['temperatura_minima'] / 2
    ).round(2)

    return df
