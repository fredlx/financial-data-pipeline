#import shutil
import pandas as pd
import yaml
import json
from pathlib import Path
import os
import ast


def safe_eval(val):
    try:
        return ast.literal_eval(val) if pd.notna(val) else () # None
    except Exception:
        return () # None
    
def safe_eval_series(series: pd.Series) -> pd.Series:
    return series.map(safe_eval)


def get_max_window(series, delta=10):
    return pd.Series(series.explode(), dtype="float").max() + delta

def get_timestamps(datetime_series: pd.Series):
    """Returns earliest and latest datetimes (news) as string like '20240419T153015'."""
    datetime_series = pd.to_datetime(datetime_series)  # ensure datetime object
    return datetime_series.min().strftime("%Y%m%dT%H%M"), datetime_series.max().strftime("%Y%m%dT%H%M")


def get_file_size_mb(file_path):
    """Returns file size in MB"""
    return round(os.path.getsize(file_path)/1048576,2)


def normalize_type_for_schema(series: pd.Series) -> str:
    """
    Normalizes pandas dtype for clean schema output to be used outside of Python

    Returns:
    - "string" for string-like columns (even if dtype is object with strings)
    - "list" for columns containing lists
    - "datetime64[ns]" for datetime
    - Native pandas type string for numeric types
    - "object" for everything else
    """
    non_null = series.dropna()
    if non_null.empty:
        return str(series.dtype)
    
    if pd.api.types.is_string_dtype(series):
        return "string"
    elif non_null.dropna().map(type).eq(str).all():
        return "string"
    elif pd.api.types.is_bool_dtype(series) or non_null.map(type).eq(bool).all():
        return "boolean"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime64[ns]"
    elif pd.api.types.is_numeric_dtype(series):
        return str(series.dtype)  # number
    elif non_null.dropna().map(type).eq(list).all():
        return "list"  # array
    elif non_null.map(type).eq(dict).all():
        return "dict"  # object
    else:
        return "object"


def save_schema(
    df, 
    output_path, 
    format="yaml", 
    sample_size=2, 
    normalize_types=True
    ):
    """
    Saves a schema file (.schema.yaml or .schema.json) with:
    - column name, dtype, nullability, sample values
    """
    def safe_sample(series):
        try:
            samples = series.dropna().unique().tolist()[:sample_size]
        except TypeError:
            samples = series.dropna().astype(str).unique().tolist()[:sample_size]
            
        # Convert datetime values to string for YAML readability
        if pd.api.types.is_datetime64_any_dtype(series):
            samples = [pd.Timestamp(x).isoformat() for x in samples]
            
        return samples

    schema = {"columns": []}

    for col in df.columns:
        
        if normalize_types:
            dtype = normalize_type_for_schema(df[col])
        else:
            dtype = str(df[col].dtype)  # pandas dtypes
        nullable = df[col].isnull().any()
        samples = safe_sample(df[col])

        schema["columns"].append({
            "name": col,
            "type": dtype,
            "nullable": bool(nullable),
            "examples": samples
        })

    ext = ".schema.yaml" if format == "yaml" else ".schema.json"
    schema_path = Path(output_path).with_suffix(ext)

    with open(schema_path, "w", encoding="utf-8") as f:
        if format == "yaml":
            yaml.dump(schema, f, sort_keys=False)
        else:
            json.dump(schema, f, indent=2)

    print(f"Schema saved to {schema_path}")


def save_df_to_csv(
    df,
    output_path,
    index=False,
    #mode="w",
    encoding="utf-8",
    create_dirs=True,
    versioned=False,
    compress=False,
    expected_columns=None,
    save_schema_format=None,   #None, yaml, json
    verbose=True
    ):
    """
    Saves a DataFrame to a CSV file with optional versioning, compression, and schema validation.

    Parameters:
    - df: pandas DataFrame to save
    - output_path: str or Path (base path without version suffix)
    - index: write index column (default=False)
    - encoding: file encoding (default='utf-8')
    - create_dirs: create parent dirs if missing
    - versioned: if True, appends a datetime suffix to filename
    - compress: if True, saves file as .csv.gz
    - expected_columns: optional list of columns to validate before saving
    - save_schema_format: if not None, saves schema in specified format 'yaml', 'json'
    """
    if df.empty:
        raise ValueError("Save failed - dataframe is empty")
        #log_and_raise(ValueError, f"Save failed - dataframe is empty", "No data")
    
    output_path = Path(output_path)

    # Schema validation
    if expected_columns:
        missing = set(expected_columns) - set(df.columns)
        if missing:
            raise KeyError(f"Missing expected columns: {missing}")
            #log_and_raise(KeyError, f"Save failed - dataframe missing expected columns: {missing}", "Columns missing")

    # Create parent directories if needed
    if create_dirs:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add timestamp versioning and compression
    if versioned:
        if 'date' not in df.columns:
            raise KeyError("date missing")
            #log_and_raise(KeyError, f"Save failed - 'datetime' not in df columns", "datetime missing")

        start_time, end_time = get_timestamps(df['datetime'])  # lastest news
        base = output_path.stem
        suffix = ".csv.gz" if compress else ".csv"
        output_path = output_path.with_name(f"{base}_{start_time}_{end_time}{suffix}")
    else:
        if compress:
            output_path = output_path.with_suffix(".csv.gz")
        else:
            output_path = output_path.with_suffix(".csv")
            
    # Save the DataFrame
    try:
        df.to_csv(
            output_path, 
            index=index, 
            #mode=mode, 
            encoding=encoding, 
            compression='gzip' if compress else None
            )
        filesize = get_file_size_mb(output_path)
        if verbose:
            print(f"Saved Dataframe to '{output_path}' :: {df.shape} / {filesize} MB")
            #logger.info(f"Saved Dataframe to '{output_path}' :: {df.shape} / {filesize} MB")
        
        # Save schema
        if save_schema_format is not None:
            save_schema(df, output_path, format=save_schema_format)
            if verbose:
                print(f"Saved Schema to '{output_path}'")
                #logger.info(f"Saved Schema to '{output_path}'")
            
        return output_path
            
    except Exception as e:
        msg = f"Failed to save CSV to {output_path}: {e}"
        print(msg)
        #logger.exception(msg)