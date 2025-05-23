import pandas as pd
import ast
import ta
from config.settings import get_ta_params_file

TA_PARAMS_PATH= get_ta_params_file()#"ta_params.csv"

# ---------- HELPERS ----------

# keep it here for self contained script
def safe_eval_series(series: pd.Series) -> pd.Series:
    
    def safe_eval(val):
        try:
            return ast.literal_eval(val) if pd.notna(val) else () # None
        except Exception:
            return () # None
    
    return series.map(safe_eval)


def get_ta_params(ta_params_path, default_params=True):
    params_col = "params_default" if default_params else "params_custom"
    ta_params_df = pd.read_csv(ta_params_path, encoding="utf-8-sig", index_col="short_name")[params_col]
    ta_params_df = safe_eval_series(ta_params_df)
    
    return ta_params_df

def get_prices(df):
    df.columns = [col.lower() for col in df.columns]
    
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise KeyError(f"Missing column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    open = df["open"]
    high = df["high"]
    low = df["low"]
    close = df["close"]
    volume = df["volume"]
    
    return open, high, low, close, volume

# (NOTUSED)
def get_names(df_params):
    """Returns {short_name: name} mapping from ta_params.csv"""
    try:
        df_params.index = df_params["short_name"]
        return df_params["name"].to_dict()
    except Exception as e:
        raise RuntimeError(f"Failed to load names: {e}")
    
    

# ---------- INDICATORS ----------

### MOMENTUM ###

# Awesome Oscilator (AO)
def awesome_oscilator(high, low, window1=5, window2=34, fillna=False):
    return ta.momentum.awesome_oscillator(high, low, window1, window2, fillna)

# Kaufman's Adaptive Moving Average (KAMA)
def kama(close, window=10, pow1=2, pow2=30, fillna=False):
    return ta.momentum.kama(close, window, pow1, pow2, fillna)

# Percentage Price Oscillator (PPO)
def ppo(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    """Percentage Price Oscillator Line"""
    return ta.momentum.ppo(close, window_slow, window_fast, window_sign, fillna)

# PPO histogram
def ppo_hist(close, window_slow=26, window_fast=12, window_sign=9, fillna= False):
    return ta.momentum.ppo_hist(close, window_slow, window_fast, window_sign, fillna)

# PPO signal
def ppo_signal(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    """Percentage Price Oscillator Signal Line - Smoothed PPO"""
    return ta.momentum.ppo_signal(close, window_slow, window_fast, window_sign, fillna)


# Percentage Volume Oscillator (PVO)
def pvo(volume, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    return ta.momentum.pvo(volume, window_slow, window_fast, window_sign, fillna)

# PVO histogram
def pvo_hist(volume, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    return ta.momentum.pvo_hist(volume, window_slow, window_fast, window_sign, fillna)

# PVO signal
def pvo_signal(volume, window_slow=26, window_fast=12, window_sign=9, fillna= False):
    return ta.momentum.pvo_signal(volume, window_slow, window_fast, window_sign, fillna)

# Rate of Change (ROC)
def roc(close, window= 12, fillna= False):
    return ta.momentum.roc(close, window, fillna)

# Relative Strength Index (RSI)
def rsi(close, window=14, fillna=False):
    return ta.momentum.rsi(close, window, fillna)

# Stochastic Oscillator (STOCH %K)
def stoch(high, low, close, window=14, smooth_window=3, fillna=False):
    return ta.momentum.stoch(high, low, close, window, smooth_window, fillna)

# SMA of Stochastic Oscillator (STOCH %D) - stoch_signal
def stoch_signal(high, low, close, window=14, smooth_window=3, fillna=False):
    """SMA of Stochastic Oscillator. Typically a 3 day SMA."""
    return ta.momentum.stoch_signal(high, low, close, window, smooth_window, fillna)

# Stochastic RSI (STOCHRSI)
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi
def stochrsi(close, window=14, smooth1=3, smooth2=3, fillna=False):
    return ta.momentum.stochrsi(close, window, smooth1, smooth2, fillna)

def stochrsi_d(close, window=14, smooth1=3, smooth2=3, fillna= False):
    return ta.momentum.stochrsi_d(close, window, smooth1, smooth2, fillna)

def stochrsi_k(close, window=14, smooth1=3, smooth2=3, fillna=False):
    return ta.momentum.stochrsi_k(close, window, smooth1, smooth2, fillna)

# True strength index (TSI)
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index
def tsi(close, window_slow=25, window_fast=13, fillna=False):
    return ta.momentum.tsi(close, window_slow, window_fast, fillna)

def tsi_signal(tsi, roll_window=10, adjust=False):
    """EMA of True strength index. Typically a 10 period window."""
    return tsi.ewm(span=roll_window, adjust=adjust, min_periods=roll_window).mean()

# Ultimate Oscillator (UO)
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator
def ultimate_oscillator(high, low, close, window1=7, window2=14, window3=28, weight1=4.0, weight2=2.0, weight3=1.0, fillna=False):
    return ta.momentum.ultimate_oscillator(high, low, close, window1, window2, window3, weight1, weight2, weight3, fillna)

# Williams %R (WILLR)
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r
def williams_r(high, low, close, lbp=14, fillna=False):
    return ta.momentum.williams_r(high, low, close, lbp, fillna)


### VOLUME ###

# Accumulation/Distribution Index (ADI) - Chaikin
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line

def acc_dist_index(high, low, close, volume, fillna=False):
    return ta.volume.acc_dist_index(high, low, close, volume, fillna)

# Chaikin Money Flow (CMF) - Chaikin
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf
def chaikin_money_flow(high, low, close, volume, window=20, fillna=False):
    return ta.volume.chaikin_money_flow(high, low, close, volume, window, fillna)

# Money Flow Index (MFI) - Gene Quong and Avrum Soudack
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi
def money_flow_index(high, low, close, volume, window=14, fillna=False):
    return ta.volume.money_flow_index(high, low, close, volume, window, fillna)


# Ease of movement (EMV) - Richard Arms
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv
def ease_of_movement(high, low, volume, window=14, fillna=False):
    return ta.volume.ease_of_movement(high, low, volume, window, fillna)

def sma_ease_of_movement(high, low, volume, window=14, fillna=False):
    return ta.volume.sma_ease_of_movement(high, low, volume, window, fillna)


# Force Index (FI) - Alexander Elder
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index
def force_index(close, volume, window=13, fillna=False):
    return ta.volume.force_index(close, volume, window, fillna)


# Negative Volume Index (NVI) - Paul Dysart
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi
def negative_volume_index(close, volume, fillna=False):
    return ta.volume.negative_volume_index(close, volume, fillna)

def nvi_signal(nvi, roll_window=255, adjust=False):
    """Signal line for NVI: EMA of NVI, typically 255 periods"""
    return nvi.ewm(span=roll_window, adjust=adjust, min_periods=roll_window).mean()


# On-balance volume (OBV) - Joe Granville
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv
def on_balance_volume(close, volume, fillna=False):
    return ta.volume.on_balance_volume(close, volume, fillna)

def obv_signal(obv, roll_window=20):  # or 65
    """Signal line for OBV: SMA of OBV, typically a 20 or 65 SMA"""
    return obv.rolling(window=roll_window).mean()


# Volume-price trend (VPT)
# https://www.investopedia.com/ask/answers/030315/what-volume-price-trend-indicator-vpt-formula-and-how-it-calculated.asp
def volume_price_trend(close, volume, fillna=False):
    return ta.volume.volume_price_trend(close, volume, fillna)


# Volume Weighted Average Price (VWAP) 
# https://academy.ftmo.com/lesson/vwap-technical-indicator/
def volume_weighted_average_price(high, low, close, volume, window=14, fillna=False):
    return ta.volume.volume_weighted_average_price(high, low, close, volume, window, fillna)


### VOLATILITY ###

# Average True Range (ATR) - J. Welles Wilder
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-true-range-atr-and-average-true-range-percent-atrp
def average_true_range(high, low, close, window=14, fillna=False):
    return ta.volatility.average_true_range(high, low, close, window, fillna)

# (TODO) Average True Range Percent (ATRP): include sma flag, window and calculation
def average_true_range_percent(atr, close, use_sma=False, roll_window=20):
    
    if use_sma:
        atrp = atr / close.rolling(window=roll_window).mean() * 100
    else:
        atrp = atr / close * 100
    
    return atrp



# Bollinger Bands (BB) - John Bollinger
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/bollinger-bandwidth

# upper band
def bollinger_hband(close, window=20, window_dev=2, fillna=False): 
    return ta.volatility.bollinger_hband(close, window, window_dev, fillna)

# upper band indicator
def bollinger_hband_indicator(close, window=20, window_dev=2, fillna=False):
    """Returns 1, if close is higher than bollinger high band. Else, return 0."""
    return ta.volatility.bollinger_hband_indicator(close, window, window_dev, fillna)

# lower band
def bollinger_lband(close, window=20, window_dev=2, fillna=False): 
    return ta.volatility.bollinger_lband(close, window, window_dev, fillna)

# lower band indicator
def bollinger_lband_indicator(close, window=20, window_dev=2, fillna=False):
    """Returns 1, if close is lower than bollinger low band. Else, return 0."""
    return ta.volatility.bollinger_lband_indicator(close, window, window_dev, fillna)

# middle band, sma
def bollinger_mavg(close, window=20, fillna=False): 
    return ta.volatility.bollinger_mavg(close, window, fillna)

# percentage band
def bollinger_pband(close, window=20, window_dev=2, fillna=False):
    """Bollinger Channel Percentage Band"""
    return ta.volatility.bollinger_pband(close, window, window_dev, fillna)

# width band
def bollinger_wband(close, window=20, window_dev=2, fillna=False):
    """Bollinger Channel Width Band"""
    return ta.volatility.bollinger_wband(close, window, window_dev, fillna)


# Donchian Channel (DC) - Richard Donchian
# https://www.investopedia.com/terms/d/donchianchannels.asp
# https://trendspider.com/learning-center/donchian-channels-a-comprehensive-guide-for-trend-following-traders/

# upper band
def donchian_channel_hband(high, low, close, h_window=20, offset=0, fillna=False):  
    return ta.volatility.donchian_channel_hband(high, low, close, h_window, offset, fillna)

# lower band
def donchian_channel_lband(high, low, close, l_window=20, offset=0, fillna=False):
    return ta.volatility.donchian_channel_lband(high, low, close, l_window, offset, fillna)

# middle band
def donchian_channel_mband(high, low, close, m_window=10, offset=0, fillna=False):
    return ta.volatility.donchian_channel_mband(high, low, close, m_window, offset, fillna)

# percentage band
def donchian_channel_pband(high, low, close, m_window=10, offset=0, fillna=False):
    return ta.volatility.donchian_channel_pband(high, low, close, m_window, offset, fillna)

# width band
def donchian_channel_wband(high, low, close, m_window=10, offset=0, fillna=False):
    return ta.volatility.donchian_channel_wband(high, low, close, m_window, offset, fillna)


# Keltner Channel (KC)
# # https://trendspider.com/learning-center/keltner-channels-understanding-and-applying-this-classic-technical-indicator/

# upper band
def keltner_channel_hband(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_hband(high, low, close, window, window_atr, fillna, original_version)

# upper band indicator
def keltner_channel_hband_indicator(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_hband_indicator(high, low, close, window, window_atr, fillna, original_version)

# lower band
def keltner_channel_lband(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_lband(high, low, close, window, window_atr, fillna, original_version)

# lower band indicator
def keltner_channel_lband_indicator(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_lband_indicator(high, low, close, window, window_atr, fillna, original_version)

# middle band
def keltner_channel_mband(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_mband(high, low, close, window, window_atr, fillna, original_version)

# percentage band
def keltner_channel_pband(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_pband(high, low, close, window, window_atr, fillna, original_version)

# width band
def keltner_channel_wband(high, low, close, window=20, window_atr=10, fillna=False, original_version=True):
    return ta.volatility.keltner_channel_wband(high, low, close, window, window_atr, fillna, original_version)


# Ulcer Index (ui) - Peter Martin and Byron McCann
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index
def ulcer_index(close, window=14, fillna=False):
    return ta.volatility.ulcer_index(close, window, fillna)

### TREND ### 

# Average Directional Movement Index (ADX) - Welles Wilder
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx

def adx(high, low, close, window=14, fillna=False):
    return ta.trend.adx(high, low, close, window, fillna)

# negative adx (-DI)
def adx_neg(high, low, close, window=14, fillna=False):
    return ta.trend.adx_neg(high, low, close, window, fillna)

# positive adx (+DI)
def adx_pos(high, low, close, window=14, fillna=False):
    return ta.trend.adx_pos(high, low, close, window, fillna)


# Aroon and Aroon Oscillator
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon-oscillator

# Aroon Indicator Negative (AI-)
def aroon_down(close, low, window=25, fillna=False):
    """Identify when trends are likely to change direction (downtrend)."""
    return ta.trend.aroon_down(close, low, window, fillna)

# Aroon Indicator Positive (AI+)
def aroon_up(close, high, window=25, fillna=False):
    """Identify when trends are likely to change direction (uptrend)."""
    return ta.trend.aroon_up(close, high, window, fillna)

# Aroon Oscillator
def aroon_oscillator(aroon_up, aroon_down):
    return aroon_up - aroon_down


# Commodity Channel Index (CCI) - Donald Lambert
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci
def cci(high, low, close, window=20, constant=0.015, fillna=False):
    return ta.trend.cci(high, low, close, window, constant, fillna)


# Detrended Price Oscillator (DPO)
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo

def dpo(close, window=20, fillna=False):
    return ta.trend.dpo(close, window, fillna)


# Exponential Moving Average (EMA)


def ema_indicator(close, window=12, fillna=False):
    return ta.trend.ema_indicator(close, window, fillna)


# Ichimoku Kinkō Hyō (Ichimoku)
def ichimoku_a(high, low, window1=9, window2=26, visual=False, fillna=False):
    return ta.trend.ichimoku_a(high, low, window1, window2, visual, fillna)

def ichimoku_b(high, low, window2=26, window3=52, visual=False, fillna=False):
    return ta.trend.ichimoku_b(high, low, window2, window3, visual, fillna)

def ichimoku_base_line(high, low, window1=9, window2=26, visual=False, fillna=False):
    """Kijun-sen (Base Line)"""
    return ta.trend.ichimoku_base_line(high, low, window1, window2, visual, fillna)

def ichimoku_conversion_line(high, low, window1=9, window2=26, visual=False, fillna=False):
    """Tenkan-sen (Conversion Line)"""
    return ta.trend.ichimoku_conversion_line(high, low, window1, window2, visual, fillna)


# KST Oscillator (KST)
def kst(close, roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15, fillna=False):
    return ta.trend.kst(close, roc1, roc2, roc3, roc4, window1, window2, window3, window4, fillna)

def kst_sig(close, roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15, nsig=9, fillna=False):
    return ta.trend.kst_sig(close, roc1, roc2, roc3, roc4, window1, window2, window3, window4, nsig, fillna)


# Moving Average Convergence Divergence (MACD)
def macd(close, window_slow=26, window_fast=12, fillna=False):
    return ta.trend.macd(close, window_slow, window_fast, fillna)

def macd_diff(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    """Shows the relationship between MACD and MACD Signal."""
    return ta.trend.macd_diff(close, window_slow, window_fast, window_sign, fillna)

def macd_signal(close, window_slow=26, window_fast=12, window_sign=9, fillna=False):
    """Shows EMA of MACD."""
    return ta.trend.macd_signal(close, window_slow, window_fast, window_sign, fillna)


# Mass Index (MI)
def mass_index(high, low, window_fast=9, window_slow=25, fillna=False):
    return ta.trend.mass_index(high, low, window_fast, window_slow, fillna)


# Parabolic Stop and Reverse (Parabolic SAR)
def psar_down(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """Returns the PSAR series with non-N/A values for downward trends"""
    return ta.trend.psar_down(high, low, close, step, max_step, fillna)

def psar_down_indicator(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """Returns 1, if there is a reversal towards an downward trend. Else, returns 0."""
    return ta.trend.psar_down_indicator(high, low, close, step, max_step, fillna)

def psar_up(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """Returns the PSAR series with non-N/A values for upward trends"""
    return ta.trend.psar_up(high, low, close, step, max_step, fillna)

def psar_up_indicator(high, low, close, step=0.02, max_step=0.2, fillna=False):
    """Returns 1, if there is a reversal towards an upward trend. Else, returns 0."""
    return ta.trend.psar_up_indicator(high, low, close, step, max_step, fillna)


# Simple Moving Average (SMA)
def sma_indicator(close, window=12, fillna=False):
    return ta.trend.sma_indicator(close, window, fillna)


# Schaff Trend Cycle (STC)
def stc(close, window_slow=50, window_fast=23, cycle=10, smooth1=3, smooth2=3, fillna=False):
    return ta.trend.stc(close, window_slow, window_fast, cycle, smooth1, smooth2, fillna)


# Triple Exponentially Smoothed Moving Average (TRIX)
def trix(close, window=15, fillna=False):
    return ta.trend.trix(close, window, fillna)


# Vortex Indicator (VI)
def vortex_indicator_neg(high, low, close, window=14, fillna=False):
    return ta.trend.vortex_indicator_neg(high, low, close, window, fillna)

def vortex_indicator_pos(high, low, close, window=14, fillna=False):
    return ta.trend.vortex_indicator_pos(high, low, close, window, fillna)


# Weighted Moving Average (WMA)
def wma_indicator(close, window=9, fillna=False):
    return ta.trend.wma_indicator(close, window, fillna)


### RETURNS ###
def cumulative_return(close, fillna=False):
    return ta.others.cumulative_return(close, fillna)

def daily_log_return(close, fillna=False):
    return ta.others.daily_log_return(close, fillna)

def daily_return(close, fillna=False):
    return ta.others.daily_return(close, fillna)


# (TODO) sharpe ratio

# (TODO) Ulcer Performance Index (UPI), or Martin Ratio.
# https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index


### GET ALL INDICATORS ###

# (TODO) refactor the entire resize df to accept partitioned files and not to pass the entire df if not needed

def slice_df(df, ta_params_path=TA_PARAMS_PATH, default_params=True):
    
    def get_max_window(series, delta=10):
        return pd.Series(series.explode(), dtype="float").max() + delta
        
    ta_params_df = get_ta_params(ta_params_path, default_params)
    max_window = get_max_window(ta_params_df)
    
    df = df.tail(int(max_window)).reset_index(drop=True).copy()
    
    return df
    

def get_all_indicators(df_orig, default_params=True, resize_df=False, ta_params_path=TA_PARAMS_PATH):
    """Returns df with indicators considering csv with params"""
    
    ta_params_df = get_ta_params(ta_params_path, default_params)
    
    # (TODO) needs refactoring to accept partitioned files
    if resize_df:
        df = slice_df(df_orig)
    else:
        df = df_orig.copy()
        
    # Normalizes numeric data 
    open, high, low, close, volume = get_prices(df)
    
    # Awesome Oscilator (AO)
    window1, window2 = ta_params_df.loc["ao"]
    df["ao"] = awesome_oscilator(high, low, window1, window2, fillna=False)

    # Kaufman's Adaptive Moving Average (KAMA)
    window, pow1, pow2 = ta_params_df.loc["kama"]
    df["kama"] = kama(close, window, pow1, pow2, fillna=False)

    # Percentage Price Oscillator (PPO)
    window_slow, window_fast, window_sign = ta_params_df.loc["ppo"]
    df["ppo"] = ppo(close, window_slow, window_fast, window_sign, fillna=False)
    df["ppo_signal"] = ppo_signal(close, window_slow, window_fast, window_sign, fillna=False)

    # Percentage Volume Oscillator (PVO)
    window_slow, window_fast, window_sign = ta_params_df.loc["pvo"]
    df["pvo"] = pvo(volume, window_slow, window_fast, window_sign, fillna=False)
    df["pvo_signal"] = pvo_signal(volume, window_slow, window_fast, window_sign, fillna= False)

    # Rate of Change (ROC)
    window = ta_params_df.loc["roc"]
    df["roc"] = roc(close, window, fillna= False)

    # Relative Strength Index (RSI)
    window = ta_params_df.loc["rsi"]
    df["rsi"] = rsi(close, window, fillna=False)

    # Stochastic Oscillator (STOCH)
    window, smooth_window = ta_params_df.loc["stoch"]
    df["stoch"] = stoch(high, low, close, window, smooth_window, fillna=False)
    df["stoch_signal"] = stoch_signal(high, low, close, window, smooth_window, fillna=False)

    # Stochastic RSI (STOCHRSI)
    window, smooth1, smooth2 = ta_params_df.loc["stochrsi"]
    df["stochrsi"] = stochrsi(close, window, smooth1, smooth2, fillna=False)
    df["stochrsi_d"] = stochrsi_d(close, window, smooth1, smooth2, fillna= False)
    df["stochrsi_k"] = stochrsi_k(close, window, smooth1, smooth2, fillna=False)

    # True strength index (TSI)
    window_slow, window_fast, window_signal = ta_params_df.loc["tsi"]
    df["tsi"] = tsi(close, window_slow, window_fast, fillna=False)
    df["tsi_signal"] = tsi_signal(df["tsi"], window_signal)

    # Ultimate Oscillator (UO)
    window1, window2, window3, weight1, weight2, weight3 = ta_params_df.loc["uo"]
    df["uo"] = ultimate_oscillator(high, low, close, window1, window2, window3, weight1, weight2, weight3, fillna=False)

    # Williams %R (WILLR)
    lbp = ta_params_df.loc["willr"]
    df["willr"] = williams_r(high, low, close, lbp, fillna=False)

    ### VOLUME ###
    # Accumulation/Distribution Index (ADI)
    df["adi"] = acc_dist_index(high, low, close, volume, fillna=False)

    # Chaikin Money Flow (CMF)
    window = ta_params_df.loc["cmf"]
    df["cmf"] = chaikin_money_flow(high, low, close, volume, window, fillna=False)

    # Ease of movement (EMV)
    # (TODO) not sure if sma_ease_of_movement window is the same as emv...
    window, window_signal = ta_params_df.loc["emv"]
    df["emv"] = ease_of_movement(high, low, volume, window, fillna=False)
    df["emv_signal"] = sma_ease_of_movement(high, low, volume, window_signal, fillna=False)

    # Force Index (FI)
    window = ta_params_df.loc["fi"]
    df["fi"] = force_index(close, volume, window, fillna=False)

    # Money Flow Index (MFI)
    window = ta_params_df.loc["mfi"]
    df["mfi"] = money_flow_index(high, low, close, volume, window, fillna=False)

    # Negative Volume Index (NVI)
    df["nvi"] = negative_volume_index(close, volume, fillna=False)

    # On-balance volume (OBV)
    window_signal = ta_params_df.loc["obv"]
    df["obv"] = on_balance_volume(close, volume, fillna=False)
    df['obv_signal'] = obv_signal(df["obv"], window_signal)

    # Volume-price trend (VPT)
    df["vpt"] = volume_price_trend(close, volume, fillna=False)

    # Volume Weighted Average Price (VWAP)
    window = ta_params_df.loc["vwap"]
    df["vwap"] = volume_weighted_average_price(high, low, close, volume, window, fillna=False)


    ### VOLATILITY ###
    
    # ATR
    window = ta_params_df.loc["atr"]
    df["atr"] = average_true_range(high, low, close, window, fillna=False)
    df['atrp'] = average_true_range_percent(df['atr'], close)

    # Bollinger Bands (BB)
    window, window_dev = ta_params_df.loc["bb"]
    df["bb_high"] = bollinger_hband(close, window, window_dev, fillna=False)
    df["bb_low"] = bollinger_lband(close, window, window_dev, fillna=False)
    df["bb_middle"] = bollinger_mavg(close, window, fillna=False)
    df["bb_percent"] = bollinger_pband(close, window, window_dev, fillna=False)
    df["bb_width"] = bollinger_wband(close, window, window_dev, fillna=False)
    df["bb_high_indicator"] = bollinger_hband_indicator(close, window, window_dev, fillna=False)
    df["bb_low_indicator"] = bollinger_lband_indicator(close, window, window_dev, fillna=False)

    # Donchian Channel (DC)
    h_window, l_window, m_window, offset = ta_params_df.loc["dc"]
    df["dc_high"] =  donchian_channel_hband(high, low, close, h_window, offset, fillna=False)
    df["dc_low"] =  donchian_channel_lband(high, low, close, l_window, offset, fillna=False)
    df["dc_middle"] = donchian_channel_mband(high, low, close, m_window, offset, fillna=False)
    df["dc_percent"] = donchian_channel_pband(high, low, close, m_window, offset, fillna=False)
    df["dc_width"] = donchian_channel_wband(high, low, close, m_window, offset, fillna=False)

    # Keltner Channel (KC)
    window, window_atr = ta_params_df.loc["kc"]
    df["kc_high"] =  keltner_channel_hband(high, low, close, window, window_atr, fillna=False, original_version=True)
    df["kc_low"] = keltner_channel_lband(high, low, close, window, window_atr, fillna=False, original_version=True)
    df["kc_middle"] = keltner_channel_mband(high, low, close, window, window_atr, fillna=False, original_version=True)
    df["kc_percent"] = keltner_channel_pband(high, low, close, window, window_atr, fillna=False, original_version=True)
    df["kc_width"] = keltner_channel_wband(high, low, close, window, window_atr, fillna=False, original_version=True)
    df["kc_high_indicator"] = keltner_channel_hband_indicator(high, low, close, window, window_atr, fillna=False, original_version=True)
    df["kc_low_indicator"] = keltner_channel_lband_indicator(high, low, close, window, window_atr, fillna=False, original_version=True)

    # Ulcer Index (ui)
    window = ta_params_df.loc["ui"]
    df["ui"] = ulcer_index(close, window, fillna=False)

    ### TREND ### 
    # Average Directional Movement Index (ADX)
    window = ta_params_df.loc["adx"]
    df["adx"] =  adx(high, low, close, window, fillna=False)
    df["adx_neg"] = adx_neg(high, low, close, window, fillna=False)
    df["adx_pos"] = adx_pos(high, low, close, window, fillna=False)

    # Aroon Indicator (AI)
    window = ta_params_df.loc["ai"]
    df["aroon_down"] = aroon_down(close, low, window, fillna=False)
    df["aroon_up"] = aroon_up(close, high, window, fillna=False)
    df["aroon_osc"] = aroon_oscillator(df["aroon_up"], df["aroon_down"])

    # Commodity Channel Index (CCI)
    window, constant = ta_params_df.loc["cci"]
    df["cci"] = cci(high, low, close, window, constant, fillna=False)

    # Detrended Price Oscillator (DPO)
    window = ta_params_df.loc["dpo"]
    df["dpo"] = dpo(close, window, fillna=False)

    # Exponential Moving Average (EMA)
    window1, window2 = ta_params_df.loc["ema"]
    df[f"ema_{window1}"] = ema_indicator(close, window1, fillna=False)
    df[f"ema_{window2}"] = ema_indicator(close, window2, fillna=False)
    
    # Simple Moving Average (SMA)
    window1, window2 = ta_params_df.loc["sma"]
    df[f"sma_{window1}"] = sma_indicator(close, window1, fillna=False)
    df[f"sma_{window2}"] = sma_indicator(close, window2, fillna=False)

    # Ichimoku Kinkō Hyō (Ichimoku)
    window1, window2, window3 = ta_params_df.loc["ichimoku"]
    df["ichimoku_a"] = ichimoku_a(high, low, window1, window2, visual=False, fillna=False)
    df["ichimoku_b"] = ichimoku_b(high, low, window2, window3, visual=False, fillna=False)
    df["ichimoku_base_line"] = ichimoku_base_line(high, low, window1, window2, visual=False, fillna=False)
    df["ichimoku_conversion_line"] = ichimoku_conversion_line(high, low, window1, window2, visual=False, fillna=False)

    # KST Oscillator (KST)
    roc1, roc2, roc3, roc4, window1, window2, window3, window4, nsig = ta_params_df.loc["kst"]
    df["kst"] = kst(close, roc1, roc2, roc3, roc4, window1, window2, window3, window4, fillna=False)
    df["kst_sig"] = kst_sig(close, roc1, roc2, roc3, roc4, window1, window2, window3, window4, nsig, fillna=False)

    # Moving Average Convergence Divergence (MACD)
    window_fast, window_slow, window_sign = ta_params_df.loc["macd"]
    df["macd"] = macd(close, window_slow, window_fast, fillna=False)
    df["macd_diff"] = macd_diff(close, window_slow, window_fast, window_sign, fillna=False)
    df["macd_signal"] = macd_signal(close, window_slow, window_fast, window_sign, fillna=False)

    # Mass Index (MI)
    window_slow, window_fast = ta_params_df.loc["mi"]
    df["mi"] = mass_index(high, low, window_fast, window_slow, fillna=False)

    # Parabolic Stop and Reverse (Parabolic SAR)
    step, max_step = ta_params_df.loc["psar"]
    df["psar_down"] = psar_down(high, low, close, step, max_step, fillna=False)
    df["psar_up"] = psar_up(high, low, close, step, max_step, fillna=False)
    df["psar_down_indicator"] = psar_down_indicator(high, low, close, step, max_step, fillna=False)
    df["psar_up_indicator"] = psar_up_indicator(high, low, close, step, max_step, fillna=False)

    

    # Schaff Trend Cycle (STC)
    window_slow, window_fast, cycle, smooth1, smooth2 = ta_params_df.loc["stc"]
    df["stc"] = stc(close, window_slow, window_fast, cycle, smooth1, smooth2, fillna=False)

    # Triple Exponentially Smoothed Moving Average (TRIX)
    window = ta_params_df.loc["trix"]
    df["trix"] = trix(close, window, fillna=False)

    # Vortex Indicator (VI)
    window = ta_params_df.loc["vi"]
    df["vortex_neg"] = vortex_indicator_neg(high, low, close, window, fillna=False)
    df["vortex_pos"] = vortex_indicator_pos(high, low, close, window, fillna=False)

    # Weighted Moving Average (WMA)
    window = ta_params_df.loc["wma"]
    df["wma"] = wma_indicator(close, window, fillna=False)

    return df