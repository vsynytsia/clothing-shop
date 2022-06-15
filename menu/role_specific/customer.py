from typing import List, Tuple

from tabulate import tabulate
from termcolor import colored

from menu import CommonMenus
from menu import build_menu_with_single_int_choice
from menu.base import BaseMenuWithChoice, BaseMenuWithNoChoice
from models import Basket, BasketClothes
from utils.parse import separate_headers_and_items


class CustomerMenus(CommonMenus):
    @staticmethod
    def main_menu(user_name: str) -> BaseMenuWithChoice:
        menu_message = f'Welcome, {user_name}! Choose what you want to do:\n 1) View available clothes\n' \
                       f' 2) View my basket\n 3) View my orders\n 4) Switch users\n 5) Exit application'
        expected_values = [1, 2, 3, 4, 5]

        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def clothes_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(select_result) == 0):
            clothes_message = colored('No clothes currently available. Please, try again later!', 'yellow')
            choices_message = '\n 1) View my basket\n 2) Back to main menu'
            expected_values = [1, 2]

        else:
            headers, items = separate_headers_and_items(select_result)

            clothes_message = tabulate(items, headers=headers, tablefmt='psql')
            choices_message = '\n 1) Add item to basket\n 2) View my basket\n 3) Back to main menu'
            expected_values = [1, 2, 3]

        menu_message = 'Here is list of all available clothes:\n' + clothes_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def specify_order_id_menu(existing_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Specify order id.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_ids)

    @staticmethod
    def all_orders_menu(select_result: List[dict]) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := len(select_result) == 0:
            orders_message = colored('You have no orders yet.', 'yellow')
            choices_message = '\n 1) Back to main menu'
            expected_values = [1]
        else:
            headers, items = separate_headers_and_items(select_result)

            orders_message = tabulate(items, headers=headers, tablefmt='psql')
            choices_message = '\n 1) View specific order\n 2) Back to main menu'
            expected_values = [1, 2]

        menu_message = 'Here is list of all your orders:\n' + orders_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def single_order_menu(select_result: List[dict]) -> BaseMenuWithChoice:
        headers, items = separate_headers_and_items(select_result)
        choices_message = '\n 1) Back to my orders menu'

        menu_message = tabulate(items, headers=headers, tablefmt='psql') + choices_message
        expected_values = [1]

        return build_menu_with_single_int_choice(menu_message, expected_values=expected_values)

    @staticmethod
    def specify_item_quantity_menu(in_stock: int, in_basket_quantity: int) -> BaseMenuWithNoChoice:
        settings = {
            'quantity': {
                'expected_type': 'int',
                'additional_validators': [lambda x: (x + in_basket_quantity) <= in_stock,
                                          lambda x: x > 0],
                'error_messages': [f'You cant order more than {in_stock} of this item. Please, try again!',
                                   'Item quantity must be > 0. Try again!']
            }
        }

        menu_message = 'Choose amount items you want to order.'
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def add_to_basket_menu(existing_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Enter id of the item you want to add to your basket.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_ids)

    @staticmethod
    def remove_from_basket_menu(existing_ids: List[int]) -> BaseMenuWithChoice:
        menu_message = 'Enter id of the item you want to delete from your basket.'
        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=existing_ids)

    @staticmethod
    def specify_removal_amount_menu(clothes: BasketClothes) -> BaseMenuWithNoChoice:
        menu_message = 'Enter amount you want to delete from your basket.'
        settings = {
            'removal_amount': {
                'expected_type': 'int',
                'additional_validators': [lambda x: x <= clothes.quantity,
                                          lambda x: x > 0],
                'error_messages': [f'You cannot delete more than {clothes.quantity} of this item. Try again!',
                                   f'Removal amount must be > 0. Try again!']
            }
        }
        return BaseMenuWithNoChoice(menu_message=menu_message, settings=settings)

    @staticmethod
    def checkout_menu() -> BaseMenuWithChoice:
        menu_message = 'Check your basket again. Do you confirm your order?\n 1) Yes\n 2) No'
        expected_values = [1, 2]

        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def post_checkout_menu() -> BaseMenuWithChoice:
        menu_message = 'Choose what you want to do next.\n 1) Back to main menu'
        expected_values = [1]

        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

    @staticmethod
    def modify_basket_menu(basket: Basket) -> Tuple[bool, BaseMenuWithChoice]:
        if is_empty := (len(basket.get_contents()) == 0):
            basket_message = colored('Your basket is currently empty', 'yellow')
            choices_message = '\n 1) Back to main menu'
            expected_values = [1]

        else:
            basket_total = basket.calculate_basket_total()

            basket_message = f'{basket.get_tabulated_contents()}\nCurrent basket total: {basket_total}'
            choices_message = '\n 1) Back to main menu\n 2) Remove item from basket\n 3) Clear basket\n 4) Checkout'
            expected_values = [1, 2, 3, 4]

        menu_message = 'This is your basket:\n' + basket_message + choices_message
        menu = build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)

        return is_empty, menu

    @staticmethod
    def post_modify_basket_menu(modify_type: str) -> BaseMenuWithChoice:
        if modify_type == 'clear':
            menu_message = 'Choose what you want to do next:\n 1) Back to main menu'
            expected_values = [1]
        else:
            menu_message = 'Choose what you want to do next:\n 1) Continue shopping\n 2) Checkout\n' \
                           ' 3) Back to main menu'
            expected_values = [1, 2, 3]

        return build_menu_with_single_int_choice(menu_message=menu_message, expected_values=expected_values)
