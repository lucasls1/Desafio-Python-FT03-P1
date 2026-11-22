import sqlite3 as sql
from typing import Any
import pandas as pd
conn = sql.connect(':memory:')
conn.row_factory = sql.Row

cursor = conn.cursor()

def tratamento(dados:dict[str,Any],dados_clima:dict[str,Any],df_previsao:pd.DataFrame):
    valores = (
        dados['cep'],
        dados['logradouro'],
        dados['bairro'],
        dados['localidade'],
        dados['estado'],
        dados['regiao'],
        dados['uf'],
        dados['ddd']
    )
    
    valoresPrevisao = []
    registro_previsao = df_previsao.to_dict(orient='records')
    for registros in registro_previsao:
       valoresPrevisao.append((
           dados['cep'],
           dados_clima['current']['temperature_2m'],
           registros['data'],
           registros['temperatura_minima'],
           registros['temperatura_maxima']
       ))
    

    try:
        cursor.execute(
            'CREATE TABLE endereco(cep TEXT PRIMARY KEY, logradouro TEXT,bairro TEXT,localidade TEXT,estado TEXT,regiao TEXT,uf TEXT,ddd INTEGER)'
        
        )
        cursor.execute(
            'CREATE TABLE previsao(cep TEXT,temperatura TEXT,data TEXT,temperatura_minima REAL,temperatura_maxima REAL,PRIMARY KEY(cep,data))'
        )
        cursor.execute(
            'INSERT INTO endereco(cep, logradouro,bairro,localidade,estado,regiao,uf,ddd) VALUES(?,?,?,?,?,?,?,?)',valores
        )
        cursor.executemany(
            'INSERT INTO previsao(cep,temperatura,data,temperatura_minima,temperatura_maxima) VALUES(?,?,?,?,?)',valoresPrevisao
        )

        linhas = conn.execute(
            'select * from endereco as e inner join previsao as p ON e.cep = p.cep '
        ).fetchall()

        return [dict(linha) for linha in linhas]
    finally:
        ...
