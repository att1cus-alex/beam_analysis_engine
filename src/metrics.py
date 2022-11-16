import pandas as pd
import numpy as onp
from scipy import stats

# Useful functions to do compute random useful 
MARKET_DAYS_PER_YEAR = 252


def linear_returns(log_returns: pd.Series):
    """
    Given a series of timestamped daily log-returns, computes the associated linear returns as a percent
    """
    return (onp.exp(log_returns) - 1.0) * 1e2

def cum_log_returns(log_returns: pd.Series):
    """
    Given a series of timestamped daily log-returns, computes the associated cumulative log returns
    """
    return log_returns.cumsum()

def cum_return(log_returns):
    """
    Given a series of timestamped daily log-returns, computes the associated cumulative return.
    """
    return linear_returns(onp.sum(log_returns))

def underwater(log_returns: pd.Series):
    """
    Given a series of timestamped log-returns, computes the associated underwater plot values 
    """
    cum_rets = onp.exp(cum_log_returns(log_returns))
    running_max = onp.maximum.accumulate(cum_rets)
    underwater = -1e2 * ((running_max - cum_rets) / running_max)
    return underwater
    

def rolling_sharpe(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the associated rolling sharpe ratio values
    """
    pass 

def rolling_beta(log_returns: pd.Series):
    """
    Given a series of timestamped log-returns, computes the associated rolling beta values
    """
    pass

# This doesn't actually use returns???
def daily_turnover(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the associated daily turnover values
    """
    pass

# Moments of returns 

# First moment (annualized)
def annual_return(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the annualized returns
    """
    return linear_returns(onp.mean(log_returns) * MARKET_DAYS_PER_YEAR)

# Second moment (annualized)
def annual_volatility(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the annual volatility of the log returns 
    """
    return linear_returns(onp.std(log_returns, ddof=1) * (MARKET_DAYS_PER_YEAR ** (1/2)))

# Third moment 
def skewness(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the annualized skewness of the log returns. 
    """
    return stats.skew(log_returns)

# Fourth moment
def kurtosis(log_returns: pd.Series):
    """
    Given a series of timestamped returns, comptues the kurtosis of the log returns. The normal distribution has a 
    kurtosis of 3.0
    """
    return stats.kurtosis(log_returns)

# ALPHA / BETA
def alpha(log_returns: pd.Series, market_log_returns: pd.Series):
    risk_free_rate = 0.0
    beta_ = beta(log_returns, market_log_returns)
    returns = linear_returns(log_returns)
    market_returns = linear_returns(market_log_returns)
    adj_returns = returns - risk_free_rate
    adj_factor_returns = market_returns - risk_free_rate
    alpha_series = adj_returns - (beta_ * adj_factor_returns)
    # print("ALPHA DEBUG", onp.mean(alpha_series))

    alpha = onp.power(onp.mean(alpha_series)/1e2 + 1, MARKET_DAYS_PER_YEAR,) - 1
    return alpha

def beta(log_returns: pd.Series, market_log_returns: pd.Series):
    independent = linear_returns(market_log_returns)
    returns = linear_returns(log_returns)
    ind_residual = independent - onp.mean(independent, axis=0)

    covariances = onp.mean(ind_residual * returns, axis=0)

    ind_residual = onp.square(ind_residual)
    independent_variances = onp.mean(ind_residual, axis=0)
    # independent_variances[independent_variances < 1.0e-30] = onp.nan

    res = onp.divide(covariances, independent_variances)

    return res

# RATIOS

def calmar_ratio(log_returns: pd.Series):
    """
    Given a series of timestamped log returns, computes the calmar ratio 

    Formula: TODO
    """
    max_dd = max_drawdown(log_returns)
    assert max_dd <= 0.0
    if max_dd == 0.0:
        return onp.inf
    else:
        return annual_return(log_returns) / onp.abs(max_dd)

def sharpe_ratio(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the Sharpe ratio

    Formula:
    """
    risk_free_rate = 0.0 # TODO: Adjust this.
    returns_risk_adj = linear_returns(log_returns) - risk_free_rate
    out = (MARKET_DAYS_PER_YEAR ** (1/2)) * (onp.mean(returns_risk_adj) / onp.std(returns_risk_adj))
    return out

def sortino_ratio(log_returns: pd.Series):
    """
    Given a series of timestamped returns, computes the sortino ratio
    """
    # No idea what this even means.
    required_return = 0.0
    adj_returns = linear_returns(log_returns) - required_return

    average_annual_return = onp.mean(adj_returns) * MARKET_DAYS_PER_YEAR
    annualized_downside_risk = downside_risk(log_returns)
    out = average_annual_return / annualized_downside_risk

    return out

def tail_ratio(log_returns: pd.Series):
    """
    Given a Series of timestamped returns, computes the tail ratio

    Formula: 95%-tile linear return / 5%-tile linear return, where everything is positive.
    """
    return onp.abs(linear_returns(onp.percentile(log_returns, 95))) / onp.abs(linear_returns(onp.percentile(log_returns, 5)))

# def common_sense_ratio(log_returns: pd.Series):
#     """
#     Given a series of timestamped log returns, computes the Common Sense Ratio
#     """
#     return -1.0

# MISCELLANEOUS

def VaR(log_returns: pd.Series):
    """
    Given a series of log returns, returns the Value at risk (5th percentile)
    """
    cutoff = 0.05
    return linear_returns(onp.percentile(log_returns, 100 * cutoff))


def CVaR(log_returns: pd.Series):
    """
    Given a series of log returns, computes the conditional value at risk
    """
    cutoff = 0.05
    cutoff_index = int((len(log_returns) - 1) * cutoff)
    return onp.mean(linear_returns(onp.partition(log_returns, cutoff_index)[:cutoff_index + 1]))


def max_drawdown(log_returns: pd.Series):
    """
    Given a series of timestamped log returns, computes the max drawdown
    """
    return onp.min(underwater(log_returns))


def stability(log_returns: pd.Series):
    """
    Given a series of timestamped log returns, computes the stability

    Formula: Stability = R^2 of linear fit of cumulative log returns.
    """
    cum_log_ret = cum_log_returns(log_returns)
    rhat = stats.linregress(onp.arange(len(cum_log_ret)), cum_log_ret)[2]
    return rhat ** 2

def downside_risk(log_returns: pd.Series):
    """
    Given a series of timestamped log returns, computes the downside risk. This is needed for computation of the Sortino
    ratio.
    """
    required_return = 0.0 # TODO: Adjust this?
    downside_diff = onp.clip(linear_returns(log_returns) - required_return, onp.NINF, 0.0)
    out = onp.sqrt(onp.mean(onp.square(downside_diff)) * MARKET_DAYS_PER_YEAR)

    return out

TEAR_SHEET_FUNCS = {
    "Annual Return": annual_return,
    "Cumulative Return": cum_return,
    "Annual Volatility": annual_volatility,
    "Skewness": skewness,
    "Kurtosis": kurtosis,
    "Sharpe Ratio": sharpe_ratio,
    "Calmar Ratio": calmar_ratio,
    "Stability": stability,
    "Max Drawdown": max_drawdown,
    "Sortino Ratio": sortino_ratio,
    "Tail Ratio": tail_ratio,
    # "Common Sense Ratio": common_sense_ratio,
    "Daily VaR": VaR,
    "Daily Conditional VaR": CVaR,
    # "Gross Leverage": , <- DELETE THIS EVENTUALLY?
    # "Daily Turnover":  FIGURE THIS OUT
}

ALPHA_BETA_FUNCS = {
    "Alpha ($\\alpha$)": alpha,
    "Beta ($\\beta$)": beta,
}
    