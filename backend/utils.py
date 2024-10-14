import json
from uuid import UUID

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def uuid_json_dumps(data):
    return json.dumps(data, cls=UUIDEncoder)

def sanitize_data(data):
    # Implement your sanitization logic here
    # For example:
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, UUID):
        return str(data)
    else:
        return data
