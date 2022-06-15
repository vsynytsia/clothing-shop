from database import Database
from interface import CommonInterface
from menu.role_specific import GuestMenus


class GuestInterface(CommonInterface):
    def __init__(self, database: Database) -> None:
        super().__init__(database=database, menu=GuestMenus())

    def run(self) -> None:
        while True:
            next_action = self.interact_with_start_menu()
            if next_action == 1:
                self.sign_in()
                break
            elif next_action == 2:
                self.sign_up()
                break
            else:
                _ = self.interact_with_available_clothes_menu()
