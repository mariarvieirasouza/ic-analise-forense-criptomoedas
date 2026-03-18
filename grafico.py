import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter, MonthLocator
import locale

"""
O código lê um arquivo CSV contendo a contagem diária de transações de cada mixer e gera um gráfico de linhas comparativo 
que demonstra a evolução da quantidade de transações por mixer (Joinmarket e Wasabi) ao longo de um período específico.
"""

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')


arquivo = r'.\dados_extraidos\transacoes_por_dia.csv'

try:
    df = pd.read_csv(arquivo, usecols=[1, 2, 3, 4]) 
except FileNotFoundError:
    print(f"ERRO: Arquivo '{arquivo}' não encontrado.")
    exit()

df.columns = ['Mes', 'Data', 'Mixer', 'Quantidade']
df['Data'] = pd.to_datetime(df['Data'])
df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
df.dropna(subset=['Quantidade'], inplace=True)


plt.figure(figsize=(14, 6))

sns.lineplot(
    data=df,
    x='Data',
    y='Quantidade',
    hue='Mixer',
    linewidth=2,
)

plt.xlabel('Data', fontsize=12)
plt.ylabel('Quantidade de Transações', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

plt.xlim(
    left=pd.to_datetime('2024-12-15'), 
    right=pd.to_datetime('2025-07-15') 
)

ax = plt.gca()

ax.xaxis.set_major_locator(MonthLocator(bymonth=range(1, 8), bymonthday=1)) 

formatter = DateFormatter('%b %Y')
ax.xaxis.set_major_formatter(formatter)

tick_labels = [formatter.format_data(tick) for tick in ax.get_xticks()]

if len(tick_labels) > 6:
    ax.set_xticklabels(tick_labels[:-1])
    
plt.xticks(rotation=45, ha='right')

plt.tight_layout()
plt.show()