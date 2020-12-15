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
from ....payment.models import Payment, Transaction
from ... import TransactionKind
from ...interface import GatewayConfig, GatewayResponse
from ...utils import create_payment_information, create_transaction, gateway_postprocess
from ....order.events import external_notification_event
from ....order.actions import (
    cancel_order,
    order_authorized,
    order_captured,
    order_refunded,
)


logger = logging.getLogger(__name__)


def create_payment_notification_for_order(
    payment: Payment, success_msg: str, failed_msg: Optional[str], is_success: bool
):
    if not payment.order:
        # Order is not assigned
        return
    msg = success_msg if is_success else failed_msg

    external_notification_event(
        order=payment.order,
        user=None,
        message=msg,
        parameters={"service": payment.gateway, "id": payment.token},
    )


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


def get_transaction(
    payment: "Payment", transaction_id: Optional[str], kind: str,
) -> Optional[Transaction]:
    transaction = payment.transactions.filter(kind=kind, token=transaction_id).last()
    return transaction


def create_new_transaction(mp_response, payment, kind):
    transaction_id = mp_response.get("id")
    currency = mp_response.get("currency_id")
    amount = mp_response.get("transaction_amount")
    is_success = True

    gateway_response = GatewayResponse(
        kind=kind,
        action_required=False,
        transaction_id=transaction_id,
        is_success=is_success,
        amount=amount,
        currency=currency,
        error="",
        raw_response=mp_response,
        searchable_key=transaction_id
    )
    return create_transaction(
        payment,
        kind=kind,
        payment_information=None,
        action_required=False,
        gateway_response=gateway_response,
    )


def get_transaction_kind(status):
    kind = POSSIBLE_STATUS.get(status)
    return kind


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


POSSIBLE_STATUS = {
    "pending": TransactionKind.PENDING,
    "approved": TransactionKind.CAPTURE,
    "authorized": TransactionKind.AUTH,
    "in_process": TransactionKind.PENDING,
    "in_mediation": TransactionKind.ACTION_TO_CONFIRM,
    "rejected": TransactionKind.CAPTURE_FAILED,
    "cancelled": TransactionKind.CANCEL,
    "refunded": TransactionKind.REFUND,
    "charged_back": TransactionKind.ACTION_TO_CONFIRM,
}


def handle_status_change(id, gateway_config):
    mp_response = get_mp_payment(id, gateway_config)
    if mp_response["status"] in POSSIBLE_STATUS:
        payment = get_payment(payment_id=mp_response["external_reference"])
        kind = get_transaction_kind(mp_response["status"])
        new_transaction = create_new_transaction(mp_response, payment, kind)
        if new_transaction.is_success:
            gateway_postprocess(new_transaction, payment)
        success_msg = f"MercadoPago: El request del pago {transaction_id} fue exitoso."
        create_payment_notification_for_order(payment, success_msg, None, True)
    else:
        logger.exception(mp_response["message"])
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
    if json_data["action"] != "payment.updated":
        return HttpResponse(status=200)
        
    handle_status_change(json_data["data"]["id"], gateway_config)
    return HttpResponse(status=200)   