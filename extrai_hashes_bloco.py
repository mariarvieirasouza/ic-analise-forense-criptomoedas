import requests
import json
import datetime
import time

"""
O código salva em um arquivo json todos os hashes dos blocos em determinado intervalo de tempo
"""

def get_unix_timestamp(year, month, day):
    date = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
    return int(date.timestamp()) * 1000

block_hashes = []

for day in range(1, 31): #pega os dias 1 até n-1
    date = get_unix_timestamp(2019, 6, day)
    #url no formato https://blockchain.info/blocks/$time_in_milliseconds?format=json -> busca dados de todos os blocos de um dia específico
    url = "https://blockchain.info/blocks/{}?format=json".format(date)
    try:
        response = requests.get(url)
        response.raise_for_status()
        blocks_data = response.json()

        if isinstance(blocks_data, list):
            for block in blocks_data:
                hash_val = block.get('hash')
                if hash_val:
                    block_hashes.append(hash_val)
        print(day)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar à API no dia {day}: {e}")
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON no dia {day}.")
    except Exception as e:
        print(f"Erro inesperado no dia {day}: {e}")

output_filename = r".\dados_extraidos\block_hashes.json"

with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(block_hashes, f, ensure_ascii=False, indent=4)

print(f"Total de hashes de bloco coletados: {len(block_hashes)}")