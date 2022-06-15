from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Tuple, Any, Union, Optional

from tabulate import tabulate

from utils.other import calculate_single_item_total
from utils.parse import separate_headers_and_items


class Status(Enum):
    REGISTERED = 'registered'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'
    DONE = 'done'


@dataclass
class User:
    first_name: str
    last_name: str
    phone_number: str
    email: str
    password_hash: str
    role_id: int = 1
    id: int = None


@dataclass
class Role:
    role: str
    id: int = None

    @staticmethod
    def map_id_to_role(role_id: int) -> str:
        roles_mapping = {
            1: 'customer',
            2: 'worker',
            3: 'admin'
        }
        return roles_mapping[role_id]


@dataclass
class Status:
    status: str
    id: int = None


@dataclass
class ClothesType:
    type: str
    id: int = None


@dataclass
class Clothes:
    clothes_type_id: int
    title: str
    description: str
    size: str
    material: str
    color: str
    price: float
    discount: float
    in_stock: int
    id: int = None

    @staticmethod
    def to_basket_clothes(clothes: dict, basket_quantity: int):
        return BasketClothes(
            clothes['id'], clothes['title'], clothes['size'], clothes['material'],
            clothes['color'], basket_quantity, clothes['price'], clothes['discount'],
            calculate_single_item_total(basket_quantity, float(clothes['price']), float(clothes['discount']))
        )


@dataclass
class Order:
    user_id: int
    date_time: datetime
    status_id: int = 1
    id: int = None


@dataclass
class ItemOrdered:
    order_id: int
    clothes_id: int
    quantity: int
    discount: float
    total: float


@dataclass
class BasketClothes:
    id: int
    title: str
    size: str
    material: str
    color: str
    quantity: int
    price: float
    discount: float
    total: float

    def to_item_ordered(self, order_id: int) -> ItemOrdered:
        return ItemOrdered(order_id, self.id, self.quantity, self.discount, self.total)


@dataclass
class Basket:
    contents: List[BasketClothes]

    def add_new(self, clothes: BasketClothes) -> 'Basket':
        self.contents.append(clothes)
        return self

    def add_existing(self, clothes: BasketClothes) -> 'Basket':
        idx = self.get_basket_clothes_id_by_clothes_id(clothes.id)
        self.contents[idx].quantity += clothes.quantity
        self.contents[idx].total += calculate_single_item_total(
            clothes.quantity,
            float(clothes.price),
            float(clothes.discount))

        return self

    def remove_single(self, clothes_id: int, amount: int) -> 'Basket':
        id_to_remove = self.get_basket_clothes_id_by_clothes_id(clothes_id)
        clothes_to_remove = self.get_contents_by_index(id_to_remove)

        new_quantity = clothes_to_remove.quantity - amount

        if new_quantity == 0:
            del self.contents[id_to_remove]
        else:
            self.contents[id_to_remove].quantity = new_quantity
            self.contents[id_to_remove].total = calculate_single_item_total(
                clothes_to_remove.quantity,
                float(clothes_to_remove.price),
                float(clothes_to_remove.discount))

        return self

    def clear(self) -> None:
        self.contents.clear()

    def get_basket_clothes_id_by_clothes_id(self, clothes_id: int) -> Optional[int]:
        all_ids = self.get_ids()

        try:
            idx = all_ids.index(clothes_id)
        except ValueError:
            idx = None
        return idx

    def get_in_basket_quantity_by_clothes_id(self, clothes_id: int) -> int:
        in_basket_quantity = 0

        idx = self.get_basket_clothes_id_by_clothes_id(clothes_id)
        if idx is not None:
            in_basket_quantity = self.get_contents_by_index(idx).quantity
        return in_basket_quantity

    def get_ids(self) -> List[int]:
        return [clothes.id for clothes in self.contents]

    def get_contents(self, raw: bool = True) -> Union[List[BasketClothes], Tuple[List[str], List[List[Any]]]]:
        if raw:
            return self.contents
        else:
            contents = [asdict(item) for item in self.contents]
            headers, items = separate_headers_and_items(contents)

            return headers, items

    def get_tabulated_contents(self) -> str:
        headers, items = self.get_contents(raw=False)
        tabulated_contents = tabulate(items, headers=headers, tablefmt="psql")

        return tabulated_contents

    def get_contents_by_index(self, idx: int) -> BasketClothes:
        return self.contents[idx]

    def calculate_basket_total(self) -> float:
        return sum([item.total for item in self.contents])

    def print(self) -> 'Basket':
        if len(self.contents) != 0:
            print(f'Your basket:\n {self.get_tabulated_contents()}\n'
                  f'Current basket total: {self.calculate_basket_total()}')

        return self
