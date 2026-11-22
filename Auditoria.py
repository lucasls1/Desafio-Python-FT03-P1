import pandas as pd

def auditar_dados(df: pd.DataFrame):

    auditoria = []

    # Verifica valores nulos
    nulos = df.isnull().sum()

    for coluna, quantidade in nulos.items():
        auditoria.append({
            'verificacao': 'Completude',
            'coluna': coluna,
            'problemas_encontrados': quantidade,
            'status': 'APROVADO' if quantidade == 0 else 'REPROVADO'
        })

    return pd.DataFrame(auditoria)