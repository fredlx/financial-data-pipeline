import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

import importlib
import scripts.ta.ta_indicators
import scripts.ta.ta_signals

importlib.reload(scripts.ta.ta_indicators)
importlib.reload(scripts.ta.ta_signals)

from scripts.ta.ta_indicators import get_all_indicators
from scripts.ta.ta_signals import get_all_signals
#from config.settings import load_indicator_params


def load_data(symbol):
    path = Path("data") / symbol / "raw" / f"{symbol}_1d.parquet"
    return pd.read_parquet(path)    
    

def transform_data(raw, verbose=False):
    
    df_enriched = get_all_indicators(raw)
    df_signals = get_all_signals(df_enriched)
    
    if verbose:
        print("Raw blocks:", raw._data.nblocks)
        print("Enriched blocks:", df_enriched._data.nblocks)
        print("Signals blocks:",df_signals._data.nblocks)
    
    return df_enriched, df_signals


def get_signal_entries(prices, signals_ind):
    """Returns pd.Series of prices where conditions are met"""
    if len(prices) != len(signals_ind):
        raise ValueError("Index mismatch")
    
    longs = prices[signals_ind == 1]
    shorts = prices[signals_ind == -1]
    
    return longs, shorts


def get_trend_periods(prices, trend_ind):
    if len(prices) != len(trend_ind):
        raise ValueError("Index mismatch")
    
    bulls = prices.where(trend_ind == 1)
    bears = prices.where(trend_ind == -1)
    
    return bulls, bears


def single_plot(
    prices, ind_name,ind_lines,ind_cols, longs, shorts, bulls, bears,
    plot_colors, plot_signals=True, overlay_trends=False
    ):
    plt.figure(figsize=(14, 6))
    plt.plot(prices, label="Price", color="black")
    
    # Indicator
    if plot_colors:
        for col, color in zip(ind_lines.columns, plot_colors):
            plt.plot(ind_lines[col], label=col, color=color)
    else:
        plt.plot(ind_lines, label = ind_cols)
    
    if overlay_trends and not bulls.empty and not bears.empty:
        plt.plot(bulls.index, bulls, color="green", label="Uptrend")
        plt.plot(bears.index, bears, color="red", label="Downtrend")
    
    if plot_signals and not longs.empty and not shorts.empty:
        plt.scatter(longs.index, longs, label="Buy", marker="^", color="green")
        plt.scatter(shorts.index, shorts, label="Sell", marker="v", color="red")

    plt.title(f"Price, {ind_name} and Entry Signals")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def multi_plots(
    n_plots,
    prices,
    ind_name,
    ind_lines_list,       # List of DataFrames for subplot 2, 3, ...
    ind_cols_list,        # List of column names (same length as above)
    plot_colors_list,     # List of color lists (same length as above)
    longs,
    shorts,
    bulls,
    bears,
    plot_signals=True,
    overlay_trends=False,
    smooth_line=None,
    plot1_df=None, 
    plot1_colors=None
    
):
    fig, ax = plt.subplots(n_plots, 1, sharex=True, figsize=(14, 4 * n_plots))

    # Plot 1: Price + plot_1 indicators
    ax[0].plot(prices, label="Price", color="black")

    if plot1_df is not None and plot1_colors:
        for col, color in zip(plot1_df.columns, plot1_colors):
            ax[0].plot(plot1_df[col], label=col, color=color)

    if overlay_trends and bulls is not None and bears is not None:
        ax[0].plot(bulls.index, bulls, color="green", label="Uptrend")
        ax[0].plot(bears.index, bears, color="red", label="Downtrend")

    if plot_signals and longs is not None and shorts is not None:
        ax[0].scatter(longs.index, longs, label="Buy", marker="^", color="green")
        ax[0].scatter(shorts.index, shorts, label="Sell", marker="v", color="red")

    ax[0].legend()
    ax[0].grid()

    # Plot 2+ (Indicators)
    for i in range(1, n_plots):
        ind_lines = ind_lines_list[i - 1]
        ind_cols = ind_cols_list[i - 1]
        plot_colors = plot_colors_list[i - 1]

        if plot_colors:
            for col, color in zip(ind_lines.columns, plot_colors):
                ax[i].plot(ind_lines[col], label=col, color=color)
        else:
            ax[i].plot(ind_lines, label=ind_cols)

        if smooth_line is not None:
            window = int(smooth_line)
            ax[i].plot(ind_lines.rolling(window).mean(), label=f"smooth_{window}")

        ax[i].legend()
        ax[i].grid()

    plt.title(f"{ind_name}")
    plt.tight_layout()
    plt.show()
    
    
def plot_indicator(
    indicators, signals, ind_name, sig_name, params_ind, trend_name,
    plot_signals=True, overlay_trends=False, smooth_line=None
    ):
    """Expects df_indicators, df_signals and params"""
    prices = indicators["close"]
    
    if sig_name == "":
        plot_signals = False

    # Compute Crosses: longs/shorts
    if f"{ind_name}_{sig_name}" in signals.columns:
        ind_signals = signals[f"{ind_name}_{sig_name}"]
        longs, shorts = get_signal_entries(prices, ind_signals)
    else:
        longs = None
        shorts = None
        
    # Compute Trends: bulls/bears
    if f"{ind_name}_{trend_name}" in signals.columns:
        ind_trend = signals[f"{ind_name}_{trend_name}"]
        bulls, bears = get_trend_periods(prices, ind_trend)
    else:
        bulls = None
        bears = None
    
    # Indicators Lines  
    plot_cfg = params_ind["plot"]
    n_plots = int(plot_cfg["type"][0])  # "3p" → 3
    
    if n_plots == 1:
        plot1 = plot_cfg["plot_1"]
        ind_cols = plot1["lines"]
        plot_colors = plot1.get("colors", [])
        ind_lines = indicators[ind_cols]
        
        single_plot(
            prices, ind_name, ind_lines,ind_cols, longs, shorts, bulls, bears,
            plot_colors, plot_signals, overlay_trends
            )
        
    else:
        ind_lines_list = []
        ind_cols_list = []
        plot_colors_list = []

        # plot_1 is handled separately (in ax[0])

        for i in range(2, n_plots + 1):  # plot_2, plot_3, ...
            key = f"plot_{i}"
            lines = plot_cfg[key]["lines"]
            colors = plot_cfg[key].get("colors", [])

            ind_cols_list.append(lines)
            ind_lines_list.append(indicators[lines])
            plot_colors_list.append(colors)

        # Pass plot_1 separately
        plot1_lines = plot_cfg["plot_1"]["lines"]
        plot1_colors = plot_cfg["plot_1"].get("colors", [])
        plot1_df = indicators[plot1_lines]
    
        multi_plots(
            n_plots,prices,ind_name, ind_lines_list, ind_cols_list, plot_colors_list, longs, shorts, bulls, bears,
            plot_signals, overlay_trends,smooth_line, plot1_df, plot1_colors
            )
        
# Usage Flow
'''
symbol = "BTC-USD"
ind_name = "uo"
sig_name = "center_cross"    # for signal entry
trend_name = "trend"         # for overlay trends

raw = load_data(symbol)
df_indicators, df_signals = transform_data(raw)
params = load_indicator_params()
params_ind = params[ind_name]

plot_indicator(df_indicators, df_signals, ind_name, sig_name, params_ind, trend_name,
    plot_signals=True, overlay_trends=False, smooth_line=3
    )'''