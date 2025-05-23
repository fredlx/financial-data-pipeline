import pandas as pd

# (TODO) Missing signal_params file and 

import importlib
import scripts.ta.signals.momentum
importlib.reload(scripts.ta.signals.momentum)

import scripts.ta.signals.volume
importlib.reload(scripts.ta.signals.volume)

import scripts.ta.signals.volatility
importlib.reload(scripts.ta.signals.volatility)

import scripts.ta.signals.trend
importlib.reload(scripts.ta.signals.trend)

# Momentum Signals
from scripts.ta.signals.momentum import (
    ao_signals, kama_signals, ppo_signals, pvo_signals, 
    roc_signals, rsi_signals, stoch_signals, stochrsi_signals, 
    tsi_signals, uo_signals, willr_signals 
)

# Volume Signals
from scripts.ta.signals.volume import (
    mfi_signals, cmf_signals, emv_signals, fi_signals,
    nvi_signals, obv_signals, vwap_signals
)

# Volatitlity Signals
from scripts.ta.signals.volatility import (
    bb_signals, dc_signals, kc_signals   
)

# Trend Signals
from scripts.ta.signals.trend import (
    adx_signals, aroon_signals, cci_signals, dpo_signals, ema_signals, 
    sma_signals, wma_signals,kst_signals, macd_signals, 
    mi_signals, psar_signals, trix_signals, vi_signals
    
)

# Computes all signals
def get_all_signals(df):
    
    # (TODO) not necessary anymore (ema_1, ema_2)
    ema_cols = [col for col in df.columns if "ema_" in col]
    sma_cols = [col for col in df.columns if "sma_" in col]
    wma_cols = [col for col in df.columns if "wma_" in col]
    
    # (TODO) refactor logic with *args, **kwargs? or **tuples
    
    new_cols = {}
    
    
    
    
    
    df_signals = pd.concat(
        
        [
            # Momentum
            ao_signals(df['ao']),
            kama_signals(df['kama'], df['close']),
            ppo_signals(df['ppo'], df['ppo_signal']),
            pvo_signals(df['pvo'], df['pvo_signal']),
            roc_signals(df['roc'], overbought=8.0, oversold=-8.0),
            rsi_signals(df['rsi'], overbought=70.0, oversold=30.0),
            stoch_signals(df['stoch'], df['stoch_signal'], overbought=80.0, oversold=20.0),
            stochrsi_signals(df['stochrsi'],df['stochrsi_d'], overbought=0.8, oversold=0.2),
            tsi_signals(df['tsi'], df['tsi_signal']),
            uo_signals(df['uo']),
            willr_signals(df['willr']),
            
            # Volume
            mfi_signals(df['mfi']),
            cmf_signals(df['cmf'], safe_margin=0.05),
            emv_signals(df['emv'], df['emv_signal']),
            fi_signals(df['fi'], df['fi_smooth']),
            nvi_signals(df['nvi'], df['nvi_signal']),
            obv_signals(df['obv'], df['obv_signal']),
            vwap_signals(df['vwap'], df['close']),
            
            # Volatility
            bb_signals(df['close'], df['bb_middle'],df['bb_high_ind'],df['bb_low_ind'],df['bb_width'],bb_width_window=5,squeeze_multiplier=2.0),
            dc_signals(df['close'], df['dc_middle']),
            kc_signals(df['close'], df['kc_middle'], df['kc_high_ind'], df['kc_low_ind']),
            
            # Trend
            adx_signals(df['adx'], df['adx_pos'], df['adx_neg'], adx_threshold=20),
            aroon_signals(df['aroon_up'], df['aroon_down'], df['aroon_osc']),
            cci_signals(df['cci'], df["cci_smooth"], overbought=200, oversold=-200),
            dpo_signals(df['dpo'], df["dpo_smooth"]), 
            ema_signals(df['close'], df["ema_1"], df["ema_2"]),
            sma_signals(df['close'], df["sma_1"], df["sma_2"]),
            wma_signals(df['close'], df["wma_1"], df["wma_2"]),
            kst_signals(df['kst'], df['kst_signal']),
            macd_signals(df['macd'], df['macd_signal'], df["macd_diff"]),
            mi_signals(df['mi'], df["mi_smooth"]),
            psar_signals(df["psar_down"], df["psar_up"], df["psar_down_ind"], df["psar_up_ind"]),
            trix_signals(df['trix'], df['trix_signal']),
            vi_signals(df['vi_pos'], df['vi_neg'])
        
        ], axis=1
    )
    
    if df_signals.empty:
        raise ValueError("df_signals is empty")
    
    return df_signals