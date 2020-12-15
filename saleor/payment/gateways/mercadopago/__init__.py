import logging
import requests
import json
from typing import Dict


from ... import TransactionKind
from ...interface import GatewayConfig, GatewayResponse, PaymentData
from . import errors
from .utils import get_error_response

SUPPORTED_CURRENCIES = ("ARS",)
# Get the logger for this file, it will allow us to log
# error responses from razorpay.
logger = logging.getLogger(__name__)


def _generate_response(
    payment_information: PaymentData, kind: str, data: Dict
) -> GatewayResponse:
    """Generate Saleor transaction information from the payload or from passed data."""
    return GatewayResponse(
        transaction_id=data.get("id", payment_information.token),
        action_required=False,
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
        return errors.UNSUPPORTED_CURRENCY % {"currency": payment_information.currency}


def get_request_url():
    url = "https://api.mercadopago.com/v1/payments"
    return url


def get_request_header(private_key: str, **_):
    header = {"Authorization": f"Bearer {private_key}"}
    return header


def get_request_body(payment_information):
    full_name = payment_information.data["payer"]["name"].split()
    first_name = full_name[0]
    last_name = full_name[-1]
    body = {
        "token": payment_information.token,
        "installments": int(payment_information.data["installments"]),
        "transaction_amount": int(payment_information.amount),
        "description": payment_information.data["description"],
        "notification_url": "http://c5d9b4e2435c.ngrok.io/plugins/mirumee.payments.mercadopago/webhooks/",
        "payment_method_id": payment_information.data["brand"],
        "statement_descriptor":"Cholitas Deco",
        "external_reference": payment_information.graphql_payment_id,
        "payer": {
            "email": payment_information.data["email"],
            "identification": {
                "number": payment_information.data["payer"]["identification"]["number"],
                "type": payment_information.data["payer"]["identification"]["type"]
            }
        },
        "additional_info":{
            "payer":{
                "first_name":first_name.capitalize(),
                "last_name": last_name.capitalize(),
                "address": {
                    "zip_code": payment_information.billing.postal_code,
                    "street_name": payment_information.billing.street_address_1,
                },
                "phone": {
                    "number":payment_information.billing.phone
			    },
            },
            "shipments":{
                "receiver_address":{
                    "street_name":payment_information.shipping.street_address_1,
                    "zip_code":payment_information.shipping.postal_code,
                    "city_name": payment_information.shipping.city,
                    "state_name": payment_information.shipping.country_area
                }
		    }
        }
    }
    return json.dumps(body)


def capture(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    error = check_payment_supported(payment_information=payment_information)
    if not error:
        url = get_request_url()
        header = get_request_header(**config.connection_params)
        payload = get_request_body(payment_information)
        response = requests.post(url, data=payload, headers=header).json()
        if response["status"] != "approved":
            if response["status"] == "in_process":
                return _generate_response(
                    payment_information=payment_information,
                    kind=TransactionKind.PENDING,
                    data=response
                )
            try:
                error = errors.STATUS_DETAIL[response["status_detail"]]
                error = error.replace("payment_method_id", response["payment_method_id"]) \
                    .replace("statement_descriptor", response["statement_descriptor"]) \
                    .replace("amount", str(response["transaction_amount"])) 
                logger.exception(error)
            except KeyError:
                logger.exception(response["message"])
                err_code = response["cause"][0]["code"]
                error = errors.MP_API_ERROR[err_code] if err_code in errors.MP_API_ERROR else errors.MP_ERROR
            finally:
                response = get_error_response(
                    payment_information.amount, error=error, id=payment_information.token
                )
    else:
        response = get_error_response(
            payment_information.amount, error=error, id=payment_information.token
        )

    return _generate_response(
        payment_information=payment_information,
        kind=TransactionKind.CAPTURE,
        data=response
    )


def process_payment(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    return capture(payment_information=payment_information, config=config)
