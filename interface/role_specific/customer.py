from datetime import datetime
from typing import List, Tuple, Optional

from termcolor import colored

from database import Database
from interface import CommonInterface
from menu.role_specific import CustomerMenus
from models import User, BasketClothes, Basket, Order, Clothes
from utils.parse import extract_ids


class CustomerInterface(CommonInterface):
    def __init__(self, database: Database, current_user: User) -> None:
        super().__init__(database=database, menu=CustomerMenus())
        self.current_user = current_user
        self.basket = Basket(contents=[])

    def run(self) -> Optional[User]:
        while True:
            next_action_top = self.interact_with_main_menu()

            if next_action_top == 1:
                self.run_view_available_clothes_menu()
            elif next_action_top == 2:
                self.run_view_my_basket_menu()
            elif next_action_top == 3:
                self.run_view_my_orders_menu()
            elif next_action_top == 4:
                return self.switch_users()
            elif next_action_top == 5:
                break

    def run_view_available_clothes_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_available_clothes_menu()

            if is_empty:
                if next_action == 1:
                    break
            else:
                # add item to basket
                if next_action == 1:
                    next_action = self.add_to_basket_menu()
                    # continue shopping
                    if next_action == 1:
                        continue
                    # checkout
                    elif next_action == 2:
                        next_action = self.interact_with_checkout_menu()
                        # basket confirmed
                        if next_action == 1:
                            next_action = self.checkout()
                            # continue shopping
                            if next_action == 1:
                                continue
                            # back to main menu
                            elif next_action == 2:
                                break
                        # basket not confirmed
                        elif next_action == 2:
                            continue

                    # back to main menu
                    elif next_action == 3:
                        break

                # view my basket or back to main menu
                elif next_action == 2:
                    self.run_view_my_basket_menu()
                    break
                elif next_action == 3:
                    break

    def run_view_my_basket_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_modify_basket_menu()
            if is_empty:
                # start shopping
                if next_action == 1:
                    break
            else:
                # continue shopping
                if next_action == 1:
                    break
                # remove item from basket
                elif next_action == 2:
                    next_action = self.remove_from_basket_menu()
                    # continue shopping
                    if next_action == 1:
                        continue
                    # checkout
                    elif next_action == 2:
                        next_action = self.interact_with_checkout_menu()
                        # basket confirmed
                        if next_action == 1:
                            next_action = self.checkout()
                            # back to main menu
                            if next_action == 1:
                                break
                        # basket not confirmed
                        elif next_action == 2:
                            continue
                    # back to main menu
                    elif next_action == 3:
                        break
                # clear basket
                elif next_action == 3:
                    next_action = self.clear_basket()
                    # back to main menu
                    if next_action == 1:
                        break
                # checkout
                elif next_action == 4:
                    next_action = self.interact_with_checkout_menu()
                    # basket confirmed
                    if next_action == 1:
                        next_action = self.checkout()
                        # back to main menu
                        if next_action == 1:
                            break
                    # basket not confirmed
                    elif next_action == 2:
                        continue

    def run_view_my_orders_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_my_orders_menu()
            if is_empty:
                # back to main menu
                if next_action == 1:
                    break
            else:
                # view specific order
                if next_action == 1:
                    next_action = self.interact_with_view_single_order_menu()
                    if next_action == 1:
                        continue
                # back to main menu
                elif next_action == 2:
                    break

    def interact_with_main_menu(self) -> int:
        return self.show_and_interact_with_menu(
            menu=self.menu.main_menu,
            user_name=self.current_user.first_name)['choice']

    def interact_with_my_orders_menu(self) -> Tuple[bool, int]:
        select_result = self.database.select_user_orders(user_id=self.current_user.id)
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.all_orders_menu,
            select_result=select_result)
        return is_empty, user_input['choice']

    def interact_with_view_single_order_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_user_orders(self.current_user.id))
        order_id = self.show_and_interact_with_menu(
            menu=self.menu.specify_order_id_menu,
            existing_ids=existing_ids)['choice']
        order = self.database.select_single_user_order(order_id)

        return self.show_and_interact_with_menu(
            menu=self.menu.single_order_menu,
            select_result=order)['choice']

    def add_to_basket_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes'))
        clothes = self._interact_with_adding_to_basket_menu(existing_ids=existing_ids)

        if clothes is not None:
            if clothes.id in self.basket.get_ids():
                self.basket.add_existing(clothes)
            else:
                self.basket.add_new(clothes)

            message = colored(f'Successfully added {clothes.quantity} items to your basket', 'green')

        else:
            message = colored(f'You cant order this item no more.', 'red')

        self.basket.print()
        print(message)
        return self._interact_with_post_modify_basket_menu(modify_type='add')

    def remove_from_basket_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes'))

        clothes_id_to_remove = self._interact_with_remove_from_basket_menu(existing_ids=existing_ids)
        basket_clothes_id = self.basket.get_basket_clothes_id_by_clothes_id(clothes_id_to_remove)
        amount_to_remove = self._interact_with_specify_removal_amount_menu(
            clothes=self.basket.contents[basket_clothes_id])

        self.basket.remove_single(clothes_id_to_remove, amount_to_remove)
        print(colored(f'Successfully removed {amount_to_remove} of '
                      f'item #{clothes_id_to_remove} from your basket', 'blue'))

        return self._interact_with_post_modify_basket_menu(modify_type='remove')

    def clear_basket(self) -> int:
        self.basket.contents.clear()
        print(colored('Your basket is now empty.', 'blue'))

        return self._interact_with_post_modify_basket_menu(modify_type='clear')

    def interact_with_modify_basket_menu(self) -> Tuple[bool, int]:
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.modify_basket_menu,
            basket=self.basket)
        return is_empty, user_input['choice']

    def interact_with_checkout_menu(self) -> int:
        return self.show_and_interact_with_menu(menu=self.menu.checkout_menu)['choice']

    def checkout(self) -> int:
        order = Order(self.current_user.id, datetime.now())
        inserted_order_id = self.database.insert_order(order, return_id=True)

        for item in self.basket.contents:
            item_ordered = item.to_item_ordered(inserted_order_id)
            self.database.insert_item_ordered(item_ordered)

        print(colored(f'Thank you for you order! Our manager will contact you very soon', 'blue'))
        self.basket.contents.clear()

        return self._interact_with_post_checkout_menu()

    def _interact_with_remove_from_basket_menu(self, existing_ids: List[int]) -> int:
        return self.show_and_interact_with_menu(
            menu=self.menu.remove_from_basket_menu,
            existing_ids=existing_ids)['choice']

    def _interact_with_specify_removal_amount_menu(self, clothes: BasketClothes) -> int:
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_removal_amount_menu,
            clothes=clothes)['removal_amount']

    def _interact_with_adding_to_basket_menu(self, existing_ids: List[int]) -> Optional[BasketClothes]:
        clothes_id = self.show_and_interact_with_menu(
            menu=self.menu.add_to_basket_menu,
            existing_ids=existing_ids)['choice']
        clothes = self.database.select_clothes_by_id(clothes_id=clothes_id)[0]
        in_basket_quantity = self.basket.get_in_basket_quantity_by_clothes_id(clothes['id'])

        if in_basket_quantity >= clothes['in_stock'] or clothes['in_stock'] <= 0:
            basket_clothes = None
        else:
            quantity = self.show_and_interact_with_menu(
                menu=self.menu.specify_item_quantity_menu,
                in_stock=clothes['in_stock'],
                in_basket_quantity=in_basket_quantity)['quantity']
            basket_clothes = Clothes.to_basket_clothes(clothes=clothes, basket_quantity=quantity)

        return basket_clothes

    def _interact_with_post_modify_basket_menu(self, modify_type: str) -> int:
        return self.show_and_interact_with_menu(
            menu=self.menu.post_modify_basket_menu,
            modify_type=modify_type)['choice']

    def _interact_with_post_checkout_menu(self) -> int:
        return self.show_and_interact_with_menu(menu=self.menu.post_checkout_menu)['choice']
