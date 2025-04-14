from dataclasses import asdict, is_dataclass



def to_serializable(obj):
    """
    Recursively convert dataclass instances or other objects to dictionaries
    so they can be JSON serialized.
    """
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    # For any other type, try to convert it or simply return it
    return obj
