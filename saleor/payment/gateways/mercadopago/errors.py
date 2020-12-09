ORDER_NOT_CHARGED = "Order was not charged."
INVALID_REQUEST = "El pago fue denegado."
SERVER_ERROR = "No se pudo procesar su orden."
UNSUPPORTED_CURRENCY = "La moneda %(currency)s no es valida."
MP_ERROR = "Ocurrió un error con la aplicación de Mercado Pago."

STATUS_DETAIL = {
    "accredited": "¡Listo! Se acreditó tu pago. En tu resumen verás el cargo de amount como statement_descriptor",
    "cc_rejected_bad_filled_card_number": "Revisa el número de tarjeta.",
    "cc_rejected_bad_filled_date": "Revisa la fecha de vencimiento.",
    "cc_rejected_bad_filled_other": "Revisa los datos.",
    "cc_rejected_bad_filled_security_code":	"Revisa el código de seguridad de la tarjeta.",
    "cc_rejected_blacklist": "No pudimos procesar tu pago.",
    "cc_rejected_call_for_authorize": "Debes autorizar ante payment_method_id el pago de amount.",
    "cc_rejected_card_disabled": "Llama a payment_method_id para activar tu tarjeta o usa otro medio de pago.",
    "cc_rejected_card_error": "No pudimos procesar tu pago.",
    "cc_rejected_duplicated_payment": "Ya hiciste un pago por ese valor. Si necesitas volver a pagar usa otra tarjeta u otro medio de pago.",
    "cc_rejected_high_risk": "Tu pago fue rechazado. Elige otro de los medios de pago, te recomendamos con medios en efectivo.",
    "cc_rejected_insufficient_amount": "Tu payment_method_id no tiene fondos suficientes.",
    "cc_rejected_invalid_installments": "payment_method_id no procesa pagos en installments cuotas.",
    "cc_rejected_max_attempts": "Llegaste al límite de intentos permitidos. Elige otra tarjeta u otro medio de pago.",
    "cc_rejected_other_reason":	"payment_method_id no procesó el pago.",
    "pending_contingency": "Estamos procesando tu pago. No te preocupes, menos de 2 días hábiles te avisaremos por e-mail si se acreditó.",
	"pending_review_manual": "Estamos procesando tu pago. No te preocupes, menos de 2 días hábiles te avisaremos por e-mail si se acreditó o si necesitamos más información.",
}