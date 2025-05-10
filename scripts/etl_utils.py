import pandas as pd
from pathlib import Path
import json


# ---------- INTERVAL HELPERS ----------

def is_intraday(interval: str) -> bool:
    return interval in {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}


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

def update_metadata(time_series, interval, meta, meta_key):
    if time_series.empty:
        raise ValueError("Time series is empty — cannot update metadata.")
    last_dt = time_series.max()
    last_date_str = last_dt.strftime('%Y-%m-%d %H:%M') if is_intraday(interval) else last_dt.strftime('%Y-%m-%d')
    meta[meta_key] = {"last_date": last_date_str}
    save_metadata(meta)


# ---------- FILE LOAD HELPERS ----------

def load_raw_data(symbol, interval, data_dir=Path("data")) -> pd.DataFrame:
    
    base = data_dir / symbol / "raw" / f"{symbol}_{interval}_raw"
    
    for ext in [".parquet", ".csv.gz", ".csv"]:
        path = base.with_suffix(ext)
        
        if path.exists():
            return read_auto_file(path)
    
    raise FileNotFoundError(f"No raw file found for {symbol} with interval {interval}")


def read_auto_file(path: Path) -> pd.DataFrame:
    """Support for CSV, CSV+GZIP, Parquet"""
    
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    suffix = path.suffix.lower()

    if suffix == ".parquet":
        return pd.read_parquet(path)

    elif suffix == ".csv":
        return pd.read_csv(path)

    elif suffix == ".gz":
        # GZIP magic number check
        with open(path, "rb") as f:
            magic = f.read(2)
        if magic != b"\x1f\x8b":
            raise ValueError("File has .gz extension but is not a valid gzip file")
        return pd.read_csv(path, compression="gzip")

    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    
    
