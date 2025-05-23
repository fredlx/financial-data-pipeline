import ta.trend as ta_trend
import pandas as pd


# Average Directional Movement Index (ADX) by Welles Wilder
def adx(high, low, close, window=14, fillna=False):
    return ta_trend.adx(high, low, close, window, fillna)

# Average Directional Movement Index (-DI)
def adx_neg(high, low, close, window=14, fillna=False):
    return ta_trend.adx_neg(high, low, close, window, fillna)

# Average Directional Movement Index (+DI)
def adx_pos(high, low, close, window=14, fillna=False):
    return ta_trend.adx_pos(high, low, close, window, fillna)

# Aroon
# Aroon Negative (-AI)
def aroon_down(close, low, window=25, fillna=False):
    """(AI-) Identify when trends are likely to change direction (downtrend)"""
    return ta_trend.aroon_down(close, low, window, fillna)

# Aroon Positive (+AI)
def aroon_up(close, high, window=25, fillna=False):
    """(AI+) Identify when trends are likely to change direction (uptrend)"""
    return ta_trend.aroon_up(close, high, window, fillna)

# Aroon Oscillator (aroon_up - aroon_down)
def aroon_osc(aroon_up, aroon_down):
    return aroon_up - aroon_down


# Commodity Channel Index (CCI) by Donald Lambert
def cci(high, low, close, window=20, constant=0.015, fillna=False):
    return ta_trend.cci(high, low, close, window, constant, fillna)

# Detrended Price Oscillator (DPO)
def dpo(close, window=20, fillna=False):
    return ta_trend.dpo(close, window, fillna)

# Exponential Moving Average (EMA)
def ema(close, window=12, fillna=False):
    return ta_trend.ema_indicator(close, window, fillna)


# Ichimoku Kinkō Hyō (Ichimoku)
# Ichimoku A: Senkou Span A (Leading Span A)
def ichi_a(high, low, window1=9, window2=26, visual=False, fillna=False):
    return ta_trend.ichimoku_a(high, low, window1, window2, visual, fillna)

# Ichimoku B: Senkou Span B (Leading Span B)
def ichi_b(high, low, window2=26, window3=52, visual=False, fillna=False):
    return ta_trend.ichimoku_b(high, low, window2, window3, visual, fillna)

# Kijun-sen (Base Line)
def ichi_base(high, low, window1=9, window2=26, visual=False, fillna=False):
    return ta_trend.ichimoku_base_line(high, low, window1, window2, visual, fillna)

# Tenkan-sen (Conversion Line)
def ichi_conversion(high, low, window1=9, window2=26, visual=False, fillna=False):
    return ta_trend.ichimoku_conversion_line(high, low, window1, window2, visual, fillna)

# Chikou Span (Lagging Span)
def chikou_span(close, period=26):
    return close.shift(-period)
    


# KST Oscillator (KST)
def kst(close, roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15, fillna=False):
    return ta_trend.kst(close, roc1, roc2, roc3, roc4, window1, window2, window3, window4, fillna)

def kst_signal(close, roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15, nsig=9, fillna=False):
    """Signal line for KST Oscillator (KST) """
    return ta_trend.kst_sig(close, roc1, roc2, roc3, roc4, window1, window2, window3, window4, nsig, fillna)


# Moving Average Convergence Divergence (MACD)
# MACD Line
def macd(close, window_slow=26, window_fast=12, fillna=False):
    """MACD Line"""
    return ta_trend.macd(close, window_slow, window_fast, fillna)

# MACD Signal Line
def macd_signal(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    """EMA Signal line MACD"""
    return ta_trend.macd_signal(close, window_slow, window_fast, window_sign, fillna)

# MACD Diff: MACD Line - MACD Signal
def macd_diff(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    """MACD Line - MACD Signal"""
    return ta_trend.macd_diff(close, window_slow, window_fast, window_sign, fillna)


# Mass Index (MI) by Donald Dorsey
def mi(high, low, window_fast=9, window_slow=25, fillna=False):
    return ta_trend.mass_index(high, low, window_fast, window_slow, fillna)


# Parabolic Stop and Reverse (Parabolic SAR)
def psar_down(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """
    Parabolic Stop and Reverse (Parabolic SAR) - Psar Down
    Returns the PSAR series with non-N/A values for downward trends
    """
    return ta_trend.psar_down(high, low, close, step, max_step, fillna)

def psar_down_ind(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """
    Parabolic Stop and Reverse (Parabolic SAR) - Psar Down Indicator
    Returns 1, if there is a reversal towards an downward trend. Else, returns 0.
    """
    return ta_trend.psar_down_indicator(high, low, close, step, max_step, fillna)

def psar_up(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """
    Parabolic Stop and Reverse (Parabolic SAR) - Psar Up
    Returns the PSAR series with non-N/A values for upward trends
    """
    return ta_trend.psar_up(high, low, close, step, max_step, fillna)

def psar_up_ind(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """
    Parabolic Stop and Reverse (Parabolic SAR) - Psar Up Indicator
    Returns 1, if there is a reversal towards an upward trend. Else, returns 0.
    """
    return ta_trend.psar_up_indicator(high, low, close, step, max_step, fillna)


# Simple Moving Average (SMA)
def sma(close, window=12, fillna=False):
    return ta_trend.sma_indicator(close, window, fillna)


# Schaff Trend Cycle (STC)
def stc(close, window_slow=50, window_fast=23, cycle=10, smooth1=3, smooth2=3, fillna=False):
    return ta_trend.stc(close, window_slow, window_fast, cycle, smooth1, smooth2, fillna)


# Triple Exponentially Smoothed Moving Average (TRIX)
def trix(close, window=15, fillna=False):
    return ta_trend.trix(close, window, fillna)

# EMA Signal line for TRIX
def trix_signal(trix, roll_window=9, adjust=False):
    """EMA Signal line for TRIX, typically a 9 window period"""
    return trix.ewm(span=roll_window, adjust=adjust, min_periods=roll_window).mean()


# Vortex Indicator (VI) by Etienne Botes and Douglas Siepman
# -VI
def vi_neg(high, low, close, window=14, fillna=False):
    return ta_trend.vortex_indicator_neg(high, low, close, window, fillna)

# +VI
def vi_pos(high, low, close, window=14, fillna=False):
    return ta_trend.vortex_indicator_pos(high, low, close, window, fillna)

# VI Oscillator (custom)
def vi_osc(vi_pos, vi_neg):
    return vi_pos - vi_neg


# Weighted Moving Average (WMA)
def wma(close, window=9, fillna=False):
    return ta_trend.wma_indicator(close, window, fillna)