from bs4 import BeautifulSoup
import requests
import numpy as np
import matplotlib.pyplot as plt
from typing import List


# Generating a graph with different coefficients / Generování grafu s různými koeficienty
def generate_graph(a: List[float], show_figure: bool = False, save_path: str | None = None):
    x = np.linspace(-3,  3, 1000)
    y = np.reshape(a, (-1, 1)) * x**2
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot()

    for i in range(len(a)):
        ax.plot(x, y[i], label='$y_{'+str(a[i])+'}(x)$')
        ax.fill_between(x, y[i], alpha=0.1)
        ax.text(x[-1], y[i][-1], r'$\int{f_{' + str(a[i]) + '}(x)dx}$',
                verticalalignment='center', horizontalalignment='left')

    ax.set_xlim(x.min()*1, x.max()*1.3)
    ax.set_ylim(y.min()*1.112, y.max()*1.112)
    ax.set_xlabel("x")
    ax.set_ylabel("$f_{a}(x)$")
    l = ax.legend(loc='lower right', bbox_to_anchor=(0.8, 1.0), ncol=3)

    if show_figure:
        plt.show()

    if save_path:
        fig.savefig(save_path)


#  Advanced sine wave visualization / Pokročilá vizualizace sinusového signálu
def generate_sinus(show_figure: bool = False, save_path: str | None = None):
    x = np.linspace(0,  100, 20000)
    y1 = 0.5*np.sin((1 * np.pi * x) / 50)
    y2 = 0.25 * np.sin(np.pi * x)
    y3 = y1 + y2
    pos = []
    neg = []

    for i in range(0, len(x)):
        if y3[i] >= y1[i]:
            pos.append(True)
            neg.append(False)
        else:
            pos.append(False)
            neg.append(True)

    y4 = y3.copy()
    y4[neg] = np.nan
    y5 = y3.copy()
    y5[pos] = np.nan

    fig = plt.figure(constrained_layout=True, figsize=(8, 10))
    ax1, ax2, ax3 = (
        fig.add_gridspec(ncols=1, nrows=3)
        .subplots())

    ax1.plot(x, y1)
    ax1.set(xlim=(0, 100), xlabel='t', ylim=(-0.8, 0.8),
            ylabel='$f_{1}(x)$', yticks=[-0.8, -0.4, 0.0, 0.4, 0.8])

    ax2.plot(x, y2)
    ax2.set(xlim=(0, 100), xlabel='t', ylim=(-0.8, 0.8),
            ylabel='$f_{2}(x)$', yticks=[-0.8, -0.4, 0.0, 0.4, 0.8])

    ax3.plot(x, y4, c='green')
    ax3.plot(x, y5, c='red')
    ax3.set(xlim=(0, 100), xlabel='t', ylim=(-0.8, 0.8),
            ylabel='$f_{1}(x)+f_{2}(x)$', yticks=[-0.8, -0.4, 0.0, 0.4, 0.8])

    if show_figure:
        plt.show()

    if save_path:
        fig.savefig(save_path)


# Parsing the html page and downloading the table/ Parsing html stranky a stažení tabulky
def download_data(url="https://ehw.fit.vutbr.cz/izv/temp.html") -> float:
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "xml")
    temp = []
    rows = soup.find_all('tr')

    for row in rows:
        data_row = row.find_all('td')
        data_dict = {}
        numbers = []

        for data in data_row:
            if data['class'] == 'ce1' or data['class'] == 'ce2':
                if len(data.p.text) == 4:
                    data_dict['year'] = int(data.text)
                else:
                    data_dict['month'] = int(data.text)
            elif ',' in data.text:
                number = float(data.text.replace(',', '.'))
                numbers.append(number)
                data_dict['temp'] = np.array(numbers)

        temp.append(data_dict)
    return temp


# Browsing data / Procházení dat
def get_avg_temp(data, year=None, month=None) -> float:
    average = []
    if year and month:
        for i in data:
            if i['year'] == year and i['month'] == month:
                average.append(np.average(i['temp']))
        return np.average(average)
    elif year or month:
        for i in data:
            if i['year'] == year or i['month'] == month:
                average.append(np.average(i['temp']))
        return np.average(average)
    else:
        for i in data:
            average.append(np.average(i['temp']))
    return np.average(average)
