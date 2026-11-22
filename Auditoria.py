import pandas as pd
# Função para auditar a qualidade dos dados.
def auditar_dados(df: pd.DataFrame):

    auditoria = []
    schema_esperado = {
    'cep': 'object',
    'logradouro': 'object',
    'localidade': 'object',
    'data': 'datetime64[ns]',
    'temperatura_minima': 'float64',
    'temperatura_maxima': 'float64'
    }
    # Validação de Schema
    for esperado in schema_esperado:
        if esperado in df.columns:
            tipo_esperado = schema_esperado[esperado]
            tipo_real = str(df[esperado].dtype)
             
        else:
            auditoria.append({
                        'verificacao': 'Schema',
                        'coluna': esperado,
                        'problemas_encontrados': 1,
                        'status': 'REPROVADO'
                    })

           

        if tipo_esperado == tipo_real:
            auditoria.append({
                'verificacao': 'Schema',
                'coluna': esperado,
                'problemas_encontrados': 0,
                'status': 'APROVADO'
            })
        else:
             auditoria.append({
                'verificacao': 'Schema',
                'coluna': esperado,
                'problemas_encontrados': 1,
                'status': 'REPROVADO'
            })
    # Validação de Nulos
    nulos = df.isnull().sum()
    total_registros =len(df)
    for coluna, quantidade in nulos.items():
        null_ratio = quantidade/ total_registros if total_registros > 0 else 0
        auditoria.append({
            'verificacao': 'Completude',
            'coluna': coluna,
            'problemas_encontrados': quantidade,
            'null_ratio': round(null_ratio,4),
            'status': 'APROVADO' if quantidade == 0 else 'REPROVADO'
        })
    # Validação de Unicidade
    # Verifica unicidade
    duplicados = df.duplicated(subset=['cep', 'data']).sum()

    auditoria.append({
        'verificacao': 'Unicidade',
        'coluna': 'cep + data',
        'problemas_encontrados': duplicados,
        'status': 'APROVADO' if duplicados == 0 else 'REPROVADO'
    })
    # Validação da consistencia entre temperaturas (Intevalos)
    inconsistencias = (
        df['temperatura_minima'] > df['temperatura_maxima']
    ).sum()

    auditoria.append({
        'verificacao': 'Range Check',
        'coluna': 'temperatura_minima/temperatura_maxima',
        'problemas_encontrados': inconsistencias,
        'status': 'APROVADO' if inconsistencias == 0 else 'REPROVADO'
    })
    return pd.DataFrame(auditoria)