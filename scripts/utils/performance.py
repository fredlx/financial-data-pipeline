


def safe_inserts(threshold=30):
    """
    monitors fragmentation before and after a function runs, 
    and defragments the DataFrame if needed
    to be used as decorator
    """
    def decorator(func):
        def wrapper(df, *args, **kwargs):
            before = getattr(df._data, "nblocks", None)
            result = func(df, *args, **kwargs)
            after = getattr(result._data, "nblocks", None)

            print(f"[safe_inserts] {func.__name__}: blocks before={before}, after={after}")

            if isinstance(after, int) and after > threshold:
                print(f"[safe_inserts] Defragmenting '{func.__name__}' output")
                return result.copy()
            return result
        return wrapper
    return decorator


def monitor_fragmentation(df, label=""):
    """Prints fragmentation info for a given DataFrame."""
    blocks = getattr(df._data, "nblocks", "N/A")
    print(f"[Fragmentation] {label}: {blocks} blocks")
    return blocks

# usage:
# After a batch of column inserts
#monitor_fragmentation(df, "After indicators batch 1")

# Defrag if needed
#if monitor_fragmentation(df, "Before psar insert") > 30:
#    df = df.copy()
#    monitor_fragmentation(df, "After defrag")