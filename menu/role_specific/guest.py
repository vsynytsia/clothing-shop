from typing import List, Tuple

from tabulate import tabulate
from termcolor import colored

from menu import CommonMenus
from menu import build_menu_with_single_int_choice
from menu.base import BaseMenuWithChoice
from utils import separate_headers_and_items


class GuestMenus(CommonMenus):
    @staticmethod
    def clothes_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            clothes_message = colored('No clothes currently available. Please, try again later!', 'yellow')
        else:
            headers, items = separate_headers_and_items(select_result=select_result)
            clothes_message = tabulate(items, headers=headers, tablefmt='psql')
        choices_message = '\n 1) Back to start menu'

        menu_message = 'Here is list of all available clothes:\n' + clothes_message + choices_message
        expected_values = [1]
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu
