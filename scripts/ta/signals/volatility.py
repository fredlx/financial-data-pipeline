import pandas as pd
import numpy as np

# (TODO) some params are hardcoded!
# move helpres to ta_helpers

import importlib
import scripts.ta.ta_helpers
importlib.reload(scripts.ta.ta_helpers)


from scripts.ta.ta_helpers import (
    validate_and_align_series,
    line_cross, 
    trend_status,
    obos_status,
    above_threshold
    )


# Bollinger Bands (BB)
def bb_signals(
    close: pd.Series,
    bb_middle: pd.Series,
    bb_high_ind: pd.Series,
    bb_low_ind: pd.Series,
    bb_width: pd.Series,
    bb_width_window: int = 5,
    squeeze_multiplier: float = 2.0,
    name: str = "bb"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {
            'bb_width': bb_width, 
            'bb_middle': bb_middle,
            'close': close,
            'bb_high_ind': bb_high_ind,
            'bb_low_ind': bb_low_ind,
        }
    )
    
    bb_width = series['bb_width']
    bb_middle = series['bb_middle']
    close = series['close']
    bb_high_ind = series['bb_high_ind']
    bb_low_ind = series['bb_low_ind']
    
    def bb_breakout_signal(
        bb_width: pd.Series, 
        bb_width_window: int, 
        squeeze_multiplier: float
    ) -> pd.Series:
        """
        Squeeze breakout.
        Signal = 1 if today's BB width > squeeze_multiplier × min(BB width from n previous periods)
        """
        previous_n_min = bb_width.shift(1).rolling(window=bb_width_window).min()
        signal = (bb_width > previous_n_min * squeeze_multiplier).astype(int)  # 1 or 0
        
        return signal

    signals = {
        f"{name}_squeeze_break": bb_breakout_signal(bb_width, bb_width_window, squeeze_multiplier),
        f"{name}_hbreak": bb_high_ind,
        f"{name}_lbreak": bb_low_ind,
        f"{name}_center_cross": line_cross(close, signal=bb_middle),
        f"{name}_trend": trend_status(close, baseline=bb_middle),
        
    }
    
    return pd.DataFrame(signals)

# Donchian Channel (DC)
def dc_signals(
    close: pd.Series,
    dc_middle: pd.Series,
    name: str = "dc"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {"close": close, "dc_middle": dc_middle}
    )
    
    close = series["close"]
    dc_middle = series["dc_middle"]
    
    signals = {
        f"{name}_center_cross": line_cross(close, signal=dc_middle),
        f"{name}_trend": trend_status(close, baseline=dc_middle),
    }
    
    return pd.DataFrame(signals)

# Keltner Channels (KC)
def kc_signals(
    close: pd.Series,
    kc_middle: pd.Series,
    kc_high_ind: pd.Series,
    kc_low_ind: pd.Series,
    name: str = "kc"
) -> pd.DataFrame:
    series = validate_and_align_series(
        {
            "close": close, 
            "kc_middle": kc_middle,
            'kc_high_ind': kc_high_ind,
            'kc_low_ind': kc_low_ind,
        }
    )
    
    close = series["close"]
    kc_middle = series["kc_middle"]
    kc_high_ind = series["kc_high_ind"]
    kc_low_ind = series["kc_low_ind"]
    
    signals = {
        f"{name}_hbreak": kc_high_ind,
        f"{name}_lbreak": kc_low_ind,
        f"{name}_center_cross": line_cross(close, signal=kc_middle),
        f"{name}_trend": trend_status(close, baseline=kc_middle),
    }
    
    return pd.DataFrame(signals)

# (TODO) Ulcer Index: measures volatility - specifically drawdown potential, 
# maybe come up with high, med, low function