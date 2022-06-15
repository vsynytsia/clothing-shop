from abc import ABC, abstractmethod
from typing import Union, Tuple

import mysql.connector
from termcolor import colored

from database import Database
from menu.role_specific import GuestMenus, CustomerMenus, WorkerMenus, AdminMenus
from models import User
from utils.hash import hash_password
from utils.other import rename_dict_key


class CommonInterface(ABC):
    def __init__(
            self,
            database: Database,
            menu: Union[GuestMenus, CustomerMenus, WorkerMenus, AdminMenus]
    ) -> None:

        self.database = database
        self.menu = menu

        self.current_user = None
        self.is_signed_in = False

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @classmethod
    def show_and_interact_with_menu(cls, menu, *args, **kwargs) -> Union[Tuple[bool, dict], dict]:
        menu_ = menu.__call__(*args, **kwargs)
        if isinstance(menu_, tuple):
            return menu_[0], menu_[1].show().interact()
        else:
            return menu_.show().interact()

    def interact_with_start_menu(self) -> int:
        return self.show_and_interact_with_menu(menu=self.menu.start_menu)['choice']

    def sign_in(self) -> None:
        menu = self.menu.sign_in_menu().show()

        while not self.is_signed_in:
            inputs = menu.interact()
            inputs['password'] = hash_password(inputs['password'])
            inputs = rename_dict_key(inputs, old_key='password', new_key='password_hash')

            response = self.database.select_user_by_email_and_phash(*inputs.values())
            if len(response) == 0:
                print(colored('Wrong email and/or password. Try again!', 'red'))
            else:
                user = User(id=response[0]['id'], *list(response[0].values())[1:])
                self._on_successful_sign_in(user=user)

    def sign_up(self) -> None:
        menu = self.menu.sign_up_menu().show()

        while not self.is_signed_in:
            inputs = menu.interact()
            inputs['password'] = hash_password(inputs['password'])
            inputs = rename_dict_key(inputs, old_key='password', new_key='password_hash')
            user = User(*inputs.values())

            try:
                inserted_user_id = self.database.insert_user(user)
                self._on_successful_sign_in(user=User(*inputs.values(), id=inserted_user_id))
            except mysql.connector.errors.IntegrityError:
                print(colored('User with given email/phone number already exists. Try again!', 'red'))

    def sign_off(self) -> None:
        self.current_user = None
        self.is_signed_in = False

    def switch_users(self) -> User:
        self.sign_off()
        self.sign_in()
        return self.current_user

    def interact_with_available_clothes_menu(self) -> Tuple[bool, int]:
        response = self.database.select_all_columns_from_table('clothes')
        is_empty, user_input = self.show_and_interact_with_menu(menu=self.menu.clothes_menu, select_result=response)
        return is_empty, user_input['choice']

    def _on_successful_sign_in(self, user: User) -> None:
        self.is_signed_in = True
        self.current_user = user
        print(colored(f'Successfully signed into your account', 'green'))
