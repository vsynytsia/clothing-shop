def calculate_single_item_total(quantity: int, price: float, discount: float) -> float:
    return quantity * price * (1 - discount / 100)


def rename_dict_key(dict_: dict, old_key, new_key) -> dict:
    return {new_key if k == old_key else k: v for k, v in dict_.items()}
