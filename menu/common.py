import re
from abc import ABC

from menu import build_menu_with_single_int_choice
from menu.base import BaseMenuWithChoice, BaseMenuWithNoChoice


class CommonMenus(ABC):
    @staticmethod
    def start_menu() -> BaseMenuWithChoice:
        menu_message = 'Choose one of the options:\n 1) Sign in\n 2) Sign up\n 3) Continue as guest'
        expected_values = [1, 2, 3]
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def sign_in_menu() -> BaseMenuWithNoChoice:
        settings = {
            'email': {
                'expected_type': 'str',
                'validate': False
            },
            'password': {
                'expected_type': 'str',
                'validate': False,
            }
        }
        menu_message = 'You chose to sign in. Follow the commands!'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def sign_up_menu() -> BaseMenuWithNoChoice:
        settings = {
            'name': {
                'expected_type': 'str',
                'additional_validators': [str.isalpha],
                'error_messages': ['Name must contain only letters of english alphabet. Try again!']
            },
            'last name': {
                'expected_type': 'str',
                'additional_validators': [str.isalpha],
                'error_messages': ['Last name must contain only letters of english alphabet. Try again!']
            },
            'phone number': {
                'expected_type': 'str',
                'additional_validators': [str.isnumeric,
                                          lambda x: len(x) == 10],
                'error_messages': ['Phone number must contain only digits 0-9. Try again!',
                                   'Phone number length must be 10. Try again!']
            },
            'email': {
                'expected_type': 'str',
                'additional_validators': [lambda x: re.search(r'^\w+_?\w+@\w+[.]\w{2,3}$', x)],
                'error_messages': ['Email must only contains letters of english alphabet, digits 0-9, @ symbol,'
                                   ' and it must have . after @. Try again!']
            },
            'password': {
                'expected_type': 'str',
                'additional_validators': [lambda x: ' ' not in x,
                                          lambda x: len(x) > 5],
                'error_messages': ['Password must not contain spaces. Try again!',
                                   'Password length must be > 5. Try again!'],
                'confirm': True
            }
        }

        menu_message = 'You chose to sign up. Follow the commands!'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)
