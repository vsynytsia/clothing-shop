from typing import List

from menu.base import BaseMenuWithChoice


def build_menu_with_single_int_choice(menu_message: str, expected_values: List[int]) -> BaseMenuWithChoice:
    settings = {
        'choice': {
            'expected_type': 'int',
            'expected_values': expected_values
        }
    }
    menu = BaseMenuWithChoice(menu_message=menu_message, settings=settings)
    return menu
