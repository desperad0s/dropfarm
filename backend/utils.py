def sanitize_data(data):
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items() if k not in ['text']}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    else:
        return data