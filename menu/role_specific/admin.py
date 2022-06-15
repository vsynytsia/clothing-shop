import re
from typing import Tuple, List

from tabulate import tabulate
from termcolor import colored

from menu import CommonMenus
from menu import build_menu_with_single_int_choice
from menu.base import BaseMenuWithChoice, BaseMenuWithNoChoice
from utils.parse import separate_headers_and_items


class AdminMenus(CommonMenus):
    @staticmethod
    def main_menu(user_name: str) -> BaseMenuWithChoice:
        menu_message = f'Welcome, {user_name}! Choose what you want to do:\n 1) Manage users\n' \
                       f' 2) Manage roles\n 3) Manage orders\n' \
                       f' 4) Manage clothes\n 5) Manage clothes type\n 6) View available clothes\n' \
                       f' 7) View my basket\n 8) View my orders\n 9) Switch users\n 10) Exit application'
        expected_values = list(range(1, 11))

        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def manage_users_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            users_message = colored('No users found. Please, try again later!', 'yellow')
            choices_message = '\n 1) Return to main menu'
            expected_values = [1]
        else:
            headers, items = separate_headers_and_items(select_result)

            users_message = tabulate(items, headers, tablefmt='psql')
            choices_message = '\n 1) Change user info\n 2) Delete user\n 3) Back to main menu'
            expected_values = [1, 2, 3]

        menu_message = 'Here is list of all users:\n' + users_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def change_user_info_menu(existing_user_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify user id whose info you want to change.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_user_ids)

    @staticmethod
    def specify_user_field_to_change_menu() -> BaseMenuWithChoice:
        menu_message = 'Specify which field you want to change:\n 1) First name\n 2) Last name\n 3) Phone number\n ' \
                       '4) Email\n 5) Role id'
        expected_values = [1, 2, 3, 4, 5]
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def specify_new_user_info_menu(settings_key: int, existing_role_ids: List[int]) -> BaseMenuWithNoChoice:
        settings_all = {
            'name': {
                'expected_type': 'str',
                'additional_validators': [str.isalpha],
                'error_messages': ['Name must contain only letters of english alphabet. Try again!']
            },
            'last_name': {
                'expected_type': 'str',
                'additional_validators': [str.isalpha],
                'error_messages': ['Last name must contain only letters of english alphabet. Try again!']
            },
            'phone_number': {
                'expected_type': 'str',
                'additional_validators': [str.isnumeric, lambda x: len(x) == 10],
                'error_messages': ['Phone number must contain only digits 0-9. Try again!',
                                   'Phone number length must be 10. Try again!']
            },
            'email': {
                'expected_type': 'str',
                'additional_validators': [lambda x: re.search(r'^\w+_?\w+@\w+[.]\w{2,3}$', x)],
                'error_messages': ['Email must only contains letters of english alphabet, digits 0-9, "@" symbol,'
                                   ' and it must have "." after @. Try again!']
            },
            'role_id': {
                'expected_type': 'int',
                'additional_validators': [lambda x: x in existing_role_ids],
                'error_messages': [f'Expected one of available role ids: {existing_role_ids}.'
                                   f'Try again!']
            }
        }
        settings_mapping = {i + 1: {k: v} for i, (k, v) in enumerate(settings_all.items())}
        settings = settings_mapping[settings_key]

        menu_message = f'Specify new {list(settings.keys())[0]}.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def delete_user_menu(existing_user_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify id of the user you want to delete.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_user_ids)

    @staticmethod
    def manage_roles_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            roles_message = colored('No roles found. Please, try again later!', 'yellow')
            choices_message = '\n 1) Return to main menu\n 2) Add new role'
            expected_values = [1, 2]
        else:
            headers, items = separate_headers_and_items(select_result)

            roles_message = tabulate(items, headers, tablefmt='psql')
            choices_message = '\n 1) Add new role \n 2) Delete role\n 3) Change existing role\n' \
                              ' 4) Back to main menu'
            expected_values = [1, 2, 3, 4]

        menu_message = 'Here is list of all roles:\n' + roles_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def add_role_menu(existing_roles: List[str]) -> BaseMenuWithNoChoice:
        settings = {
            'role': {
                'expected_type': 'str',
                'additional_validators': [str.isalpha,
                                          lambda x: x not in existing_roles],
                'error_messages': ['Role must contain only letters of english alphabet. Try again!',
                                   'This role already exists. Please, try again!']
            }
        }
        menu_message = 'Specify role you want to add.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def delete_role_menu(existing_role_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify id of the role you want to delete.'\
                       + colored('\nWARNING!!! ALL USERS WITH THIS ROLE WILL ALSO BE DELETED', 'red')
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_role_ids)

    @staticmethod
    def change_role_info_menu(existing_role_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify id of the role whose info you want to change.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_role_ids)

    @staticmethod
    def specify_new_role_info_menu(existing_roles: List[str]) -> BaseMenuWithNoChoice:
        settings = {
            'role': {
                'expected_type': 'str',
                'additional_validators': [str.isalpha,
                                          lambda x: x not in existing_roles],
                'error_messages': ['Role must contain only letters of english alphabet. Try again!',
                                   'This role already exists. Please, try again!']
            }
        }
        menu_message = 'Specify new role info.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)
