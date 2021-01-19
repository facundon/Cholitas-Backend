from typing import TYPE_CHECKING

from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseNotFound

from ..utils import get_supported_currencies
from . import GatewayConfig, capture, process_payment


GATEWAY_NAME = "Transferencia Bancaria"

if TYPE_CHECKING:
    from . import GatewayResponse, PaymentData


def require_active_plugin(fn):
    def wrapped(self, *args, **kwargs):
        previous = kwargs.get("previous_value", None)
        if not self.active:
            return previous
        return fn(self, *args, **kwargs)

    return wrapped


class TransferenciaBancariaGatewayPlugin(BasePlugin):
    PLUGIN_NAME = GATEWAY_NAME
    PLUGIN_ID = "mirumee.payments.transferencia"
    DEFAULT_CONFIGURATION = [
        {"name": "Public API key", "value": None},
        {"name": "Secret API key", "value": None},
        {"name": "Store customers card", "value": False},
        {"name": "Automatic payment capture", "value": True},
        {"name": "Supported currencies", "value": ""},
    ]

    CONFIG_STRUCTURE = {
        "Public API key": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Nombre de la cuenta a depositar",
            "label": "Nombre",
        },
        "Secret API key": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "CBU de la cuenta",
            "label": "CBU",
        },
        "Store customers card": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "No aplica."
            "de Mercado Pago.",
            "label": "Guardar tarjeta del cliente",
        },
        "Automatic payment capture": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "No aplica",
            "label": "Captura de pagos automática",
        },
        "Supported currencies": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determina las monedas soportadas por el medio de pago."
            " Por favor ingresar las monedas separadas con coma.",
            "label": "Monedas soportadas",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=configuration["Automatic payment capture"],
            supported_currencies=configuration["Supported currencies"],
            connection_params={
                "public_key": configuration["Public API key"],
                "private_key": configuration["Secret API key"],
                "prefill": True,
                "store_name": None,
                "store_image": None,
            },
            store_customer=configuration["Store customers card"],
        )

    
    def _get_gateway_config(self):
        return self.config

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return capture(payment_information, self._get_gateway_config())

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return process_payment(payment_information, self._get_gateway_config())

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self._get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)

    @require_active_plugin
    def get_payment_config(self, previous_value):
        config = self._get_gateway_config()
        return [{"field": "api_key", "value": config.connection_params["public_key"]}]
