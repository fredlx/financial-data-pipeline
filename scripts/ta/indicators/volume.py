import ta.volume as ta_volume
import pandas as pd


# Accumulation/Distribution Index (ADI) by Chaikin
def adi(high, low, close, volume, fillna=False):
    return ta_volume.acc_dist_index(high, low, close, volume, fillna)


# Chaikin Money Flow (CMF) by Chaikin
def cmf(high, low, close, volume, window=20, fillna=False):
    return ta_volume.chaikin_money_flow(high, low, close, volume, window, fillna)


# Money Flow Index (MFI) by Gene Quong and Avrum Soudack
def mfi(high, low, close, volume, window=14, fillna=False):
    return ta_volume.money_flow_index(high, low, close, volume, window, fillna)


# Ease of movement (EMV) by Richard Arms
def emv(high, low, volume, window=14, fillna=False):
    return ta_volume.ease_of_movement(high, low, volume, window, fillna)

def emv_signal(high, low, volume, window=14, fillna=False):
    """SMA Signal line for Ease of movement (EMV) from ta.volume"""
    return ta_volume.sma_ease_of_movement(high, low, volume, window, fillna)


# Force Index (FI) by Alexander Elder.
def fi(close, volume, window=13, fillna=False):
    return ta_volume.force_index(close, volume, window, fillna)


# Negative Volume Index (NVI) by Paul Dysart
def nvi(close, volume, fillna=False):
    return ta_volume.negative_volume_index(close, volume, fillna)

def nvi_signal(nvi, roll_window=255, adjust=False):
    """EMA Signal line for Negative Volume Index (NVI)"""
    return nvi.ewm(span=roll_window, adjust=adjust, min_periods=roll_window).mean()


# On-balance volume (OBV) by Joe Granville
def obv(close, volume, fillna=False):
    return ta_volume.on_balance_volume(close, volume, fillna)

def obv_signal(obv, roll_window=20):  # or 65
    """SMA Signal line On-balance volume (OBV), typically a 20 or 65 SMA"""
    return obv.rolling(window=roll_window).mean()


# Volume-price trend (VPT)
def vpt(close, volume, fillna=False):
    return ta_volume.volume_price_trend(close, volume, fillna)


# Volume Weighted Average Price (VWAP)
def vwap(high, low, close, volume, window=14, fillna=False):
    return ta_volume.volume_weighted_average_price(high, low, close, volume, window, fillna)