import json
import logging
import requests
import binascii

from json.decoder import JSONDecodeError
from ....core.transactions import transaction_with_commit_on_errors
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.core.handlers.wsgi import WSGIRequest
from graphql_relay import from_global_id
from typing import Optional
from ....payment.models import Payment


logger = logging.getLogger(__name__)


def get_payment(
    payment_id: Optional[str],
    transaction_id: Optional[str] = None,
    check_if_active=True,
) -> Optional[Payment]:
    transaction_id = transaction_id or ""
    if payment_id is None or not payment_id.strip():
        logger.warning("Missing payment ID. Reference %s", transaction_id)
        return None
    try:
        _type, db_payment_id = from_global_id(payment_id)
    except (UnicodeDecodeError, binascii.Error):
        logger.warning(
            "Unable to decode the payment ID %s. Reference %s",
            payment_id,
            transaction_id,
        )
        return None
    payments = (
        Payment.objects.prefetch_related("order", "checkout")
        .select_for_update(of=("self",))
        .filter(id=db_payment_id, gateway="mirumee.payments.mercadopago")
    )
    if check_if_active:
        payments = payments.filter(is_active=True)
    payment = payments.first()
    if not payment:
        logger.warning(
            "Payment for %s (%s) was not found. Reference %s",
            payment_id,
            db_payment_id,
            transaction_id,
        )
    return payment


def get_request_header(private_key: str, **_):
    header = {"Authorization": f"Bearer {private_key}"}
    return header


def get_request_url(id):
    return f"https://api.mercadopago.com/v1/payments/{id}"


def get_mp_payment(id, gateway_config):
    url = get_request_url(id)
    header = get_request_header(**gateway_config.connection_params)
    response = requests.get(url, headers=header).json()
    return response

POSSIBLE_STATUS = [
    "pending",
    "approved",
    "authorized",
    "in_process",
    "in_mediation",
    "rejected",
    "cancelled",
    "refunded",
    "charged_back",
]


def handle_status_change(id, gateway_config):
    response = get_mp_payment(id, gateway_config)
    if response["status"] in POSSIBLE_STATUS:
        payment = get_payment(payment_id=response["external_reference"])
        print(dir(payment))
    else:
        logger.exception(response["message"])
        return


@transaction_with_commit_on_errors()
def handle_webhook(request: WSGIRequest, gateway_config: "GatewayConfig"):
    try:
        json_data = json.loads(request.body)
    except JSONDecodeError:
        logger.warning("No se pudo parsear el body del request.")
        return HttpResponse(status=200)
    # JSON and HTTP POST notifications always contain a single NotificationRequestItem
    # object.
    # notification = json_data.get("notificationItems")[0].get(
    #     "NotificationRequestItem", {}
    # )
    handle_status_change(json_data["data"]["id"], gateway_config)
    return HttpResponse(status=200)   