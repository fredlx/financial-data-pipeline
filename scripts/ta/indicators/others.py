import ta.others as ta_others
import numpy as np
import pandas as pd


def cumulative_rets(close, fillna=False):
    return ta_others.cumulative_return(close, fillna)

def daily_rets(close, fillna=False):
    return ta_others.daily_return(close, fillna)

def daily_log_rets(close, fillna=False):
    return ta_others.daily_log_return(close, fillna)

def sharpe_ratio(
    stock_prices: pd.Series, 
    benchmark_prices: pd.Series, 
    trading_days: int =252 # 365
    ) -> float: 
    """
    Measures the risk to reward of a portfolio/asset by 
    dividing the excess return by its volatility.
    """
    stock_rets = stock_prices.pct_change()
    bench_rets = benchmark_prices.pct_change()
    
    excess_rets = stock_rets.sub(bench_rets, axis=0).dropna()
    avg_excess_return = excess_rets.mean()
    sd_excess_return = excess_rets.std()
    
    # Daily Sharpe Ratio
    daily_sharpe_ratio = avg_excess_return.div(sd_excess_return)
    
    # Annualized Sharpe Ratio
    annual_factor = np.sqrt(trading_days)  # numpy sqrt
    annual_sharpe_ratio = daily_sharpe_ratio.mul(annual_factor)
    
    return annual_sharpe_ratio
    
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index
# https://portfoliooptimizer.io/blog/ulcer-performance-index-optimization/
def ulcer_performance_index(prices, risk_free_rate=0.0):
    """
    Ulcer Performance Index (UPI), or Martin Ratio
    risk-adjusted performance metric that refines the Sharpe Ratio by 
    replacing volatility with downside risk, using Ulcer Index
    """
    
    def ulcer_index(prices):
        max_price = np.maximum.accumulate(prices)
        drawdown = (prices - max_price) / max_price * 100
        return np.sqrt(np.mean(drawdown**2))
    
    returns = np.diff(prices) / prices[:-1]
    mean_return = np.mean(returns)
    ui = ulcer_index(prices) # ulcer_index 
    return (mean_return - risk_free_rate) / ui if ui != 0 else np.nan