
import pandas as pd
from Transformacao import tratamento
from Consumo_Api import consutar_cep, coordenadas,clima
from Auditoria import auditar_dados

# Função Principal
def main():

    cep = input('Digite o CEP: ')
    try:
        endereco = consutar_cep(cep)
       
        if endereco is None:
            print('CEP não encontrado')
        else:
              local = coordenadas(endereco['localidade'],endereco['uf'])
              resClima = clima(local['latitude'],local['longitude'])
              previsao = resClima['daily']
              df_previsao= pd.DataFrame({
                    'data': previsao['time'],
                    'temperatura_minima': previsao['temperature_2m_min'],
                    'temperatura_maxima': previsao['temperature_2m_max']
              })
              res = tratamento(endereco,resClima,df_previsao)
              df = pd.DataFrame(res)

              df['data'] =pd.to_datetime(df['data'])
              df['ano'] = df['data'].dt.year
              df['mes'] = df['data'].dt.month

              df.to_parquet(
                'dados_parquet',
                engine='pyarrow',
                compression='snappy',
                index=False,
                partition_cols=['ano', 'mes']
)
              df_auditoria = auditar_dados(df)

              df_auditoria.to_csv(
                'auditoria_qualidade.csv',
                 index=False,
                 encoding='utf-8-sig'
                )
              
              df.to_csv('Previsap_clima_por_cep.csv',index=False, encoding='utf-8-sig')
              print(df)
    except Exception as erro:
        print(f'Erro encontrado:{erro}')

main()