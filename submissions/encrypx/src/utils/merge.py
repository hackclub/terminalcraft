def merge(dict1: dict, dict2: dict) -> dict:
    """
    The merge function merges two dictionaries. If a key is present in both, the value from dict1 is used.
    If a key is only present in one dictionary, it's value will be used as-is.

    Args:
        dict1 (dict): The dictionary that the data is being merged into
        dict2 (dict): The dictionary that contains the data that will be merged.

    Returns:
        A new dictionary containing all the key value pairs from both dicts, combined
    """

    merged = dict1

    for key in dict2:
        if type(dict2[key]) == dict:
            merged[key] = merge(dict1[key] if key in dict1 else {}, dict2[key])

        elif key not in dict1:
            merged[key] = dict2[key]

    return merged
