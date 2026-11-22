
import pandas as pd
from Consumo_Api import consutar_cep


# Função Principal
def main():

    cep = input('Digite o CEP: ')
    try:
        endereco = consutar_cep(cep)
       
        if endereco is None:
            print('CEP não encontrado')
        else:
                      
              df = pd.DataFrame([endereco])

              print(df)
    except Exception as erro:
        print(f'Erro encontrado:{erro}')

main()


