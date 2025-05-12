import pandas as pd
from pathlib import Path
import json


# ---------- INTERVAL HELPERS ----------

def is_intraday(interval: str) -> bool:
    return interval in {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}


def yf_interval_to_pandas_freq(yf_interval: str) -> str:
    """
    Convert yfinance interval (e.g. '15m', '1d') to pandas frequency string (e.g. '15T', 'D')
    """
    yf_interval = yf_interval.lower().strip()

    mapping = {
        "1m": "T",     # minute
        "2m": "2T",
        "5m": "5T",
        "15m": "15T",
        "30m": "30T",
        "60m": "60T",
        "90m": "90T",
        "1h": "60T",
        "1d": "D",
        "5d": "5D",
        "1wk": "W",
        "1mo": "M",
        "3mo": "3M",
    }

    if yf_interval not in mapping:
        raise ValueError(f"Unsupported yfinance interval: '{yf_interval}'")

    return mapping[yf_interval]


# (NOTUSED)
def infer_interval_from_series(time_series: pd.Series):
    """Infer interval from time series. Returns (label, timedelta)."""
    s = time_series.sort_values()
    diffs = s.diff().dropna()

    if diffs.empty:
        raise ValueError("Not enough data to infer interval.")

    try:
        delta = diffs.mode()[0]
    except IndexError:
        delta = diffs.median()

    minutes = delta.total_seconds() / 60

    if minutes <= 1:
        label = '1m'
    elif minutes <= 2:
        label = '2m'
    elif minutes <= 5:
        label = '5m'
    elif minutes <= 15:
        label = '15m'
    elif minutes <= 30:
        label = '30m'
    elif minutes <= 60:
        label = '60m'
    elif minutes <= 90:
        label = '90m'
    elif minutes <= 1440:
        label = '1d'
    elif minutes <= 7200:
        label = '5d'
    elif minutes <= 10080:
        label = '1wk'
    elif minutes <= 44640:
        label = '1mo'
    elif minutes <= 133920:
        label = '3mo'
    else:
        raise ValueError(f"Unsupported interval: {delta}")

    return label#, delta


# ---------- METADATA HELPERS ----------

# (TODO) move to settings/config.ini
META_FILE = Path("data/meta/last_date_per_symbol.json")


def load_metadata():
    if META_FILE.exists():
        with open(META_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(meta: dict):
    META_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(META_FILE, 'w') as f:
        json.dump(meta, f, indent=2)

def update_metadata(time_series, symbol, interval):
    if time_series.empty:
        raise ValueError("Time series is empty — cannot update metadata.")
    
    meta = load_metadata()
    meta_key = f"{symbol}_{interval}"
    
    time_series = pd.to_datetime(time_series)
    last_dt = time_series.max()
    last_date_str = last_dt.strftime('%Y-%m-%d %H:%M') if is_intraday(interval) else last_dt.strftime('%Y-%m-%d')
    meta[meta_key] = {"last_date": last_date_str}
    save_metadata(meta)


# ---------- FILE LOAD HELPERS ----------


def read_auto_file(path: Path) -> pd.DataFrame:
    
    path = Path(path)  # fix for/from airflow
    
    if not path.exists():
        raise FileNotFoundError(f"{path.resolve()} not found")

    suffix = path.suffix.lower()

    if suffix == ".parquet":
        return pd.read_parquet(path)

    elif suffix in {".csv", ".gz"}:
        # Read first 2 bytes to detect gzip
        with open(path, "rb") as f:
            magic = f.read(2)

        compression = "gzip" if magic == b"\x1f\x8b" else None
        return pd.read_csv(path, compression=compression)

    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    
    
