
import numpy as np
import pandas as pd

import os

from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib.pyplot import cycler
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.cm

import seaborn as sns

SAVE_DIR = "metrics/reports/"


def line_plot(
        thing: List[pd.Series],
        xlabel: str,
        ylabel: str,
        title: str,
        save_name: Optional[str]=None,
        # area: int=0
        ):
    plt.clf()
    sns.set_style(style='darkgrid')
    c1 = get_cycle("spring", len(thing))
    plt.rcParams["axes.prop_cycle"] = c1
    plt.rcParams["figure.figsize"] = (12,6)
    fig, ax = plt.subplots(1)
    for col in thing:
        ax.plot(col, label=col.name)

    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if save_name is None:
        fig.show()
    else:
        fig.savefig(f'{SAVE_DIR}/{save_name}.pdf')

def comparative_line_plot(
        thing1: List[pd.Series], 
        thing2: List[pd.Series],
        xlabel: str,
        ylabel: str,
        title: str,
        save_name: Optional[str]=None,
        ):
    plt.clf()
    sns.set_style(style='darkgrid')
    c1 = get_cycle("spring", len(thing1))
    c2 = get_cycle("bone", len(thing2))
    plt.rcParams["axes.prop_cycle"] = c1.concat(c2)
    plt.rcParams["figure.figsize"] = (12,6)
    fig, ax = plt.subplots(1)
    
    # Plot our returns (winter colormap)
    for col in thing1:
        ax.plot(col, label=col.name)

    # Plot symbol returns (plasma colormap)
    for col in thing2:
        ax.plot(col, label=col.name)

    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if save_name is None:
        fig.show()
    else:
        fig.savefig(os.path.join(SAVE_DIR, f'{save_name}.pdf'))

def get_cycle(cmap, N=None, use_index="auto"):
    if isinstance(cmap, str):
        if use_index == "auto":
            if cmap in ['Pastel1', 'Pastel2', 'Paired', 'Accent',
                        'Dark2', 'Set1', 'Set2', 'Set3',
                        'tab10', 'tab20', 'tab20b', 'tab20c']:
                use_index=True
            else:
                use_index=False
        cmap = matplotlib.cm.get_cmap(cmap)
    if not N:
        N = cmap.N
    if use_index=="auto":
        if cmap.N > 100:
            use_index=False
        elif isinstance(cmap, LinearSegmentedColormap):
            use_index=False
        elif isinstance(cmap, ListedColormap):
            use_index=True
    if use_index:
        ind = np.arange(int(N)) % cmap.N
        return cycler("color",cmap(ind))
    else:
        colors = cmap(np.linspace(0,1,N))
        return cycler("color",colors)