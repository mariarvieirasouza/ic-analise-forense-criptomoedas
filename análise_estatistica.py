import ijson
import datetime
import csv
from collections import defaultdict

"""
O código faz uma análise sobre todas as transações extraídas de um arquivo json e salva em um csv para cada dia:
1- O número de transações no dia
2- O valor mixado em Bitcoin (média por transação e total)
3- Média do número de endereços de entrada por transação
4- Média do número de endereços de saída por transação
5- Média do número de endereços reutilizados dentro de cada transação
6- Média do número de endereços reutilizados dentro do período analisado
Além de salvar esses dados por dia no csv, ele imprime as médias por mês.
"""

def analise_estatistica(arquivo_entrada, arquivo_saida):
    def new_dict():
      return {
          'count': 0,
          'btc_total': 0,
          'in_total': 0,
          'out_total': 0,
          'reused_global': 0,
          'reused': 0
      }
    status = defaultdict(new_dict)
    
    seen_addresses = set()
        
    try:
        with open(arquivo_entrada, "rb") as f:
            transactions = ijson.items(f, 'item')
            
            for tx in transactions:
                timestamp = tx.get("time")
                if timestamp is None: continue
                dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
                date_str = dt.strftime("%Y-%m-%d")
                inputs = tx.get('inputs', [])
                outputs = tx.get('out', []) 
                tx_addresses = []
                for i in inputs:
                    addr = i.get('prev_out', {}).get('addr')
                    if addr: 
                        tx_addresses.append(addr)
                val_satoshi_tx = 0
                for o in outputs:
                    addr = o.get('addr')
                    if addr: 
                        tx_addresses.append(addr)
                    val_satoshi_tx += o.get('value', 0)
                
                reuso_interno = len(tx_addresses) - len(set(tx_addresses))
                unique_tx_addrs = set(tx_addresses)
                reuso_global = sum(1 for a in unique_tx_addrs if a in seen_addresses)
                seen_addresses.update(unique_tx_addrs)
                
                val_btc = val_satoshi_tx / 100_000_000.0
                
                s = status[date_str]
                s['count'] += 1
                s['btc_total'] += val_btc
                s['in_total'] += len(inputs)
                s['out_total'] += len(outputs)
                s['reused_global'] += reuso_global
                s['reused'] += reuso_interno
                s['day'] = dt.day
                s['month'] = dt.month
                s['year_month'] = dt.strftime("%Y-%m")

        headers = [
            "dia", "mês", "data", "mixer", "n_transacoes", 
            "media_btc_tx", "total_btc_dia", "media_in_tx", 
            "media_out_tx", "media_reuso_global_tx", "media_reuso_interno_tx"
        ]
        
        month_data = defaultdict(list)
        
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f_csv:
            writer = csv.writer(f_csv)
            writer.writerow(headers)
            
            for aux in sorted(status.keys()):
                n = status[aux]['count']
                m_btc = status[aux]['btc_total']/n
                m_in = status[aux]['in_total']/n
                m_out = status[aux]['out_total']/n
                m_glob = status[aux]['reused_global']/n
                m_int = status[aux]['reused']/n
                
                writer.writerow([
                    status[aux]['day'], status[aux]['month'], aux, "Wasabi", n,
                    f"{m_btc:.8f}", f"{status[aux]['btc_total']:.8f}", 
                    f"{m_in:.2f}", f"{m_out:.2f}", f"{m_glob:.2f}", f"{m_int:.2f}"
                ])
                
                month_data[status[aux]['year_month']].append({'n': n, 'btc': m_btc, 'in': m_in, 'out': m_out, 'glob': m_glob, 'int': m_int})

        print("Resumo das estatísticas:")
        print()
        total_days = 0
        sum_n = 0
        sum_btc = 0 
        sum_in = 0
        sum_out = 0
        sum_glob = 0
        sum_int = 0
        for month in sorted(month_data.keys()):
            days = month_data[month]
            n_days = len(days)
            m_n = sum(d['n'] for d in days)/n_days
            m_btc = sum(d['btc'] for d in days)/n_days
            m_in = sum(d['in'] for d in days)/n_days
            m_out = sum(d['out'] for d in days)/n_days
            m_glob = sum(d['glob'] for d in days)/n_days
            m_int = sum(d['int'] for d in days)/n_days
      
            print(f"MÊS: {month}")
            print(f"Média Transações/Dia: {m_n}")
            print(f"Média BTC Mixado/TX:  {m_btc}")
            print(f"Média Endereços IN/TX: {m_in}")
            print(f"Média Endereços OUT/TX: {m_out}")
            print(f"Média Reuso Global/TX: {m_glob}")
            print(f"Média Reuso Interno/TX: {m_int}")
            print("-" * 30)

            total_days += n_days
            sum_n += m_n
            sum_btc += m_btc
            sum_in += m_in
            sum_out += m_out
            sum_glob += m_glob
            sum_int += m_int
    except Exception as e:
        print(f"Erro: {e}")

print("Análise Wasabi:")
arquivo =  r".\dados_extraidos\wasabi_all_transactions.json"
analise_estatistica(arquivo, r".\dados_extraidos\analise_wasabi_completa.csv")
print()
print("Análise Joinmarket:")
arquivo =  r".\dados_extraidos\joinmarket_all_transactions.json"
analise_estatistica(arquivo, r".\dados_extraidos\analise_joinmarket_completa.csv")