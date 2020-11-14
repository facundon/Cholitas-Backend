from decimal import Decimal


def get_error_response(amount: Decimal, **additional_kwargs) -> dict:
    """Create a placeholder response for invalid or failed requests.

    It is used to generate a failed transaction object.
    """
    return {"is_success": False, "amount": amount, **additional_kwargs}

