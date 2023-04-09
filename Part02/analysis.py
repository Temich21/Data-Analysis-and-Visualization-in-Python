from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from zipfile import ZipFile


# Loading data from ZIP files / Načtení dat ze ZIP souborů
def load_data(filename: str) -> pd.DataFrame:
    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    regions_values = list(regions.values())
    regions_keys = list(regions.keys())

    df = pd.DataFrame()

    with ZipFile(filename) as data:
        data.extractall('data')
        for year in data.namelist():
            with ZipFile('data/' + year) as dy:
                for csv_file in dy.namelist():
                    number = csv_file.split('.')
                    if number[0] in regions_values:
                        with dy.open(csv_file) as f:
                            df_region = pd.read_csv(
                                f, names=headers, encoding="cp1250", sep=';', low_memory=False)
                            df_region.insert(
                                0, 'region', regions_keys[regions_values.index(number[0])], True)
                            df = pd.concat([df, df_region])

    return df


# Formatting and cleaning data / Formátování a čištění dat
def parse_data(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    new_df = df.copy()

    dates = new_df['p2a']
    dates = pd.to_datetime(dates)
    new_df.insert(1, 'date', dates)

    new_df[['d', 'e']] = new_df[['d', 'e']].apply(
        lambda x: x.str.replace(',', '.'))
    new_df['d'] = pd.to_numeric(new_df.d, errors='coerce')
    new_df['e'] = pd.to_numeric(new_df.e, errors='coerce')

    new_df = new_df.drop_duplicates(subset=['p1'])

    new_df[['p2a', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p27', 'p28', 'p35', 'p36', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a',
            'p50b', 'p51', 'p52', 'p55a', 'p57', 'p58', 'k', 'o', 'p', 't', 'p5a']] = new_df[['p2a', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p27', 'p28', 'p35', 'p36', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a',
                                                                                              'p50b', 'p51', 'p52', 'p55a', 'p57', 'p58', 'k', 'o', 'p', 't', 'p5a']].astype("category")

    if verbose == True:
        old_memory = df.memory_usage(deep=True).sum() / 10**6
        new_memory = new_df.memory_usage(deep=True).sum() / 10**6
        print(f"orig_size={old_memory:.1f} MB")
        print(f"new_size={new_memory:.1f} MB")

    return new_df


# Number of accidents in individual regions according to visibility / Počty nehod v jednotlivých regionech podle viditelnosti
def plot_visibility(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):

    def _section_dividing_(num):
        if num == 1:
            return '1'
        elif num == 2 or num == 3:
            return '2 and 3'
        elif num == 4 or num == 6:
            return '4 and 6'
        elif num == 5 or num == 7:
            return '5 and 7'

    df['section'] = df['p19'].apply(_section_dividing_)

    df_p19 = df.groupby(['region', 'section'])['p19'].count().reset_index()
    df_p19 = df_p19[(df_p19['region'] == 'JHM') | (df_p19['region'] == 'OLK') | (
        df_p19['region'] == 'PAK') | (df_p19['region'] == 'KVK')]

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))

    ax = axes.flatten()

    sns.set_palette("bright")

    sns.barplot(data=df_p19[df_p19['section'] == '1'],
                x='region', y='p19', ax=ax[0]).set(title='Viditelnost: ve dne - nezhoršená')
    sns.barplot(data=df_p19[df_p19['section'] ==
                '4 and 6'], x='region', y='p19', ax=ax[1]).set(title='Viditelnost: v noci - nezhoršená')
    sns.barplot(data=df_p19[df_p19['section'] ==
                '2 and 3'], x='region', y='p19', ax=ax[2]).set(title='Viditelnost: ve dne - zhoršená')
    sns.barplot(data=df_p19[df_p19['section'] ==
                '5 and 7'], x='region', y='p19', ax=ax[3]).set(title='Viditelnost: v noci - zhoršená')

    ax[0].set(ylim=(0, 30000), ylabel='Počet nehod')
    ax[0].xaxis.set_visible(False)

    ax[1].set(ylim=(0, 30000), ylabel='', yticklabels=[])
    ax[1].xaxis.set_visible(False)

    ax[2].set(xlabel='Kraj', ylim=(0, 30000), ylabel='Počet nehod')
    ax[2].tick_params(axis='x', which='both', length=0)

    ax[3].set(xlabel='Kraj', ylim=(0, 30000), ylabel='', yticklabels=[])
    ax[3].tick_params(axis='x', which='both', length=0)

    for i in range(len(ax)):
        ax[i].set_axisbelow(True)
        ax[i].grid(axis="y", color="black", alpha=.5, linewidth=.3)

    fig.suptitle('Počet nehod dle viditelnosti', fontsize=20)

    if show_figure:
        plt.show()

    if fig_location:
        fig.savefig(fig_location)


# Type of collision of moving vehicles / Druh srážky jedoucích vozidel


def plot_direction(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):

    def crash_trasfer(num):
        if num == 1:
            return 'čelní'
        elif num == 2:
            return 'boční'
        elif num == 3:
            return 'z boku'
        elif num == 4:
            return 'zezadu'

    df = df[df['p7'] != 0]
    df['p7'] = df['p7'].apply(crash_trasfer)
    df['count'] = df['p7']
    df['date'] = df['date'].dt.month

    df_p7 = df.groupby(['region', 'date', 'p7'])['count'].count().reset_index()
    df_p7.rename(columns={'p7': 'Druh srážky'}, inplace=True)
    df_p7 = df_p7[(df_p7['region'] == 'JHM') | (df_p7['region'] == 'OLK') | (
        df_p7['region'] == 'PAK') | (df_p7['region'] == 'KVK')]

    sns.set_style("whitegrid", {"grid.color": ".6", "grid.linestyle": ":"})

    g = sns.catplot(data=df_p7, x='date', y='count', hue='Druh srážky',
                    col='region', kind='bar', height=3, aspect=1.5, col_wrap=2)

    g.set_axis_labels('Měsíc', 'Počet nehod')
    g.set_titles("Kraj: {col_name}")
    g.fig.suptitle("Druh srážky jedoucích vozidel", y=1)

    if show_figure:
        plt.show()

    if fig_location:
        g.savefig(fig_location)


# Consequences of accidents in time / Následky nehod v čase


def plot_consequences(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):

    df_p13 = df[['region', 'date', 'p13a', 'p13b', 'p13c']]
    df_p13['date'] = df_p13['date'].dt.strftime('%Y-%m')

    df_p13.rename(columns={'p13a': 'Usmrcení', 'p13b': 'Těžké zranění',
                           'p13c': 'Lehké zranění'}, inplace=True)

    df_p13 = df_p13[(df_p13['region'] == 'JHM') | (df_p13['region'] == 'OLK') | (
        df_p13['region'] == 'PAK') | (df_p13['region'] == 'KVK')]

    df_p13 = pd.pivot_table(df_p13, values=['Usmrcení', 'Těžké zranění', 'Lehké zranění'], index=[
                            'region', 'date'], aggfunc='sum').reset_index()

    df_p13 = pd.melt(df_p13, id_vars=['region', 'date'], value_vars=[
        'Usmrcení', 'Těžké zranění', 'Lehké zranění'], var_name='Druh', value_name='Množství')

    sns.set_style("whitegrid", {"grid.color": ".6", "grid.linestyle": ":"})

    g = sns.relplot(
        data=df_p13, x='date', y='Množství', col='region', hue='Druh', kind="line", height=3, aspect=1.5, col_wrap=2
    )

    g.set_titles("Kraj: {col_name}")
    g.set_axis_labels('', 'Počet nehod')
    g.fig.suptitle("Následky nehod v čase", y=1)
    g.set(xlim=(0, 74), ylim=(0, 350), xticks=([0, 12, 24, 36, 48, 60, 71]), xticklabels=(
        ['01/16', '01/17', '01/18', '01/19', '01/20', '01/21', '01/22']))

    if show_figure:
        plt.show()

    if fig_location:
        g.savefig(fig_location)


if __name__ == "__main__":
    df = load_data("data/data.zip")
    df2 = parse_data(df, True)

    plot_visibility(df2, "01_visibility.png")
    plot_direction(df2, "02_direction.png", True)
    plot_consequences(df2, "03_consequences.png")
