import logging
from typing import Dict


from ... import TransactionKind
from ...interface import GatewayConfig, GatewayResponse, PaymentData
from .utils import get_error_response


SUPPORTED_CURRENCIES = ("ARS",)
UNSUPPORTED_CURRENCY = "La moneda %(currency)s no es valida."
# Get the logger for this file, it will allow us to log
# error responses from mercadoPago
logger = logging.getLogger(__name__)


def _generate_response(
    payment_information: PaymentData, kind: str, data: Dict, transfer_data: Dict,
) -> GatewayResponse:
    """Generate Saleor transaction information from the payload or from passed data."""

    name = transfer_data.get("public_key")
    cbu = transfer_data.get("private_key")
    externalResource = {
        "name": name,
        "cbu": cbu,
    }
    return GatewayResponse(
        transaction_id=data.get("id", payment_information.token),
        action_required=False,
        action_required_data={"externalResource": externalResource},
        kind=kind,
        amount=data.get("amount", payment_information.amount),
        currency=data.get("currency", payment_information.currency),
        error=data.get("error"),
        is_success=data.get("is_success", True),
        raw_response=data,
    )


def check_payment_supported(payment_information: PaymentData):
    """Check that a given payment is supported."""
    if payment_information.currency not in SUPPORTED_CURRENCIES:
        return UNSUPPORTED_CURRENCY % {"currency": payment_information.currency}


def capture(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    error = check_payment_supported(payment_information=payment_information)
    if error:
        response = get_error_response(
            payment_information.amount, error=error, id=payment_information.token
        )
    return _generate_response(
        payment_information=payment_information,
        kind=TransactionKind.PENDING,
        data=response,
        transfer_data=config.connection_params,
    )


def process_payment(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    return capture(payment_information=payment_information, transfer_data=config.connection_params)
