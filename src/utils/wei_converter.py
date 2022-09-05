from decimal import Decimal, localcontext

from eth_utils.currency import MIN_WEI, MAX_WEI
from eth_utils.types import is_integer, is_string


def from_basis_points(number: int, decimals: int):
    """
    Конвертирует из базовых поинтов к человеческому числу(ETH, MATIC)
    в зависимости от decimals у токена
    """
    if number == 0:
        return 0

    if number < MIN_WEI or number > MAX_WEI:
        raise ValueError("value must be between 1 and 2**256 - 1")

    with localcontext() as ctx:
        ctx.prec = 999
        d_number = Decimal(value=number, context=ctx)
        unit_value = Decimal('10') ** decimals
        result_value = d_number / unit_value

    return result_value


def to_basis_points(number, decimals: int) -> int:
    if is_integer(number) or is_string(number):
        number = Decimal(value=number)
    elif isinstance(number, float):
        number = Decimal(value=str(number))
    elif isinstance(number, Decimal):
        number = number
    else:
        raise TypeError("Unsupported type.  Must be one of integer, float, or string")

    if number == 0:
        return 0

    with localcontext() as ctx:
        ctx.prec = 999
        d_number = Decimal(value=number, context=ctx)
        unit_value = Decimal('10') ** decimals
        result_value = d_number * unit_value

    if result_value < MIN_WEI or result_value > MAX_WEI:
        raise ValueError("value must be between 1 and 2**256 - 1")

    return int(result_value)
