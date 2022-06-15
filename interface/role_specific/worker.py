from typing import Tuple, Union, Optional

from termcolor import colored

from database import Database
from interface import CommonInterface
from interface.role_specific import CustomerInterface
from menu.role_specific import WorkerMenus
from models import User, Clothes, ClothesType, Status
from utils.parse import extract_ids, extract_all_values_from_list_of_dicts


class WorkerInterface(CommonInterface):
    def __init__(self, database: Database, current_user: User) -> None:
        super().__init__(database, menu=WorkerMenus())
        self.current_user = current_user

    def run(self) -> Optional[User]:
        lower_level_interfaces = {
            'customer': CustomerInterface(database=self.database, current_user=self.current_user)
        }

        while True:
            next_action_top = self.interact_with_main_menu()

            if next_action_top == 1:
                self.run_manage_orders_menu()
            elif next_action_top == 2:
                self.run_manage_clothes_menu()
            elif next_action_top == 3:
                self.run_manage_clothes_type_menu()
            elif next_action_top == 4:
                self.run_manage_status_menu()
            elif next_action_top == 5:
                lower_level_interfaces['customer'].run_view_available_clothes_menu()
            elif next_action_top == 6:
                lower_level_interfaces['customer'].run_view_my_basket_menu()
            elif next_action_top == 7:
                lower_level_interfaces['customer'].run_view_my_orders_menu()
            elif next_action_top == 8:
                return self.switch_users()
            elif next_action_top == 9:
                break

    def run_manage_orders_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_manage_orders_menu()

            if is_empty:
                if next_action == 1:
                    break
            else:
                if next_action == 1:
                    self.change_order_status()
                elif next_action == 2:
                    break

    def run_manage_clothes_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_manage_clothes_menu()

            if is_empty:
                if next_action == 1:
                    break
                elif next_action == 2:
                    self.add_clothes()
            else:
                if next_action == 1:
                    self.add_clothes()
                elif next_action == 2:
                    self.remove_clothes()
                elif next_action == 3:
                    self.restock_clothes()
                elif next_action == 4:
                    self.change_clothes_info()
                elif next_action == 5:
                    break

    def run_manage_clothes_type_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_manage_clothes_type_menu()

            if is_empty:
                if next_action == 1:
                    self.add_clothes_type()
                elif next_action == 2:
                    break
            else:
                if next_action == 1:
                    self.add_clothes_type()
                elif next_action == 2:
                    self.remove_clothes_type()
                elif next_action == 3:
                    self.change_clothes_type_info()
                elif next_action == 4:
                    break

    def run_manage_status_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_manage_status_menu()

            if is_empty:
                if next_action == 1:
                    self.add_status()
                elif next_action == 2:
                    break
            else:
                if next_action == 1:
                    self.add_status()
                elif next_action == 2:
                    self.remove_status()
                elif next_action == 3:
                    self.change_status_info()
                elif next_action == 4:
                    break

    def interact_with_main_menu(self) -> int:
        return self.show_and_interact_with_menu(
            menu=self.menu.main_menu,
            user_name=self.current_user.first_name)['choice']

    def interact_with_manage_orders_menu(self) -> Tuple[bool, int]:
        available_orders = self.database.select_all_columns_from_table(table='order')
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.manage_orders_menu,
            select_result=available_orders)

        return is_empty, user_input['choice']

    def change_order_status(self) -> None:
        order_id = self._interact_with_change_order_status_menu()
        new_order_status = self._interact_with_specify_new_order_status_menu()

        self.database.update_value_by_id(table='`order`', column='status_id', new_value=new_order_status, id_=order_id)
        print(colored(f'Successfully status of order "{order_id}" to "{new_order_status}"', 'blue'))

    def interact_with_manage_clothes_menu(self) -> Tuple[bool, int]:
        available_clothes = self.database.select_all_columns_from_table(table='clothes')
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.manage_clothes_menu,
            select_result=available_clothes)

        return is_empty, user_input['choice']

    def add_clothes(self) -> None:
        clothes = self._interact_with_add_clothes_menu()
        self.database.insert_clothes(clothes=clothes, return_id=False)
        print(colored('Clothes was successfully inserted!', 'blue'))

    def remove_clothes(self) -> None:
        clothes_id_to_remove = self._interact_with_remove_clothes_menu()
        self.database.delete_from_table_by_id(table='clothes', id_=clothes_id_to_remove)
        print(colored(f'Successfully removed clothes with id "{clothes_id_to_remove}"', 'blue'))

    def restock_clothes(self) -> None:
        clothes_id = self._interact_with_restock_clothes_menu()
        restock_amount = self._interact_with_specify_restock_amount_menu()

        print(colored(f'Successfully updated in_stock of item #{clothes_id} to {restock_amount}', 'blue'))
        self.database.update_value_by_id(table='clothes', column='in_stock', new_value=restock_amount, id_=clothes_id)

    def interact_with_manage_clothes_type_menu(self) -> Tuple[bool, int]:
        available_clothes_types = self.database.select_all_columns_from_table(table='clothes_type')
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.manage_clothes_type_menu,
            select_result=available_clothes_types)

        return is_empty, user_input['choice']

    def add_clothes_type(self) -> None:
        clothes_type = ClothesType(self._interact_with_add_clothes_type_menu())
        self.database.insert_clothes_type(clothes_type)
        print(colored(f'Successfully added "{clothes_type.type}" clothes type.', 'blue'))

    def remove_clothes_type(self) -> None:
        id_to_remove = self._interact_with_remove_clothes_type_menu()
        self.database.delete_from_table_by_id(table='clothes_type', id_=id_to_remove)
        print(colored(f'Successfully removed clothes type with id "{id_to_remove}"', 'blue'))

    def change_clothes_info(self) -> None:
        fields_mapping = {
            1: 'clothes_type_id',
            2: 'title',
            3: 'description',
            4: 'size',
            5: 'material',
            6: 'color',
            7: 'price',
            8: 'discount',
            9: 'in_stock'
        }

        clothes_id = self._interact_with_change_clothes_info_menu()
        key = self._interact_with_specify_clothes_field_to_change_menu()
        field = fields_mapping[key]
        new_field_value = self._interact_with_specify_new_clothes_info_menu(key=key, field=field)

        self.database.update_value_by_id(table='clothes', column=field, new_value=new_field_value, id_=clothes_id)
        print(colored(f'Successfully changed value of {field} to {new_field_value} for clothes with id {clothes_id}',
                      'blue'))

    def change_clothes_type_info(self) -> None:
        clothes_type_id = self._interact_with_change_clothes_type_info_menu()
        new_clothes_type = self._interact_with_specify_new_clothes_type_menu()

        self.database.update_value_by_id(table='clothes_type', column='type', new_value=new_clothes_type,
                                         id_=clothes_type_id)
        print(colored(f'Successfully changed value to {new_clothes_type} for clothes type with id {clothes_type_id}',
                      'blue'))

    def interact_with_manage_status_menu(self) -> Tuple[bool, int]:
        existing_statuses = self.database.select_all_columns_from_table(table='status')
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.manage_status_menu,
            select_result=existing_statuses)

        return is_empty, user_input['choice']

    def add_status(self) -> None:
        status = Status(self._interact_with_add_status_menu())
        self.database.insert_status(status)
        print(colored(f'Successfully added status "{status.status}".', 'blue'))

    def remove_status(self) -> None:
        id_to_remove = self._interact_with_remove_status_menu()
        self.database.delete_from_table_by_id(table='status', id_=id_to_remove)
        print(colored(f'Successfully removed status with id "{id_to_remove}"', 'blue'))

    def change_status_info(self) -> None:
        status_id = self._interact_with_change_status_info_menu()
        new_status = self._interact_with_specify_new_status_menu()

        self.database.update_value_by_id(table='status', column='status', new_value=new_status, id_=status_id)
        print(colored(f'Successfully changed value to {new_status} for status with id {status_id}',
                      'blue'))

    def _interact_with_change_clothes_type_info_menu(self) -> int:
        existing_clothes_type_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes_type'))
        return self.show_and_interact_with_menu(
            menu=self.menu.change_clothes_type_info_menu,
            existing_clothes_type_ids=existing_clothes_type_ids)['choice']

    def _interact_with_change_clothes_info_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes'))
        return self.show_and_interact_with_menu(
            menu=self.menu.change_clothes_info_menu,
            existing_clothes_ids=existing_ids)['choice']

    def _interact_with_specify_new_clothes_type_menu(self) -> str:
        existing_clothes_types = extract_all_values_from_list_of_dicts(
            list_of_dicts=self.database.select_column_from_table(column='type', table='clothes_type'),
            flatten=True
        )
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_new_clothes_type_menu,
            existing_clothes_types=existing_clothes_types)['clothes_type']

    def _interact_with_specify_clothes_field_to_change_menu(self) -> int:
        return self.show_and_interact_with_menu(menu=self.menu.specify_clothes_field_to_change_menu)['choice']

    def _interact_with_specify_new_clothes_info_menu(self, key: int, field: str) -> Union[int, float, str]:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes_type'))
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_new_clothes_info_menu,
            existing_clothes_type_ids=existing_ids,
            settings_key=key)[field]

    def _interact_with_change_order_status_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='order'))
        return self.show_and_interact_with_menu(
            menu=self.menu.change_order_status_menu,
            existing_order_ids=existing_ids)['choice']

    def _interact_with_specify_new_order_status_menu(self) -> int:
        existing_status_ids = extract_ids(self.database.select_all_columns_from_table(table='status'))
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_new_order_status_menu,
            existing_status_ids=existing_status_ids)['choice']

    def _interact_with_add_clothes_menu(self) -> Clothes:
        available_clothes_type_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes_type'))
        clothes_dict = self.menu.add_clothes_menu(available_clothes_type_ids).show(what='choice').interact()

        choice, no_choice = clothes_dict['choice'], clothes_dict['no_choice']
        return Clothes(**choice, **no_choice)

    def _interact_with_remove_clothes_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes'))
        return self.show_and_interact_with_menu(
            menu=self.menu.remove_clothes_menu,
            existing_clothes_ids=existing_ids)['choice']

    def _interact_with_restock_clothes_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes'))
        return self.show_and_interact_with_menu(
            menu=self.menu.restock_clothes_menu,
            existing_clothes_ids=existing_ids)['choice']

    def _interact_with_specify_restock_amount_menu(self) -> int:
        return self.show_and_interact_with_menu(menu=self.menu.specify_restock_amount_menu)['restock_amount']

    def _interact_with_add_clothes_type_menu(self) -> str:
        existing_clothes_types = extract_all_values_from_list_of_dicts(
            list_of_dicts=self.database.select_column_from_table(column='type', table='clothes_type'),
            flatten=True
        )
        return self.show_and_interact_with_menu(
            menu=self.menu.add_clothes_type_menu,
            existing_clothes_types=existing_clothes_types)['clothes_type']

    def _interact_with_remove_clothes_type_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='clothes_type'))
        return self.show_and_interact_with_menu(
            menu=self.menu.remove_clothes_type_menu,
            existing_clothes_type_ids=existing_ids)['choice']

    def _interact_with_add_status_menu(self) -> str:
        existing_statuses = extract_all_values_from_list_of_dicts(
            list_of_dicts=self.database.select_column_from_table(column='status', table='status'),
            flatten=True
        )
        return self.show_and_interact_with_menu(
            menu=self.menu.add_status_menu,
            existing_statuses=existing_statuses)['status']

    def _interact_with_remove_status_menu(self) -> int:
        existing_ids = extract_ids(self.database.select_all_columns_from_table(table='status'))
        return self.show_and_interact_with_menu(
            menu=self.menu.remove_status_menu,
            existing_status_ids=existing_ids)['choice']

    def _interact_with_change_status_info_menu(self) -> int:
        existing_status_ids = extract_ids(self.database.select_all_columns_from_table(table='status'))
        return self.show_and_interact_with_menu(
            menu=self.menu.change_status_info_menu,
            existing_status_ids=existing_status_ids)['choice']

    def _interact_with_specify_new_status_menu(self) -> str:
        existing_statuses = extract_all_values_from_list_of_dicts(
            list_of_dicts=self.database.select_column_from_table(column='status', table='status'),
            flatten=True
        )
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_new_status_menu,
            existing_statuses=existing_statuses)['status']
