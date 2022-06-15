from typing import Tuple, Optional

from termcolor import colored

from database import Database
from interface import CommonInterface
from interface.role_specific import WorkerInterface, CustomerInterface
from menu.role_specific import AdminMenus
from models import User, Role
from utils.parse import extract_ids, extract_all_values_from_list_of_dicts


class AdminInterface(CommonInterface):
    def __init__(self, database: Database, current_user: User) -> None:
        super().__init__(database, menu=AdminMenus())
        self.current_user = current_user

    def run(self) -> Optional[User]:
        lower_level_interfaces = {
            'customer': CustomerInterface(database=self.database, current_user=self.current_user),
            'worker': WorkerInterface(database=self.database, current_user=self.current_user)
        }

        while True:
            next_action_top = self.interact_with_main_menu()

            if next_action_top == 1:
                self.run_manage_users_menu()
            elif next_action_top == 2:
                self.run_manage_roles_menu()
            elif next_action_top == 3:
                lower_level_interfaces['worker'].run_manage_orders_menu()
            elif next_action_top == 4:
                lower_level_interfaces['worker'].run_manage_clothes_menu()
            elif next_action_top == 5:
                lower_level_interfaces['worker'].run_manage_clothes_type_menu()
            elif next_action_top == 6:
                lower_level_interfaces['customer'].run_view_available_clothes_menu()
            elif next_action_top == 7:
                lower_level_interfaces['customer'].run_view_my_basket_menu()
            elif next_action_top == 8:
                lower_level_interfaces['customer'].run_view_my_orders_menu()
            elif next_action_top == 9:
                return self.switch_users()
            elif next_action_top == 10:
                break

    def run_manage_users_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_manage_users_menu()

            if is_empty and next_action == 1:
                break
            else:
                if next_action == 1:
                    self.change_user_info()
                elif next_action == 2:
                    self.delete_user()
                elif next_action == 3:
                    break

    def run_manage_roles_menu(self) -> None:
        while True:
            is_empty, next_action = self.interact_with_manage_roles_menu()

            if is_empty:
                if next_action == 1:
                    break
                elif next_action == 2:
                    self.add_role()
            else:
                if next_action == 1:
                    self.add_role()
                elif next_action == 2:
                    self.delete_role()
                elif next_action == 3:
                    self.change_role_info()
                elif next_action == 4:
                    break

    def interact_with_main_menu(self) -> int:
        return self.show_and_interact_with_menu(
            menu=self.menu.main_menu,
            user_name=self.current_user.first_name)['choice']

    def interact_with_manage_users_menu(self) -> Tuple[bool, int]:
        available_users = self.database.select_all_columns_from_table(table='user')
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.manage_users_menu,
            select_result=available_users)

        return is_empty, user_input['choice']

    def change_user_info(self) -> None:
        fields_mapping = {
            1: 'first_name',
            2: 'last_name',
            3: 'phone_number',
            4: 'email',
            5: 'role_id'
        }

        user_id = self._interact_with_change_user_info_menu()
        key = self._interact_with_specify_user_field_to_change_menu()
        field = fields_mapping[key]
        new_field_value = self._interact_with_specify_new_user_info_menu(key=key, field=field)

        self.database.update_value_by_id(table='user', column=field,
                                         new_value=new_field_value, id_=user_id)
        print(colored(f'Successfully changed value of {field} to {new_field_value} for user with id {user_id}',
                      'blue'))

    def delete_user(self) -> None:
        user_id = self._interact_with_delete_user_menu()
        self.database.delete_from_table_by_id(table='user', id_=user_id)

        print(colored(f'Successfully deleted user with id {user_id}', 'blue'))

    def interact_with_manage_roles_menu(self) -> Tuple[bool, int]:
        select_result = self.database.select_all_columns_from_table(table='role')
        is_empty, user_input = self.show_and_interact_with_menu(
            menu=self.menu.manage_roles_menu,
            select_result=select_result)

        return is_empty, user_input['choice']

    def add_role(self) -> None:
        role = Role(self._interact_with_add_role_menu())
        self.database.insert_role(role)
        print(colored(f'Successfully added {role} role.', 'blue'))

    def delete_role(self) -> None:
        id_to_remove = self._interact_with_delete_role_menu()
        self.database.delete_from_table_by_id(table='role', id_=id_to_remove)
        print(colored(f'Successfully removed role with id {id_to_remove}', 'blue'))

    def change_role_info(self) -> None:
        role_id = self._interact_with_change_role_info_menu()
        new_role = self._interact_with_specify_new_role_info_menu()

        self.database.update_value_by_id(table='role', column='role', new_value=new_role, id_=role_id)
        print(colored(f'Successfully changed role with id {role_id} to {new_role}'))

    def _interact_with_add_role_menu(self) -> str:
        existing_roles = extract_all_values_from_list_of_dicts(
            list_of_dicts=self.database.select_column_from_table(table='role', column='role'),
            flatten=True
        )
        return self.show_and_interact_with_menu(
            menu=self.menu.add_role_menu,
            existing_roles=existing_roles)['role']

    def _interact_with_delete_role_menu(self) -> int:
        existing_role_ids = extract_ids(self.database.select_all_columns_from_table(table='role'))
        return self.show_and_interact_with_menu(
            menu=self.menu.delete_role_menu,
            existing_role_ids=existing_role_ids)['choice']

    def _interact_with_change_role_info_menu(self) -> int:
        existing_role_ids = extract_ids(self.database.select_all_columns_from_table(table='role'))
        return self.show_and_interact_with_menu(
            menu=self.menu.change_role_info_menu,
            existing_role_ids=existing_role_ids)['choice']

    def _interact_with_specify_new_role_info_menu(self) -> str:
        existing_roles = extract_all_values_from_list_of_dicts(
            list_of_dicts=self.database.select_column_from_table(table='role', column='role'),
            flatten=True
        )
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_new_role_info_menu,
            existing_roles=existing_roles)['role']

    def _interact_with_change_user_info_menu(self) -> int:
        existing_user_ids = extract_ids(self.database.select_all_columns_from_table(table='user'))
        return self.show_and_interact_with_menu(
            menu=self.menu.change_user_info_menu,
            existing_user_ids=existing_user_ids)['choice']

    def _interact_with_specify_user_field_to_change_menu(self) -> int:
        return self.show_and_interact_with_menu(menu=self.menu.specify_user_field_to_change_menu)['choice']

    def _interact_with_specify_new_user_info_menu(self, key: int, field: str) -> str:
        existing_role_ids = extract_ids(self.database.select_all_columns_from_table(table='role'))
        return self.show_and_interact_with_menu(
            menu=self.menu.specify_new_user_info_menu,
            settings_key=key,
            existing_role_ids=existing_role_ids)[field]

    def _interact_with_delete_user_menu(self) -> int:
        available_ids = extract_ids(self.database.select_all_columns_from_table(table='user'))
        return self.show_and_interact_with_menu(
            menu=self.menu.delete_user_menu,
            existing_user_ids=available_ids)['choice']
