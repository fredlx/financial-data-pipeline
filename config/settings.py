import configparser
from pathlib import Path

def load_config(filename="config.ini", folder="config"):
    """Loads configuration from config file."""
    project_root = Path(__file__).resolve().parents[1]
    config_path = project_root / folder / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

config = load_config()


def get_ta_params_file():
    return config["TA_PARAMS"]["filepath"]


def _get(section: str, key: str):
    return config[section][key]

def get_symbols(is_update: bool =True):
    section = "UPDATE" if is_update else "BACKFILL"
    return [s.strip() for s in _get(section, "symbols").split(",")]

def get_period(is_update: bool =True):
    return _get("UPDATE" if is_update else "BACKFILL", "period")

def get_interval(is_update: bool =True):
    return _get("UPDATE" if is_update else "BACKFILL", "interval")