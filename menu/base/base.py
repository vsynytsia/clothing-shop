from abc import ABC, abstractmethod
from typing import Union, Any, Optional

from termcolor import colored

from user_input_validation import validate_input


class BaseMenu(ABC):
    def __init__(self, menu_message: str, settings: Optional[dict]):
        self.menu_message = menu_message
        self.settings = settings

    def show(self):
        print(self.menu_message)
        return self

    @abstractmethod
    def interact(self):
        raise NotImplementedError


class BaseMenuWithChoice(BaseMenu):
    def __init__(self, menu_message: str, settings: Optional[dict]) -> None:
        super().__init__(menu_message, settings)

    def interact(self) -> Optional[dict]:
        if self.settings is None:
            return
        for input_value, input_settings in self.settings.items():
            while True:
                input_message = f'Enter your {input_value}: '

                try:
                    input_ = validate_input(
                        user_input=input(input_message),
                        expected_type=input_settings['expected_type'],
                        expected_values=input_settings['expected_values'],
                        additional_validators=input_settings.get('additional_validators', None),
                        error_messages=input_settings.get('error_messages', None)
                    )
                    return {input_value: input_}

                except ValueError as error:
                    print(colored(str(error), 'red'))


class BaseMenuWithNoChoice(BaseMenu):
    def __init__(self, menu_message: str, settings: dict) -> None:
        super().__init__(menu_message, settings)

    def interact(self) -> Optional[dict]:
        if self.settings is None:
            return

        inputs = {}
        for input_value, input_settings in self.settings.items():
            input_message = f'Enter your {input_value}: '

            if input_settings.get('confirm', False):
                confirm_message = f'Repeat your {input_value}: '
            else:
                confirm_message = None

            if input_settings.get('validate', True):
                input_ = self._input_single_until_correct(
                    input_message=input_message,
                    expected_type=input_settings['expected_type'],
                    confirm=input_settings.get('confirm', False),
                    confirm_message=confirm_message,
                    additional_validators=input_settings.get('additional_validators', None),
                    error_messages=input_settings.get('error_messages', None)
                )
            else:
                input_ = input(input_message)
            inputs[input_value] = input_

        return inputs

    def _input_single_until_correct(
            self,
            input_message: str,
            expected_type: str,
            confirm: bool,
            **kwargs
    ) -> Union[int, str]:

        while True:
            try:
                input_ = validate_input(
                    user_input=input(input_message),
                    expected_type=expected_type,
                    **kwargs
                )
            except ValueError as error:
                print(colored(str(error), 'red'))
                continue

            if not confirm:
                break
            try:
                self._confirm_input(input_message=kwargs['confirm_message'], first_input=input_)
                break
            except ValueError as error:
                print(colored(str(error), 'red'))

        return input_

    @staticmethod
    def _confirm_input(input_message: str, first_input: Any) -> None:
        second_input = input(input_message)

        if first_input != second_input:
            raise ValueError(f'{input_message.split(" ")[-2][:-1].capitalize()}s dont match. Try again!')


class BaseMenuMixed(BaseMenu):
    def __init__(
            self,
            choice_menu_settings: dict,
            choice_menu_message: str,
            no_choice_menu_settings: dict,
            no_choice_menu_message: str
    ) -> None:
        self.choice_menu = BaseMenuWithChoice(choice_menu_message, choice_menu_settings)
        self.no_choice_menu = BaseMenuWithNoChoice(no_choice_menu_message, no_choice_menu_settings)

    def show(self, what='both') -> 'BaseMenuMixed':
        if what == 'choice':
            self.choice_menu.show()
        elif what == 'no_choice':
            self.no_choice_menu.show()

        return self

    def interact(self) -> dict:
        choice_inputs = self.choice_menu.interact()
        no_choice_inputs = self.no_choice_menu.interact()

        inputs = {
            'choice': choice_inputs,
            'no_choice': no_choice_inputs
        }

        return inputs
