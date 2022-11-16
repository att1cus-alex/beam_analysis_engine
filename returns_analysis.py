import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

import itertools

import numpy as np

from typing import List

from . plot_utils import get_cycle

def helper(a):
    return list(itertools.chain.from_iterable(a))

def get_rolling_returns(df, periods):
    """
    Given an array of daily returns and a list of periods, returns a new dataframe with the periods we want to histogram for.
    """
    for period in periods:
        roll_returns = df.rolling(window=period)
        pr = roll_returns['log_returns'].mean()
        df[f"log_returns_period_{period}"] = pr

    return df


def plot_period_wide_returns(return_dict, save_dir=None):
    """
        Return dict should be structured like:
        {
            "<seed>": {
                "<Period>": [...list of returns...],
                ...
            }
            ...
        }
    """
    for value in return_dict.values():
        periods = list(value.keys())
        break

    # columns = ['Seed'] + periods
    # df_all = pd.DataFrame(columns = columns)
    dfs = []
    for key, value in return_dict.items():
        tot_length = sum([len(value[p]) for p in periods])
        d1 = {'Seed': [key] * tot_length}
        d2 = {'Period': helper([[p] * len(value[p]) for p in periods])}
        d3 = {'bps': helper([value[p] for p in periods])}
        df = pd.DataFrame(d1 | d2 | d3)
        # df = df.assign(seed=key)
        dfs.append(df)
    df_all = pd.concat(dfs, ignore_index=True)
    plt.clf()
    plt.figure(figsize=(8,6))
    sns.set_theme(style='darkgrid')
    # sns.color_palette('flare')
    vp = sns.violinplot(data=df_all, 
                        x='Seed', 
                        y='bps', 
                        hue='Period',
                        split=False, 
                        inner="quart", 
                        linewidth=1, 
                        palette='flare')
    # Set custom axis labels.
    vp.set(xlabel='Algo Seed', ylabel='Return (bps)', ylim=(-250, 250))
    # sns.despine(left=True)
    fig = vp.get_figure()
    if save_dir is None:
        fig.show() # Be careful with this
    else:
        fig.savefig(f'{save_dir}/pwr.pdf')


def plot_cum_returns(our_returns: List[pd.Series], symbol_returns: List[pd.Series], save_dir=None):
    """
    Something
    """
    plt.clf()
    sns.set_style(style='darkgrid')
    c1 = get_cycle("spring", len(our_returns))
    c2 = get_cycle("bone", len(symbol_returns))
    plt.rcParams["axes.prop_cycle"] = c1.concat(c2)
    plt.rcParams["figure.figsize"] = (12,6)
    fig, ax = plt.subplots(1)
    # Plot our returns (winter colormap)
    for col in our_returns:
        ax.plot(col, label=col.name)
    # Plot symbol returns (plasma colormap)
    for col in symbol_returns:
        ax.plot(col, label=col.name)

    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("Returns")
    ax.set_title("Cumulative Returns vs. Underlying Securities")
    if save_dir is None:
        fig.show()
    else:
        fig.savefig(f'{save_dir}/cum_ret.pdf')


# if __name__ == "__main__":
    
#     r_dict = {}
#     periods = [1, 3, 5] # Day periods to measure returns
#     seeds = [1,2,3]
#     for seed in seeds:
#         ret = generate_fake_log_returns(30)
#         df = pd.DataFrame(ret, columns=['log_returns'])
#         df = get_rolling_returns(df, periods=periods)
#         tmp = {}
#         for period in periods:
#             tmp[period] = df[f"log_returns_period_{period}"].values
#         r_dict[seed] = tmp

    
#     # data = pd.DataFrame()
#     # dummy_data = sns.load_dataset('tips')
#     # print(dummy_data)
#     plot_period_wide_returns(r_dict)
