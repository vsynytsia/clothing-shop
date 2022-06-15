from typing import List, Tuple, Union

from tabulate import tabulate
from termcolor import colored

from menu import CommonMenus
from menu import build_menu_with_single_int_choice
from menu.base import BaseMenuWithChoice, BaseMenuWithNoChoice, BaseMenuMixed
from utils import separate_headers_and_items


class WorkerMenus(CommonMenus):
    @staticmethod
    def main_menu(user_name: str) -> BaseMenuWithChoice:
        menu_message = f'Welcome, {user_name}! Choose what you want to do:\n 1) Manage orders\n' \
                       f' 2) Manage clothes\n 3) Manage clothes type\n 4) Manage statuses\n 5) View available clothes\n' \
                       f' 6) View my basket\n 7) View my orders\n 8) Switch users\n 9) Exit application'
        expected_values = list(range(1, 10))

        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def manage_orders_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            orders_message = colored('No orders found. Please, try again later!', 'yellow')
            choices_message = '\n 1) Back to main menu'
            expected_values = [1]

        else:
            headers, items = separate_headers_and_items(select_result)

            orders_message = tabulate(items, headers=headers, tablefmt='psql')
            choices_message = '\n 1) Change order status\n 2) Back to main menu'
            expected_values = [1, 2]

        menu_message = 'Here is list of all orders:\n' + orders_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def change_order_status_menu(existing_order_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Enter id of the order you want to change.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_order_ids)

    @staticmethod
    def specify_new_order_status_menu(existing_status_ids: List[int]) -> BaseMenuWithChoice:
        settings = {
            'choice': {
                'expected_type': 'int',
                'expected_values': existing_status_ids
            }
        }
        menu_message = 'Specify new order status'
        return BaseMenuWithChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def manage_clothes_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            clothes_message = colored('No clothes found. Please, try again later!', 'yellow')
            choices_message = '\n 1) Back to main menu\n 2) Add new clothes'
            expected_values = [1, 2]

        else:
            headers, items = separate_headers_and_items(select_result)

            clothes_message = tabulate(items, headers=headers, tablefmt='psql')
            choices_message = '\n 1) Add new clothes\n 2) Delete clothes\n 3) Restock existing clothes\n' \
                              ' 4) Edit existing clothes info\n 5) Back to main menu '
            expected_values = [1, 2, 3, 4, 5]

        menu_message = 'Here is list of all clothes:\n' + clothes_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def add_clothes_menu(existing_clothes_type_ids: List[int]) -> BaseMenuMixed:
        choice_settings = {
            'clothes_type_id': {
                'expected_type': 'int',
                'expected_values': existing_clothes_type_ids
            }
        }

        no_choice_settings = {
            'title': {
                'expected_type': 'str',
            },
            'description': {
                'expected_type': 'str'
            },
            'size': {
                'expected_type': 'str'
            },
            'material': {
                'expected_type': 'str',
            },
            'color': {
                'expected_type': 'str'
            },
            'price': {
                'expected_type': 'float',
                'additional_validators': [lambda x: x > 0],
                'error_messages': ['Price must be greater than 0. Try again!']
            },
            'discount': {
                'expected_type': 'float',
                'additional_validators': [lambda x: 0 <= x < 100],
                'error_messages': ['Discount must be between 0 and 100. Try again!']
            },
            'in_stock': {
                'expected_type': 'int',
                'additional_validators': [lambda x: x > 0],
                'error_messages': ['In stock amount must be greater than 0. Try again!']
            }
        }

        choice_menu_message = 'Enter information about clothes you want to add.'
        no_choice_menu_message = ''

        return BaseMenuMixed(choice_settings, choice_menu_message, no_choice_settings, no_choice_menu_message)

    @staticmethod
    def remove_clothes_menu(existing_clothes_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Enter id of the clothes you want to delete'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_clothes_ids)

    @staticmethod
    def restock_clothes_menu(existing_clothes_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Enter id of the clothes you want to restock'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_clothes_ids)

    @staticmethod
    def specify_restock_amount_menu() -> BaseMenuWithNoChoice:
        settings = {
            'restock_amount': {
                'expected_type': 'int',
                'additional_validators': [lambda x: x > 0],
                'error_messages': ['Restock amount must be greater than 0. Try again!']
            }
        }
        menu_message = 'Specify new in stock amount'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def manage_clothes_type_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            clothes_type_message = colored('No clothes type available. Please, try again later!', 'yellow')
            choices_messages = '\n 1) Add clothes type\n 2) Back to main menu'
            expected_values = [1, 2]
        else:
            headers, items = separate_headers_and_items(select_result)

            clothes_type_message = tabulate(items, headers=headers, tablefmt='psql')
            choices_messages = '\n 1) Add clothes type\n 2) Remove clothes type\n' \
                               ' 3) Edit existing clothes type info\n 4) Back to main menu'
            expected_values = [1, 2, 3, 4]

        menu_message = 'Here is list of all clothes types:\n' + clothes_type_message + choices_messages
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def add_clothes_type_menu(existing_clothes_types: List[str]) -> BaseMenuWithNoChoice:
        settings = {
            'clothes_type': {
                'expected_type': 'str',
                'additional_validators': [lambda x: x not in existing_clothes_types],
                'error_messages': ['This clothes type already exists. Please, try again!']
            }
        }
        menu_message = 'Specify clothes type you want to add.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def remove_clothes_type_menu(existing_clothes_type_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify clothes type id you want to delete.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_clothes_type_ids)

    @staticmethod
    def change_clothes_type_info_menu(existing_clothes_type_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify clothes type id whose info you want to change.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_clothes_type_ids)

    @staticmethod
    def specify_new_clothes_type_menu(existing_clothes_types: List[str]) -> BaseMenuWithNoChoice:
        settings = {
            'clothes_type': {
                'expected_type': 'str',
                'additional_validators': [lambda x: x not in existing_clothes_types],
                'error_messages': ['This clothes type already exists. Please, try again!']
            }
        }
        menu_message = 'Specify new clothes type.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def change_clothes_info_menu(existing_clothes_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify clothes id whose info you want to change.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_clothes_ids)

    @staticmethod
    def specify_clothes_field_to_change_menu() -> BaseMenuWithChoice:
        menu_message = 'Specify which field you want to change:\n 1) Clothes type id\n 2) Title\n 3) Description\n ' \
                       '4) Size\n 5) Material\n 6) Color\n 7) Price\n 8) Discount\n 9) In stock'
        expected_values = list(range(1, 10))
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def specify_new_clothes_info_menu(settings_key: int, existing_clothes_type_ids: List[int]) \
            -> Union[BaseMenuWithChoice, BaseMenuWithNoChoice]:
        choice_settings = {
            'clothes_type_id': {
                'expected_type': 'int',
                'expected_values': existing_clothes_type_ids
            }
        }
        no_choice_settings = {
            'title': {
                'expected_type': 'str',
            },
            'description': {
                'expected_type': 'str'
            },
            'size': {
                'expected_type': 'str'
            },
            'material': {
                'expected_type': 'str',
            },
            'color': {
                'expected_type': 'str'
            },
            'price': {
                'expected_type': 'float',
                'additional_validators': [lambda x: x > 0],
                'error_messages': ['Price must be greater than 0. Try again!']
            },
            'discount': {
                'expected_type': 'float',
                'additional_validators': [lambda x: 0 <= x < 100],
                'error_messages': ['Discount must be between 0 and 100. Try again!']
            },
            'in_stock': {
                'expected_type': 'int',
                'additional_validators': [lambda x: x > 0],
                'error_messages': ['In stock amount must be greater than 0. Try again!']
            }
        }

        if settings_key == 1:
            menu_message = 'Specify new clothes type id'
            return BaseMenuWithChoice(menu_message=menu_message, settings=choice_settings)

        settings_mapping = {i + 2: {k: v} for i, (k, v) in enumerate(no_choice_settings.items())}
        settings = settings_mapping[settings_key]

        menu_message = f'Specify new {list(settings.keys())[0]}.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def manage_status_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            statuses_message = colored('No statuses available. Please, try again later!', 'yellow')
            choices_messages = '\n 1) Add status\n 2) Back to main menu'
            expected_values = [1, 2]
        else:
            headers, items = separate_headers_and_items(select_result)

            statuses_message = tabulate(items, headers=headers, tablefmt='psql')
            choices_messages = '\n 1) Add status\n 2) Remove status\n' \
                               ' 3) Edit existing status info\n 4) Back to main menu'
            expected_values = [1, 2, 3, 4]

        menu_message = 'Here is list of all clothes types:\n' + statuses_message + choices_messages
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def add_status_menu(existing_statuses: List[str]) -> BaseMenuWithNoChoice:
        settings = {
            'status': {
                'expected_type': 'str',
                'additional_validators': [lambda x: x not in existing_statuses],
                'error_messages': ['This status already exists. Please, try again!']
            }
        }
        menu_message = 'Specify status you want to add.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def remove_status_menu(existing_status_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify id of status you want to delete.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_status_ids)

    @staticmethod
    def change_status_info_menu(existing_status_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify status id whose info you want to change.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_status_ids)

    @staticmethod
    def specify_new_status_menu(existing_statuses: List[str]) -> BaseMenuWithNoChoice:
        settings = {
            'status': {
                'expected_type': 'str',
                'additional_validators': [lambda x: x not in existing_statuses],
                'error_messages': ['This status already exists. Please, try again!']
            }
        }
        menu_message = 'Specify new status.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)
