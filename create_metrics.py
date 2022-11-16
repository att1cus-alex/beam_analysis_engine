from comet_ml.api import API

import numpy as np
import ast

import os

from . returns_analysis import plot_period_wide_returns, plot_cum_returns

# Get metrics from comet
def get_vals(exp, name):
    metric = exp.get_metrics(name)
    arr = [(int(a['epoch']), float(a['metricValue'])) for a in metric]
    arr = sorted(arr, key=lambda x: x[0])
    epoch, vals = zip(*arr)
    return vals

# Helper function for numpy rolling window
def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def rolling_returns(returns, periods, bps_convert=True):
    ret = {}
    for period in periods:
        rolled = rolling_window(returns, period + 1)
        rolled_returns = (rolled[:,-1] - rolled[:,0]) / period
        # Optionally convert the returns to bps (imo bps are dumb)
        if bps_convert:
            rolled_returns = log_ret_to_bps(rolled_returns)
        ret[period] = rolled_returns
    return ret

def log_ret_to_bps(log_rets):
    # Exponentiate to get linear returns
    lr = np.exp(log_rets)
    # Convert to basis points 
    bps = (lr - 1) * 10000
    return bps

class AlgoMetrics:

    def __init__(self, exp_ids, workspace='alex-guerra-618', project_name='tests'):
        api_key = "XhV8CaJQB3HYDaYxXmTY2tE2i"
        comet_api = API(api_key=api_key)
        experiments = [comet_api.get_experiment(project_name=project_name,
                                                    workspace=workspace,
                                                    experiment=exp_id) for exp_id in exp_ids]

        # Get all the tickers traded and make sure they are all consistent
        self.symbols_list = [exp.get_parameters_summary('tickers')['valueCurrent'] for exp in experiments]
        assert all(self.symbols_list)
        self.symbols = ast.literal_eval(self.symbols_list[0])

        # Get the seed for all the experiments.
        seeds = [exp.get_parameters_summary('seed')['valueCurrent'] for exp in experiments]
        
        self.exp_dict = {seeds[i] : experiments[i] for i in range(len(seeds))}

        # Get the cumulative returns for all the seeds
        self.our_log_rets = self.get_our_log_returns()

        # Get the individual stock returns for all the securities
        self.sym_log_rets = self.get_symbol_log_returns()
    
    def get_our_log_returns(self):
        assert self.exp_dict is not None
        vals_all = {}
        for seed, exp in self.exp_dict.items():
            vals = get_vals(exp, 'Cum Portfolio Returns')
            # TODO: Also use epoch i a useful way somehow
            vals_all[seed] = np.log(vals)
            
        return vals_all

    def get_symbol_log_returns(self):
        assert self.symbols is not None and len(self.symbols) > 0
        vals_all = {}
        # Can just use the first experiment since they should all be the same.
        exp = self.exp_dict[next(iter(self.exp_dict))]
        for symbol in self.symbols:
            vals = get_vals(exp, f'Cum {symbol} Returns')
            vals_all[symbol] = np.log(vals)
        return vals_all

    def create_report(self, periods, report_name="test"):
        # First make a folder for the report (if not exists)
        save_dir = f"metrics/reports/{report_name}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Returns analysis

        # PERIOD WISE RETURNS
        pwr_dict = {}
        for seed, our_log_ret in self.our_log_rets.items():
            rets = rolling_returns(our_log_ret, periods)
            pwr_dict[seed] = rets

        # this plots absolute period wise returns (pwr) on a violin plot for each seed.
        plot_period_wide_returns(pwr_dict, save_dir=save_dir)
        
        # CUMULATIVE RETURNS 
        our_cum_dict = {}
        for seed, log_ret in self.our_log_rets.items():
            our_cum_dict[seed] = np.exp(log_ret)
        sym_cum_dict = {}
        for symbol, log_ret in self.sym_log_rets.items():
            sym_cum_dict[symbol] = np.exp(log_ret)
        plot_cum_returns(our_cum_dict, sym_cum_dict, save_dir=save_dir)

        
        
        


if __name__ == "__main__":
    # BAC only experiments
    exp_ids = ["2a6af48a09284ed8b12876afea442718", "c1c3e0b0589148e7b615199ea1d14341"]
    am = AlgoMetrics(exp_ids)
    periods = [1, 5, 25]
    am.create_report(periods)