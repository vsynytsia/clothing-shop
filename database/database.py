from typing import List, Tuple, Optional

import mysql.connector

from models import User, Order, ItemOrdered, Clothes, ClothesType, Role, Status
from utils import calculate_single_item_total


class Database:
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor(dictionary=True)

    def _execute_and_commit(self, query: str, params: Optional[Tuple], return_id: bool) -> Optional[int]:
        self.cursor.execute(query, params)
        self.db.commit()
        return self.cursor.lastrowid if return_id else None

    def _execute_and_fetchall(self, query: str, params: Optional[Tuple]) -> List[dict]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def select_user_by_email_and_phash(self, email: str, password_hash: str) -> List[dict]:
        query = 'select * from user as u where (u.email = %s and u.password_hash = %s)'
        params = (email, password_hash)
        return self._execute_and_fetchall(query, params=params)

    def select_all_columns_from_table(self, table: str) -> List[dict]:
        query = 'select * from `%s`' % table
        return self._execute_and_fetchall(query, params=None)

    def select_column_from_table(self, column: str, table: str) -> List[dict]:
        query = 'select %s from %s' % (column, table)
        return self._execute_and_fetchall(query, params=None)

    def select_clothes_by_id(self, clothes_id: int) -> List[dict]:
        query = 'select * from clothes as c where c.id = %s'
        params = (clothes_id,)
        return self._execute_and_fetchall(query, params=params)

    def select_user_orders(self, user_id: int) -> List[dict]:
        query = 'select o.id, o.date_time, s.status from `order` as o, status as s' \
                ' where o.user_id = %s and o.status_id = s.id '
        params = (user_id,)
        return self._execute_and_fetchall(query, params=params)

    def select_single_user_order(self, order_id: int) -> List[dict]:
        query = 'select order_id, title, size, material, color, quantity, price, c.discount, total, date_time, s.status' \
                ' from status as s, `order` as o' \
                ' join item_ordered i on o.id = i.order_id' \
                ' join clothes c on c.id = i.clothes_id' \
                ' where order_id = %s and o.status_id = s.id'
        params = (order_id,)
        return self._execute_and_fetchall(query, params=params)

    def insert_clothes(self, clothes: Clothes, return_id: bool = False) -> Optional[int]:
        query = 'insert into clothes (clothes_type_id, title, description, size, material, color, price, discount, in_stock)' \
                ' values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        params = (clothes.clothes_type_id, clothes.title, clothes.description, clothes.size,
                  clothes.material, clothes.color, clothes.price, clothes.discount, clothes.in_stock)
        return self._execute_and_commit(query, params=params, return_id=return_id)

    def insert_user(self, user: User, return_id: bool = False) -> Optional[int]:
        query = 'insert into user (first_name, last_name, phone_number, email, password_hash)' \
                ' values (%s, %s, %s, %s, %s)'
        params = (user.first_name, user.last_name, user.phone_number, user.email, user.password_hash)
        return self._execute_and_commit(query, params=params, return_id=return_id)

    def insert_order(self, order: Order, return_id: bool = False) -> Optional[int]:
        query = 'insert into `order` (user_id, date_time) values (%s, %s)'
        params = (order.user_id, order.date_time)
        return self._execute_and_commit(query, params=params, return_id=return_id)

    def insert_item_ordered(self, item_ordered: ItemOrdered, return_id: bool = False) -> Optional[int]:
        query = 'insert into item_ordered (order_id, clothes_id, quantity, discount, total)' \
                'values (%s, %s, %s, %s, %s)'

        clothes = self.select_clothes_by_id(item_ordered.clothes_id)[0]
        price, discount = clothes['price'], clothes['discount']
        item_ordered.total = calculate_single_item_total(item_ordered.quantity, float(price), float(discount))

        params = (item_ordered.order_id, item_ordered.clothes_id, item_ordered.quantity,
                  item_ordered.discount, item_ordered.total)

        id_ = self._execute_and_commit(query, params=params, return_id=return_id)
        self._on_inserted_item_ordered(item_ordered)
        return id_

    def insert_clothes_type(self, clothes_type: ClothesType) -> None:
        query = 'insert into clothes_type (type) values (%s)'
        params = (clothes_type.type,)
        return self._execute_and_commit(query, params=params, return_id=False)

    def insert_role(self, role: Role) -> None:
        query = 'insert into role (role) values (%s)'
        params = (role.role,)
        return self._execute_and_commit(query, params=params, return_id=False)

    def insert_status(self, status: Status) -> None:
        query = 'insert into status (status) values (%s)'
        params = (status.status,)
        return self._execute_and_commit(query, params=params, return_id=False)

    def delete_from_table_by_id(self, table: str, id_: int) -> None:
        query = 'delete from %s where %s.id = %s' % (table, table, id_)
        return self._execute_and_commit(query, params=None, return_id=False)

    def update_value_by_id(self, table: str, column: str, new_value, id_: int) -> None:
        query = 'update {} set {} = %s where id = %s'.format(table, column)
        params = (new_value, id_)
        return self._execute_and_commit(query, params=params, return_id=False)

    def _on_inserted_item_ordered(self, inserted_item: ItemOrdered) -> None:
        query = 'update clothes set in_stock = %s where clothes.id = %s'
        clothes = self.select_clothes_by_id(inserted_item.clothes_id)[0]
        params = (clothes['in_stock'] - inserted_item.quantity, inserted_item.clothes_id)
        return self._execute_and_commit(query, params=params, return_id=False)
