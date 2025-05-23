DEFAULT_HASH_ALGO = "sha256"  # or "md5"

SYMBOLS = [
    "BTC-USD, ETH-USD, XRP-USD, SOL-USD",
    "DOGE-USD, ADA-USD, TRX-USD, LINK-USD"  
    ]

# (NEW) tsi_signal, nvi_signal, obv_signal, atrp, aroon_osc
ENRICHED_COLUMNS = [
    'date', 'open', 'high', 'low', 'close', 'volume', 'daily_return',
    'daily_log_return', 'ao', 'kama', 'ppo', 'ppo_signal', 'pvo',
    'pvo_signal', 'roc', 'rsi', 'stoch', 'stoch_signal', 'stochrsi',
    'stochrsi_d', 'stochrsi_k', 'tsi', 'tsi_signal', 'uo', 'willr', 'adi', 'cmf', 'emv', 'emv_signal',
    'fi', 'mfi', 'nvi', 'nvi_signal','obv', 'obv_signal', 'vpt', 'vwap', 'atr', 'atrp', 'bb_high',
    'bb_low', 'bb_middle', 'bb_percent', 'bb_width', 'bb_high_indicator',
    'bb_low_indicator', 'dc_high', 'dc_low', 'dc_middle', 'dc_percent',
    'dc_width', 'kc_high', 'kc_low', 'kc_middle', 'kc_percent', 'kc_width',
    'kc_high_indicator', 'kc_low_indicator', 'ui', 'adx', 'adx_neg',
    'adx_pos', 'aroon_down', 'aroon_up', 'aroon_osc', 'cci', 'dpo', 'ema', 'ichimoku_a',
    'ichimoku_b', 'ichimoku_base_line', 'ichimoku_conversion_line', 'kst',
    'kst_sig', 'macd', 'macd_diff', 'macd_signal', 'mi', 'psar_down',
    'psar_up', 'psar_down_indicator', 'psar_up_indicator', 'sma', 'stc',
    'trix', 'vortex_neg', 'vortex_pos', 'wma'
    ]