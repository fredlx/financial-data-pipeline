import ta.momentum as ta_momentum
import pandas as pd


# Awesome Oscilator (AO)
def ao(high, low, window1=5, window2=34, fillna=False):
    return ta_momentum.awesome_oscillator(high, low, window1, window2, fillna)


# Kaufman's Adaptive Moving Average (KAMA)
def kama(close, window=10, pow1=2, pow2=30, fillna=False):
    return ta_momentum.kama(close, window, pow1, pow2, fillna)


# Percentage Price Oscillator Line (PPO)
def ppo(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    return ta_momentum.ppo(close, window_slow, window_fast, window_sign, fillna)

# Percentage Price Oscillator Histogram (PPO)
def ppo_hist(close, window_slow=26, window_fast=12, window_sign=9, fillna= False):
    return ta_momentum.ppo_hist(close, window_slow, window_fast, window_sign, fillna)

# Percentage Price Oscillator Signal Line (PPO)
def ppo_signal(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    return ta_momentum.ppo_signal(close, window_slow, window_fast, window_sign, fillna)


# Percentage Volume Oscillator Line (PVO)
def pvo(volume, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    return ta_momentum.pvo(volume, window_slow, window_fast, window_sign, fillna)

# Percentage Volume Oscillator Histogram (PVO)
def pvo_hist(volume, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    return ta_momentum.pvo_hist(volume, window_slow, window_fast, window_sign, fillna)

# Percentage Volume Oscillator Signal Line (PVO)
def pvo_signal(volume, window_slow=26, window_fast=12, window_sign=9, fillna= False):
    return ta_momentum.pvo_signal(volume, window_slow, window_fast, window_sign, fillna)


# Rate of Change (ROC)
def roc(close, window= 12, fillna= False):
    return ta_momentum.roc(close, window, fillna)


# Relative Strength Index (RSI)
def rsi(close, window=14, fillna=False):
    return ta_momentum.rsi(close, window, fillna)


# Stochastic Oscillator (STOCH)
def stoch(high, low, close, window=14, smooth_window=3, fillna=False):
    return ta_momentum.stoch(high, low, close, window, smooth_window, fillna)

# Stochastic Oscillator Signal Line (STOCH-SMA)
def stoch_signal(high, low, close, window=14, smooth_window=3, fillna=False):
    return ta_momentum.stoch_signal(high, low, close, window, smooth_window, fillna)


# Stochastic RSI (STOCHRSI)
def stochrsi(close, window=14, smooth1=3, smooth2=3, fillna=False):
    return ta_momentum.stochrsi(close, window, smooth1, smooth2, fillna)

# Stochastic RSI (STOCHRSI %D)
def stochrsi_d(close, window=14, smooth1=3, smooth2=3, fillna= False):
    return ta_momentum.stochrsi_d(close, window, smooth1, smooth2, fillna)

# Stochastic RSI (STOCHRSI %K)
def stochrsi_k(close, window=14, smooth1=3, smooth2=3, fillna=False):
    return ta_momentum.stochrsi_k(close, window, smooth1, smooth2, fillna)


# True strength index (TSI)
def tsi(close, window_slow=25, window_fast=13, fillna=False):
    return ta_momentum.tsi(close, window_slow, window_fast, fillna)

# True strength index Signal Line (TSI)
def tsi_signal(tsi, roll_window=10, adjust=False):
    """EMA Signal line for True strength index (TSI), typically a 10 period window."""
    return tsi.ewm(span=roll_window, adjust=adjust, min_periods=roll_window).mean()


# Ultimate Oscillator (UO)
def uo(high, low, close, window1=7, window2=14, window3=28, weight1=4.0, weight2=2.0, weight3=1.0, fillna=False):
    return ta_momentum.ultimate_oscillator(high, low, close, window1, window2, window3, weight1, weight2, weight3, fillna)


# Williams %R (WILLR)
def willr(high, low, close, lbp=14, fillna=False):
    return ta_momentum.williams_r(high, low, close, lbp, fillna)