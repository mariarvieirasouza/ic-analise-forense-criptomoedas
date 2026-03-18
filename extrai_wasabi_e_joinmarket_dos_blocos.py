import requests
import json
import time
import os
from collections import Counter

"""
O código pega um arquivo json com os hashes de blocos a serem analisados e analisa, em lotes, se cada transação do 
bloco é joinmarket ou wasabi e, caso seja, salva apenas as transações que são desses serviços nos respectivos 
arquivos json
"""

def joinmarket(transaction): #identifica joinmarket
    outputs = transaction.get('out', [])
    inputs = transaction.get('inputs', [])
    #numero de scripts distintos
    input_scripts = set()
    for inp in inputs:
        if 'prev_out' in inp:
            input_scripts.add(inp['prev_out'].get('script', ''))
    values = []
    for o in outputs:
        values.append(o.get('value', 0))
    value_cont = Counter(values)
    n = max(value_cont.values()) if value_cont else 0 #numero maximo de saidas com mesmo valor

    if not (n >= len(outputs) / 2): #n >= metade do numero de saidas
        return False
    if not (n >= 3 and n <= len(input_scripts)): #n >= 3 e n <= número de scripts de entrada distintos
        return False
    return True

def wasabi(transaction): #identifica wasabi 2.0 
    outputs = transaction.get('out', [])
    inputs = transaction.get('inputs', [])
    output_addrs = []
    for o in outputs:
        output_addrs.append(o.get('addr', ''))
    #enderecos de saida comecam com bc1
    count_bc1 = 0
    for addr in output_addrs:
        if addr and addr.startswith('bc1'):
            count_bc1 += 1
    if not (count_bc1 >= len(output_addrs)):
        return False
    #numero de saidas = numero de scripts distintos
    output_scripts = set()
    for out in outputs:
        output_scripts.add(out.get('script', ''))
    if len(outputs) != len(output_scripts):
        return False
    #todos os valores maiores que 0
    values = []
    for o in outputs:
        values.append(o.get('value', 0))
    for v in values:
        if v <= 0:
            return False
    #n é o numero de participantes 
    value_cont = Counter(values)
    n = max(value_cont.values()) if value_cont else 0
    #minimo de 3 participantes
    if n < 3:
        return False
    #numero de trocos (saidas que aparecem uma vez) <= numero de participantes
    change_cont = 0
    for val, i in value_cont.items():
        if i == 1:
            change_cont += 1
    if change_cont >= n:
        return False
    #numero de entradas >= numero de participantes
    if transaction.get('vin_sz', 0) < n:
        return False
    return True

def wasabi_10_e_11(transaction): #identifica wasabi 1.0 e 1.1
    values = []
    for o in transaction.get('out', []):
        valor = o.get('value', 0)
        values.append(valor)
    if not values: 
        return False
    value_cont = Counter(values)
    most_freq_val, freq_count = value_cont.most_common(1)[0]
    most_freq_btc = most_freq_val / 100000000 #converte para btc
    if freq_count < 10: return False #minimo 10 saídas iguais
    if not (0.08 <= most_freq_btc <= 0.12): return False #denominação próxima de 0.1 btc
    unique_vals = []
    for v, count in value_cont.items():
        if count == 1:
            unique_vals.append(v)
    if len(value_cont) < 3 or len(unique_vals) < 1: #minimo 3 valores distintos e um único
        return False
    if transaction.get('vin_sz', 0) < freq_count: 
        return False #inputs >= frequência da denominação
    return True

def extrai_wasabi_e_joinmarket(start_index, end_index):
    block_hashes_file = r".\dados_extraidos\block_hashes.json"
    wasabi_output_file = r".\dados_extraidos\wasabi.json"
    joinmarket_output_file = r".\dados_extraidos\joinmarket.json"
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

    wasabi_transactions = load_txs(wasabi_output_file)
    joinmarket_transactions = load_txs(joinmarket_output_file)
    
    wasabi_count = len(wasabi_transactions)
    joinmarket_count = len(joinmarket_transactions)
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
                if wasabi(tx):
                    wasabi_transactions.append(tx)
                    wasabi_count += 1 
                elif joinmarket(tx):
                    joinmarket_transactions.append(tx)
                    joinmarket_count += 1 
            
            print(f"Hash {i}/{n_hashes} processado. Transações analisadas (lote): {cont_tx} | Wasabi (total): {wasabi_count} | JoinMarket (total): {joinmarket_count}", end='\r')
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"\nErro ao buscar bloco {h}: {e}")
        except json.JSONDecodeError:
            print(f"\nErro ao decodificar JSON do bloco {h}.")
        except Exception as e:
            print(f"\nErro inesperado no bloco {h}: {e}")

    with open(wasabi_output_file, "w", encoding="utf-8") as f:
        json.dump(wasabi_transactions, f, ensure_ascii=False, indent=4)
    print(f"Total de transações Wasabi salvas em '{wasabi_output_file}': {wasabi_count}")
    with open(joinmarket_output_file, "w", encoding="utf-8") as f:
        json.dump(joinmarket_transactions, f, ensure_ascii=False, indent=4)
    print(f"Total de transações JoinMarket salvas em '{joinmarket_output_file}': {joinmarket_count}")

    print()
    print(f"Total de transações analisadas nesse lote: {cont_tx}")
    print(f"Total acumulado de Wasabi: {wasabi_count}")
    print(f"Total acumulado de JoinMarket: {joinmarket_count}")

extrai_wasabi_e_joinmarket(0, 1500) #alterar os índices para mudar o lote