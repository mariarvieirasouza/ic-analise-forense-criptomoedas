import json
import ijson
from collections import Counter

"""
O código pega vários arquivos json com as informações de transações e analisa se cada transação é 
joinmarket ou wasabi e, caso seja, salva apenas as transações que são desses serviços nos respectivos 
arquivos json. Ele roda todas as transações de uma vez, então pode ser mais lento.
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

wasabi_transactions = []
joinmarket_transactions = []
files = [
    r".\dados_extraidos\transactions_0_1500_2025.json",
    r".\dados_extraidos\transactions_1500_3000_2025.json",
    r".\dados_extraidos\transactions_3000_4542_2025.json"
]

for filename in files:
    try:
        with open(filename, "rb") as f:
            transactions = ijson.items(f, 'item')
            for transaction in transactions:
                if wasabi(transaction):
                    wasabi_transactions.append(transaction)
                elif joinmarket(transaction):
                    joinmarket_transactions.append(transaction)
    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except Exception as e:
        print("Erro:", e)

with open(r".\dados_extraidos\wasabi_transactions.json", "w") as f:
    json.dump(wasabi_transactions, f, indent=4)

with open(r".\dados_extraidos\joinmarket_transactions.json", "w") as f:
    json.dump(joinmarket_transactions, f, indent=4)

print("Wasabi:")
print(len(wasabi_transactions))
print("JoinMarket:")
print(len(joinmarket_transactions))
