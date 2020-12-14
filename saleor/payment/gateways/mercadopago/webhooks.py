import json
import logging
import requests

from json.decoder import JSONDecodeError
from ....core.transactions import transaction_with_commit_on_errors
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.core.handlers.wsgi import WSGIRequest


logger = logging.getLogger(__name__)


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


def get_request_header(private_key: str, **_):
    header = {"Authorization": f"Bearer {private_key}"}
    return header


def get_request_url(id):
    return f"https://api.mercadopago.com/v1/payments/{id}"


def get_payment(id, gateway_config):
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
    response = get_payment(id, gateway_config)
    if response["status"] in POSSIBLE_STATUS:
        # ACTUALIZAR ESTADO DEL PAGO. COMO? NO SE. TIENE QUE VER CON EL TRANSACTION KIND Y _GENERATE RESPONSE
    else:
        logger.exception(response["message"])
        return

    