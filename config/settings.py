import configparser
import yaml
from pathlib import Path


# config.ini
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

# Get custom/default params
def get_ta_params_file():
    return config["TA_PARAMS"]["filepath"]

# Get symbols, period and interval for extractions
def _get(section: str, key: str):
    return config[section][key]

def get_symbols(is_update: bool =True):
    section = "UPDATE" if is_update else "BACKFILL"
    return [s.strip() for s in _get(section, "symbols").split(",")]

def get_period(is_update: bool =True):
    return _get("UPDATE" if is_update else "BACKFILL", "period")

def get_interval(is_update: bool =True):
    return _get("UPDATE" if is_update else "BACKFILL", "interval")

# Get metadata filepath
def get_metadata_file():
    return config["METADATA"]["filepath"]


# v1: Used in plots
def load_yaml_config(filename: str) -> dict:
    #project_folder = Path(__file__).resolve()
    config_path = Path(__file__).resolve().parents[1] / "config" / filename
    #config_path = Path(__file__).resolve() / "config" / filename
    with config_path.open() as f:
        return yaml.safe_load(f)

# v1
def load_signal_params() -> dict:
    return load_yaml_config("signal_params.yaml")

def load_indicator_params() -> dict:
    return load_yaml_config("indicator_params.yaml")
    
# Usage:
#params = load_signal_params()
#df = stochrsi_signals(stochrsi, stochrsi_d, **params["stochrsi"])


# v2: flattened dictionarity for clarity
# Used in get_indicators 
def load_yaml_config(filename: str) -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / filename
    with config_path.open() as f:
        return yaml.safe_load(f)

def load_flat_params(config: dict, section="main") -> dict:
    flat = {}
    for name, cfg in config.items():
        p = cfg.get("params", {}).get(section, {})
        flat[name] = tuple(p.values()) if isinstance(p, dict) else ()
    return flat

# usage:
#raw_ind_cfg = load_yaml_config("indicator_params.yaml")
#flat_main = load_flat_params(raw_ind_cfg, section="main")
#flat_custom = load_flat_params(raw_ind_cfg, section="custom")