from operator import methodcaller
from typing import Union


def validate_input(
        user_input: Union[int, float, str],
        expected_type: str,
        **kwargs
) -> Union[int, float, str]:
    if expected_type == 'str':
        user_input = validate_string_input(user_input, **kwargs)
    elif expected_type == 'int':
        user_input = validate_int_input(user_input, **kwargs)
    elif expected_type == 'float':
        user_input = validate_float_input(user_input, **kwargs)

    return user_input


def require_additional_validation(func):
    def inner(*args, **kwargs):
        user_input = func(*args, **kwargs)

        if 'additional_validators' in kwargs and kwargs['additional_validators'] is not None:
            validation_results = list(map(methodcaller('__call__', user_input), kwargs['additional_validators']))
            if not all(validation_results):
                first_failed_validation_idx = [i for i, validation_result in enumerate(validation_results)
                                               if not validation_result][0]
                error_message = kwargs['error_messages'][first_failed_validation_idx]
                raise ValueError(error_message)

        return user_input

    return inner


def require_fill(func):
    def inner(*args, **kwargs):
        if len(args[0]) == 0:
            raise ValueError("You can't leave this field blank. Please, try again!")
        return func(*args, **kwargs)

    return inner


def cant_exceed_max_length(func):
    def inner(*args, **kwargs):
        if len(args[0]) > 255:
            raise ValueError('Maximum input length exceeded! Please, try again!')
        return func(*args, **kwargs)

    return inner


@require_additional_validation
@cant_exceed_max_length
@require_fill
def validate_string_input(user_input: str, **kwargs) -> str:
    user_input = user_input.strip()

    if kwargs.get('expected_values', None) is not None and user_input not in kwargs.get('expected_values', []):
        raise ValueError(f'Expected one of the options: {kwargs["expected_values"]},'
                         f' got "{user_input}" instead. Try again!')

    return user_input


@require_additional_validation
@cant_exceed_max_length
@require_fill
def validate_int_input(user_input: str, **kwargs) -> int:
    user_input = user_input.strip()

    if len(user_input) > 255:
        raise ValueError('Maximum string length exceeded')

    # re-raise exception so appropriate message is displayed
    try:
        user_input = int(user_input)

    except ValueError:
        if kwargs.get('expected_values', None) is None:
            error_message = f'Expected input is integer, got {user_input} instead.' \
                            f' Please, try again!'
        else:
            error_message = f'Expected one of the options: {kwargs["expected_values"]},' \
                            f' got "{user_input}" instead. Try again!'
        raise ValueError(error_message)

    if kwargs.get('expected_values', None) is not None and user_input not in kwargs.get('expected_values', []):
        raise ValueError(f'Expected one of the options: {kwargs["expected_values"]},'
                         f' got "{user_input}" instead. Try again!')

    return user_input


@require_additional_validation
@cant_exceed_max_length
@require_fill
def validate_float_input(user_input: str, **kwargs) -> float:
    user_input = user_input.strip()

    # re-raise exception so appropriate message is displayed
    try:
        user_input = float(user_input)
    except ValueError:
        raise ValueError(f'Expected input is a number, got {user_input} instead. Please, try again!')

    return user_input
