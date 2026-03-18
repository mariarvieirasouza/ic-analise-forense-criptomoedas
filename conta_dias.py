import ijson
import datetime
from collections import defaultdict

"""
O código conta o número de transações por dia dado um arquivo json de transações
"""

def contar_transacoes_por_dia(nome_arquivo):
    transacoes_por_dia = defaultdict(int)
    transacoes_totais_lidas = 0
    transacoes_sem_time = 0

    try:
        with open(nome_arquivo, "rb") as f:
            transactions = ijson.items(f, 'item')
            for transaction in transactions:
                transacoes_totais_lidas += 1

                timestamp_segundos = transaction.get("time")
                
                if timestamp_segundos is not None:
                    try:
                        dt_object = datetime.datetime.fromtimestamp(timestamp_segundos, tz=datetime.timezone.utc)
                        data_string = dt_object.strftime("%Y-%m-%d")
                        transacoes_por_dia[data_string] += 1
                    except ValueError as ve:
                        print(f"Timestamp inválido encontrado ({timestamp_segundos}) na transação {transacoes_totais_lidas}.")
                        transacoes_sem_time += 1 
                        continue
                else:
                    transacoes_sem_time += 1
                    
        print(f"Total de transações lidas do arquivo: {transacoes_totais_lidas}")
        print(f"Transações sem 'time' (descartadas): {transacoes_sem_time}")
        
        acumula=0
        print("\n--- Transações por Dia ---")
        datas_ordenadas = sorted(transacoes_por_dia.keys())
        print("Data        | Transações")
        print("------------|-------------")
        for data in datas_ordenadas:
            contagem = transacoes_por_dia[data]
            print(f"{data} | {contagem:11}")
            acumula = acumula + contagem
        print(acumula)
    except FileNotFoundError:
        print(f"\nArquivo '{nome_arquivo}' não encontrado.")
    except ijson.common.IncompleteJSONError:
        print("\nArquivo JSON incompleto ou malformado.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")

print("Wasabi:")
arquivo =  r".\dados_extraidos\wasabi.json"
contar_transacoes_por_dia(arquivo)
print()
print("Análise Joinmarket:")
arquivo =  r".\dados_extraidos\joinmarket.json"
contar_transacoes_por_dia(arquivo)
