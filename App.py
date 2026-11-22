
import pandas as pd
from Consumo_Api import consutar_cep
from Transformacao import tratamento
from Consumo_Api import consutar_cep, coordenadas,clima

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
              print(df)
    except Exception as erro:
        print(f'Erro encontrado:{erro}')

main()


