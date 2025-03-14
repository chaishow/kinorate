def snakecase(s):
    """Преобразует строку из camelCase в snake_case."""
    return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')


def parse_keys_to_snake_case(data_dict):
    return {snakecase(key): value for key, value in data_dict.items()}