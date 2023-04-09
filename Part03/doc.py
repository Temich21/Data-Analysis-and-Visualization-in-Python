import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

df = pd.read_pickle("accidents.pkl.gz")
df = df[df['p13a'] > 0]

# FIG
df_cnt = df.groupby(['region'])['p13a'].count().reset_index()
sns.set(rc={'figure.figsize': (11.7, 8.27)})
sns.set_palette("bright")
sns.set_style("whitegrid", {"grid.color": ".6", "grid.linestyle": "-"})
sns.barplot(data=df_cnt, x='region', y='p13a')
plt.title('Množství srmti v jednotlivých regionech', fontsize=20)
plt.xlabel('Region', fontsize=16)
plt.ylabel('Množství', fontsize=16)
plt.tick_params(axis='both', which='major', labelsize=14)
plt.savefig('fig.png')

# Table
df_table = df.copy()
df_table['p2a'] = pd.to_datetime(df_table['p2a'])
df_table['p2a'] = df_table['p2a'].dt.strftime('%Y')
regions = df_table['region'].unique()
years = df_table['p2a'].unique()

df_table = df_table.groupby(['region', 'p2a'])['p13a'].count()

df_table_new = pd.DataFrame()
for year in years:
    df_table_temporary = pd.DataFrame()
    df_table_temporary.insert(0, year, [])
    for region in regions:
        df_table_temporary = pd.concat([df_table_temporary, pd.DataFrame(
            [df_table.loc[region, year]], columns=[year], index=[region])])
    df_table_new = pd.concat([df_table_new, df_table_temporary], axis=1)

df_table_new = df_table_new.astype('int64')

table = [[''] + df_table_new.columns.values.tolist()] + \
    df_table_new.reset_index().values.tolist()

filename = 'tab.txt'
with open(filename, 'w') as file_object:
    file_object.write(tabulate(table))

# Vypočitané hodnoty
df_p12 = df.groupby('p12')['p1'].count().reset_index().rename(
    columns={'p12': 'Hlavní příčina nehody', 'p1': 'Počet'})
df_p12 = df_p12[df_p12['Počet'] > 150]


def _section_dividing_(num):
    if num == 100:
        return '100'  # 'nezaviněná řidičem'
    elif num >= 201 and num <= 209:
        return '201-209'  # 'nepřiměřená rychlost jízdy'
    elif num >= 301 and num <= 311:
        return '301-311'  # 'nesprávné předjíždění'
    elif num >= 401 and num <= 414:
        return '401-414'  # 'nedání přednosti v jízdě'
    elif num >= 501 and num <= 516:
        return '501-516'  # 'nesprávný způsob jízdy'
    else:
        return '601-615'  # 'technická závada vozidla'


df['p12_group'] = df['p12'].apply(_section_dividing_)
df_p12_group = df.groupby('p12_group')['p1'].count().reset_index().rename(
    columns={'p12_group': 'Hlavní příčina nehody', 'p1': 'Počet'})
number_group_1 = df_p12_group.loc[df_p12_group['Hlavní příčina nehody']
                                  == "501-516"]['Počet']
number_group_2 = df_p12_group.loc[df_p12_group['Hlavní příčina nehody']
                                  == "201-209"]['Počet']

print(f"Za dobu 2016-2021 celkem zamřelo: {df['p13a'].sum()} lidi")
print(
    f"v Středočeském kraju maximalně zamřelo: {df_table_new.loc['STC'].max()} lidi")
print(f"V roce 2021 zamřelo: {df_table_new['2021'].sum()} lidi")
print(
    f"Menši o průměru: {df_table_new.sum().mean() - df_table_new['2021'].sum()}")
print(
    f"Dle přičiny 205 zamřelo: {df_p12.loc[df_p12['Hlavní příčina nehody'] == 205]['Počet'].max()} lidi")
print(
    f"Dle přičiny 205 zamřelo: {df_p12.loc[df_p12['Hlavní příčina nehody'] == 501]['Počet'].max()} lidi")
print(
    f"Dle přičiny 205 zamřelo: {df_p12.loc[df_p12['Hlavní příčina nehody'] == 508]['Počet'].max()} lidi")
print(
    f"Dle přičiny 205 zamřelo: {df_p12.loc[df_p12['Hlavní příčina nehody'] == 204]['Počet'].max()} lidi")
print(
    f"V skupině dle nesprávného způsobu jízdy celkem zamřelo: {number_group_1.max()} lidi")
print(
    f"V skupině dle nepřiměřené rychlosti jízdy celkem zamřelo: {number_group_2.max()} lidi")
