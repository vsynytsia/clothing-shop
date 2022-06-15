from termcolor import colored

from database import Database
from interface.role_specific import *
from models import Role


def main():
    database = Database(
        host='localhost',
        user='root',
        password='qwerty',
        database='clothing_shop_db'
    )
    interfaces_mapping = {
        'customer': CustomerInterface,
        'worker': WorkerInterface,
        'admin': AdminInterface
    }

    guest_interface = GuestInterface(database=database)
    guest_interface.run()
    current_user = guest_interface.current_user

    while True:
        role = Role.map_id_to_role(current_user.role_id)
        interface = interfaces_mapping[role](database=database, current_user=current_user)
        current_user = interface.run()

        if current_user is None:
            break
    print(colored('See you soon!', 'magenta'))


if __name__ == '__main__':
    main()
