import requests
import json
import time
import os
from collections import Counter

"""
O código pega um arquivo json com os hashes de blocos a serem analisados e salva todas as transações desses 
hashes em um arquivo json, em lotes
"""

def extrai_transacoes(start_index, end_index):
    block_hashes_file = r".\dados_extraidos\block_hashes.json"
    output_file = r".\dados_extraidos\transactions.json"
    try:
        with open(block_hashes_file, "r", encoding="utf-8") as f:
            block_hashes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar hashes de bloco: {e}")
        return

    if start_index<0 or start_index>=len(block_hashes):
        print(f"Erro: start_index fora do intervalo válido.")
        return
    if end_index>len(block_hashes):
        end_index = len(block_hashes)
        print(f"end_index ajustado para {len(block_hashes)}.")

    hashes_to_process = block_hashes[start_index:end_index]
    n_hashes = len(hashes_to_process)
    
    def load_txs(filename):
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"Carregadas {len(data)} transações existentes de '{filename}'.")
                    return data
            except json.JSONDecodeError:
                print(f"Arquivo '{filename}' corrompido ou vazio (inicia em lista vazia)")
                return []
        return []

    transactions = load_txs(output_file)
    count = len(transactions)
    cont_tx = 0 

    print(f"Processando {n_hashes} hashes de bloco do índice {start_index} ao {end_index - 1}:")

    for i, h in enumerate(hashes_to_process, 1):
        url = f"https://blockchain.info/rawblock/{h}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            block_data = response.json()
            txs = block_data.get('tx', [])
            for tx in txs:
                cont_tx += 1 
                transactions.append(tx)
                count+=1
            print(f"Hash {i}/{n_hashes} processado. Transações salvas (lote): {cont_tx}", end='\r')
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"\nErro ao buscar bloco {h}: {e}")
        except json.JSONDecodeError:
            print(f"\nErro ao decodificar JSON do bloco {h}.")
        except Exception as e:
            print(f"\nErro inesperado no bloco {h}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=4)
    print(f"Total de transações salvas em '{output_file}': {count}")

    print()
    print(f"Total de transações analisadas nesse lote: {cont_tx}")

extrai_transacoes(0, 10) #para ajustar as transações do lote 