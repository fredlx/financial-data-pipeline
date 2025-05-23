import ta.volatility as ta_volatility
import pandas as pd


# Average True Range (ATR) - J. Welles Wilder
def atr(high, low, close, window=14, fillna=False):
    return ta_volatility.average_true_range(high, low, close, window, fillna)

# Average True Range Percent (ATRP)
def atrp(atr, close, use_sma=False, roll_window=20):
    """Use Close or SMA Close"""
    if use_sma:
        atrp = atr / close.rolling(window=roll_window).mean() * 100
    else:
        atrp = atr / close * 100
    return atrp


# Ulcer Index (UI) by Peter Martin and Byron McCann
def ui(close, window=14, fillna=False):
    return ta_volatility.ulcer_index(close, window, fillna)


# Bollinger Bands (BB) by John Bollinger

def bb_high(close, window=20, window_dev=2, fillna=False):
    """BB Upper Band"""
    return ta_volatility.bollinger_hband(close, window, window_dev, fillna)

def bb_high_ind(close, window=20, window_dev=2, fillna=False):
    """
    BB Upper Band Indicator
    Returns 1, if close is higher than high band. Else, return 0.
    """
    return ta_volatility.bollinger_hband_indicator(close, window, window_dev, fillna)

def bb_low(close, window=20, window_dev=2, fillna=False): 
    """BB Lower Band"""
    return ta_volatility.bollinger_lband(close, window, window_dev, fillna)

def bb_low_ind(close, window=20, window_dev=2, fillna=False):
    """
    BB Lower Band Indicator
    Returns 1, if close is lower than low band. Else, return 0.
    """
    return ta_volatility.bollinger_lband_indicator(close, window, window_dev, fillna)

def bb_middle(close, window=20, fillna=False):
    """BB Middle Band SMA""" 
    return ta_volatility.bollinger_mavg(close, window, fillna)

def bb_width(close, window=20, window_dev=2, fillna=False):
    """BB Width Band"""
    return ta_volatility.bollinger_wband(close, window, window_dev, fillna)

def bb_percent(close, window=20, window_dev=2, fillna=False):
    """BB Channel Percentage Band"""
    return ta_volatility.bollinger_pband(close, window, window_dev, fillna)


# Donchian Channel (DC) by Richard Donchian
# https://trendspider.com/learning-center/donchian-channels-a-comprehensive-guide-for-trend-following-traders/

def dc_high(high, low, close, h_window=20, offset=0, fillna=False):
    """DC Upper Band"""  
    return ta_volatility.donchian_channel_hband(high, low, close, h_window, offset, fillna)

def dc_low(high, low, close, l_window=20, offset=0, fillna=False):
    """DC Lower Band""" 
    return ta_volatility.donchian_channel_lband(high, low, close, l_window, offset, fillna)

def dc_middle(high, low, close, m_window=10, offset=0, fillna=False):
    """DC Middle Band""" 
    return ta_volatility.donchian_channel_mband(high, low, close, m_window, offset, fillna)

def dc_width(high, low, close, m_window=10, offset=0, fillna=False):
    """DC Channel Width Band""" 
    return ta_volatility.donchian_channel_wband(high, low, close, m_window, offset, fillna)

def dc_percent(high, low, close, m_window=10, offset=0, fillna=False):
    """DC Channel Width Percentage Band""" 
    return ta_volatility.donchian_channel_pband(high, low, close, m_window, offset, fillna)


# Keltner Channel (KC) by Chester W. Keltner
# https://trendspider.com/learning-center/keltner-channels-understanding-and-applying-this-classic-technical-indicator/

def kc_high(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """KC Upper Band"""
    return ta_volatility.keltner_channel_hband(high, low, close, window, window_atr, fillna, original_version)

def kc_high_ind(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """
    KC Upper Band Indicator
    Returns 1, if close is higher than high band. Else, return 0.
    """
    return ta_volatility.keltner_channel_hband_indicator(high, low, close, window, window_atr, fillna, original_version)

def kc_low(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """KC Lower Band"""
    return ta_volatility.keltner_channel_lband(high, low, close, window, window_atr, fillna, original_version)

def kc_low_ind(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """
    KC Lower Band Indicator
    Returns 1, if close is lower than low band. Else, return 0.
    """
    return ta_volatility.keltner_channel_lband_indicator(high, low, close, window, window_atr, fillna, original_version)

def kc_middle(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """KC Middle Band"""
    return ta_volatility.keltner_channel_mband(high, low, close, window, window_atr, fillna, original_version)

def kc_width(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """KC Channel Width Band Band"""
    return ta_volatility.keltner_channel_wband(high, low, close, window, window_atr, fillna, original_version)

def kc_percent(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    """KC Channel Width Percentage Band"""
    return ta_volatility.keltner_channel_pband(high, low, close, window, window_atr, fillna, original_version)


