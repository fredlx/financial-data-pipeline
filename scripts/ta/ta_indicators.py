import pandas as pd
from pathlib import Path

import importlib
import scripts.ta.indicators.momentum
importlib.reload(scripts.ta.indicators.momentum)

import scripts.ta.indicators.volume
importlib.reload(scripts.ta.indicators.volume)

import scripts.ta.indicators.volatility
importlib.reload(scripts.ta.indicators.volatility)

import scripts.ta.indicators.trend
importlib.reload(scripts.ta.indicators.trend)

import config.settings
importlib.reload(config.settings)

from scripts.ta.ta_helpers import get_ta_params, get_ohlcv
from config.settings import load_yaml_config, load_flat_params

from scripts.utils.performance import safe_inserts


from scripts.ta.indicators.momentum import (
    ao, kama, ppo, ppo_signal, pvo, pvo_signal, roc, rsi, stoch, stoch_signal, 
    stochrsi, stochrsi_d, stochrsi_k, tsi, tsi_signal, uo, willr
    )

from scripts.ta.indicators.volatility import (
    atr, atrp, ui, dc_high, dc_low, dc_middle, dc_width, dc_percent,
    bb_high, bb_low, bb_middle, bb_high_ind, bb_low_ind, bb_width, bb_percent,
    kc_high, kc_low, kc_middle, kc_high_ind, kc_low_ind, kc_width, kc_percent
    )

from scripts.ta.indicators.trend import (
    adx, adx_pos, adx_neg, aroon_down, aroon_up, aroon_osc, cci ,dpo, 
    ema, sma, wma, ichi_a, ichi_b, ichi_base, ichi_conversion, chikou_span, kst, kst_signal, 
    macd, macd_diff, macd_signal, mi, psar_down, psar_down_ind, psar_up, psar_up_ind, 
    stc, trix, trix_signal, vi_neg, vi_pos, vi_osc
    )

from scripts.ta.indicators.volume import (
    adi, cmf, mfi, emv, emv_signal, fi, nvi, nvi_signal,
    obv, obv_signal, vpt, vwap
    )

from scripts.ta.indicators.others import (
    cumulative_rets, daily_rets, daily_log_rets, 
    sharpe_ratio, ulcer_performance_index
    )


# (TODO) refactor the entire resize df to accept partitioned files and not to pass the entire df if not needed

def slice_df(df, default_params=True):
    
    def get_max_window(series, delta=10):
        return pd.Series(series.explode(), dtype="float").max() + delta
        
    ta_params_df = get_ta_params(default_params)
    max_window = get_max_window(ta_params_df)
    
    df = df.tail(int(max_window)).reset_index(drop=True).copy()
    
    return df
    
@safe_inserts(threshold=30)
def get_all_indicators(df_orig, default_params=True, resize_df=False):
    """Returns df with indicators considering csv with params"""
    
    ta_params_ind = load_yaml_config("indicator_params.yaml")
    flat_main = load_flat_params(ta_params_ind, section="main")
    flat_custom = load_flat_params(ta_params_ind, section="custom")

    df = slice_df(df_orig) if resize_df else df_orig.copy()
    open_, high, low, close, volume = get_ohlcv(df)
    
    # use dict instead of pandas inserts to df
    new_cols = {}
    
    
    # ------------------- MOMENTUM ------------------ #
    
    # Awesome Oscilator (AO)
    name = "ao"
    new_cols[name] = ao(high, low, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()  # smooth
    
    # Kaufman's Adaptive Moving Average (KAMA)
    name = "kama"
    new_cols[name] = kama(close, *flat_main[name])

    # Percentage Price Oscillator (PPO)
    name = "ppo"
    new_cols[name] = ppo(close, *flat_main[name])
    new_cols[f"{name}_signal"] = ppo_signal(close, *flat_main[name])

    # Percentage Volume Oscillator (PVO)
    name = "pvo"
    new_cols[name] = pvo(volume, *flat_main[name])
    new_cols[f"{name}_signal"] = pvo_signal(volume, *flat_main[name])

    # Rate of Change (ROC)
    name = "roc"
    new_cols[name] = roc(close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Relative Strength Index (RSI)
    name = "rsi"
    new_cols[name] = rsi(close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Stochastic Oscillator (STOCH)
    name = "stoch"
    new_cols[name] = stoch(high, low, close, *flat_main[name])
    new_cols[f"{name}_signal"] = stoch_signal(high, low, close, *flat_main[name])

    # Stochastic RSI (STOCHRSI)
    name = "stochrsi"
    new_cols[name] = stochrsi(close, *flat_main[name])
    new_cols[f"{name}_d"] = stochrsi_d(close, *flat_main[name])
    new_cols[f"{name}_k"] = stochrsi_k(close, *flat_main[name])

    # True strength index (TSI)
    name = "tsi"
    new_cols[name] = tsi(close, *flat_main[name])
    new_cols[f"{name}_signal"] = tsi_signal(new_cols[name], *flat_custom[name])

    # Ultimate Oscillator (UO)
    name = "uo"
    new_cols[name] = uo(high, low, close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Williams %R (WILLR)
    name = "willr"
    new_cols[name] = willr(high, low, close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # -------------- VOLUME --------------- #
    
    # Accumulation/Distribution Index (ADI)
    name = "adi"
    new_cols[name] = adi(high, low, close, volume)

    # Chaikin Money Flow (CMF)
    name = "cmf"
    new_cols[name] = cmf(high, low, close, volume, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Ease of movement (EMV)
    name = "emv"
    new_cols[name] = emv(high, low, volume, *flat_main[name])
    new_cols[f"{name}_signal"] = emv_signal(high, low, volume, *flat_custom[name])

    # Force Index (FI)
    name = "fi"
    new_cols[name] = fi(close, volume, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Money Flow Index (MFI)
    name = "mfi"
    new_cols[name] = mfi(high, low, close, volume, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Negative Volume Index (NVI)
    name = "nvi"
    new_cols[name] = nvi(close, volume)
    new_cols[f'{name}_signal'] = nvi_signal(new_cols[name], *flat_main[name])

    # On-balance volume (OBV)
    name = "obv"
    new_cols[name] = obv(close, volume)
    new_cols[f'{name}_signal'] = obv_signal(new_cols[name], *flat_main[name])

    # Volume-price trend (VPT)
    name = "vpt"
    new_cols[name] = vpt(close, volume)
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Volume Weighted Average Price (VWAP)
    name = "vwap"
    new_cols["vwap"] = vwap(high, low, close, volume, *flat_main[name])


    # ------------------ VOLATILITY ------------------- #
    
    # ATR
    name = "atr"
    new_cols[name] = atr(high, low, close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()
    
    # ATRP
    name = "atrp"
    new_cols[name] = atrp(new_cols['atr'], close)
    new_cols[f'{name}_smooth'] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Bollinger Bands (BB)
    name = "bb"
    new_cols[f"{name}_high"] = bb_high(close, *flat_main[name])
    new_cols[f"{name}_low"] = bb_low(close, *flat_main[name])
    new_cols[f"{name}_middle"] = bb_middle(close, *flat_main[name])
    new_cols[f"{name}_width_p"] = bb_percent(close, *flat_main[name])
    new_cols[f"{name}_width"] = bb_width(close, *flat_main[name])
    new_cols[f"{name}_high_ind"] = bb_high_ind(close, *flat_main[name])
    new_cols[f"{name}_low_ind"] = bb_low_ind(close, *flat_main[name])

    # Donchian Channel (DC)
    name = "dc"
    h_window, l_window, m_window, offset = flat_main[name]
    new_cols[f"{name}_high"] =  dc_high(high, low, close, h_window, offset)
    new_cols[f"{name}_low"] =  dc_low(high, low, close, l_window, offset)
    new_cols[f"{name}_middle"] = dc_middle(high, low, close, m_window, offset)
    new_cols[f"{name}_width_p"] = dc_percent(high, low, close, m_window, offset)
    new_cols[f"{name}_width"] = dc_width(high, low, close, m_window, offset)

    # Keltner Channel (KC)
    name = "kc"
    new_cols[f"{name}_high"] =  kc_high(high, low, close, *flat_main[name])
    new_cols[f"{name}_low"] = kc_low(high, low, close, *flat_main[name])
    new_cols[f"{name}_middle"] = kc_middle(high, low, close, *flat_main[name])
    new_cols[f"{name}_width_p"] = kc_percent(high, low, close, *flat_main[name])
    new_cols[f"{name}_width"] = kc_width(high, low, close, *flat_main[name])
    new_cols[f"{name}_high_ind"] = kc_high_ind(high, low, close, *flat_main[name])
    new_cols[f"{name}_low_ind"] = kc_low_ind(high, low, close, *flat_main[name])

    # Ulcer Index (ui)
    name = "ui"
    new_cols[name] = ui(close, *flat_main[name])
    new_cols[f"{name}_smooth"] = ui(close, *flat_main[name])


    #--------------------- TREND ------------------------#
    
    # Average Directional Movement Index (ADX)
    name = "adx"
    new_cols[name] =  adx(high, low, close, *flat_main[name])
    new_cols[f"{name}_neg"] = adx_neg(high, low, close, *flat_main[name])
    new_cols[f"{name}_pos"] = adx_pos(high, low, close, *flat_main[name])

    # Aroon Indicator (AROON)
    name = "aroon"
    new_cols[f"{name}_down"] = aroon_down(close, low, *flat_main[name])
    new_cols[f"{name}_up"] = aroon_up(close, high, *flat_main[name])
    new_cols[f"{name}_osc"] = aroon_osc(new_cols[f"{name}_up"], new_cols[f"{name}_down"])

    # Commodity Channel Index (CCI)
    name = "cci"
    new_cols[name] = cci(high, low, close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Detrended Price Oscillator (DPO)
    name = "dpo"
    new_cols[name] = dpo(close, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Exponential Moving Average (EMA)
    name = "ema"
    w1, w2 = flat_main[name]
    new_cols[f"{name}_1"] = ema(close, w1, fillna=False)
    new_cols[f"{name}_2"] = ema(close, w2, fillna=False)
    
    # Simple Moving Average (SMA)
    name = "sma"
    w1, w2 = flat_main[name]
    new_cols[f"{name}_1"] = sma(close, w1, fillna=False)
    new_cols[f"{name}_2"] = sma(close, w2, fillna=False)
    
    # Weighted Moving Average (WMA)
    name = "wma"
    w1, w2 = flat_main[name]
    new_cols[f"{name}_1"] = wma(close, w1, fillna=False)
    new_cols[f"{name}_2"] = wma(close, w2, fillna=False)

    # Ichimoku Kinkō Hyō (Ichimoku)
    name = "ichi"
    window1, window2, window3, period = flat_main[name]
    new_cols[f"{name}_a"] = ichi_a(high, low, window1, window2, visual=False, fillna=False)
    new_cols[f"{name}_b"] = ichi_b(high, low, window2, window3, visual=False, fillna=False)
    new_cols[f"{name}_base"] = ichi_base(high, low, window1, window2, visual=False, fillna=False)
    new_cols[f"{name}_conversion"] = ichi_conversion(high, low, window1, window2, visual=False, fillna=False)
    new_cols[f"{name}_lagged"] = chikou_span(close, period)

    # KST Oscillator (KST)
    name = "kst"
    window_signal = flat_custom[name][0]  # extract int
    params_signal = (*flat_main[name], window_signal)
    new_cols[name] = kst(close, *flat_main[name])
    new_cols[f"{name}_signal"] = kst_signal(close, *params_signal)

    # Moving Average Convergence Divergence (MACD)
    name = "macd"
    window_fast, window_slow, window_sign = flat_main[name]
    new_cols[name] = macd(close, window_slow, window_fast, fillna=False)
    new_cols[f"{name}_diff"] = macd_diff(close, window_slow, window_fast, window_sign, fillna=False)
    new_cols[f"{name}_signal"] = macd_signal(close, window_slow, window_fast, window_sign, fillna=False)

    # Mass Index (MI)
    name = "mi"
    new_cols[name] = mi(high, low, *flat_main[name])
    new_cols[f"{name}_smooth"] = new_cols[name].rolling(*flat_custom[name]).mean()

    # Parabolic Stop and Reverse (Parabolic SAR)
    name = "psar"
    new_cols[f"{name}_down"] = psar_down(high, low, close, *flat_main[name])
    new_cols[f"{name}_up"] = psar_up(high, low, close, *flat_main[name])
    new_cols[f"{name}_down_ind"] = psar_down_ind(high, low, close, *flat_main[name])
    new_cols[f"{name}_up_ind"] = psar_up_ind(high, low, close, *flat_main[name])

    # Schaff Trend Cycle (STC)
    name = "stc"
    new_cols[name] = stc(close, *flat_main[name])

    # Triple Exponentially Smoothed Moving Average (TRIX)
    name = "trix"
    new_cols[name] = trix(close, *flat_main[name])
    new_cols[f"{name}_signal"] = trix_signal(new_cols[name], *flat_custom[name])

    # Vortex Indicator (VI)
    name = "vi"
    new_cols[f"{name}_neg"] = vi_neg(high, low, close, *flat_main[name])
    new_cols[f"{name}_pos"] = vi_pos(high, low, close, *flat_main[name])
    new_cols[f"{name}_osc"] = vi_osc(new_cols[f"{name}_pos"], new_cols[f"{name}_neg"])
    
    df = pd.concat([df, pd.DataFrame(new_cols)], axis=1)
    
    # v1: solves fragmentation issue (keep it under 32)
    #df = df.copy() 
    #print("nblocks after copy:",df._data.nblocks)
    
    return df
