from typing import List, Tuple, Any


def extract_all_values_from_list_of_dicts(list_of_dicts: List[dict], flatten: bool = False) -> List[Any]:
    result = [[value for value in list(dict_.values())] for dict_ in list_of_dicts]
    if flatten:
        result = sum(result, [])
    return result


def separate_headers_and_items(select_result: List[dict]) -> Tuple[List[str], List[List[Any]]]:
    headers = list(select_result[0].keys())
    items = extract_all_values_from_list_of_dicts(select_result)

    return headers, items


def extract_ids(select_result: List[dict]) -> List[int]:
    ids = [dict_['id'] for dict_ in select_result]
    return ids
