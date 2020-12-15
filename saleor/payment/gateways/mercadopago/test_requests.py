import requests
import json


def get_request_data(id):
    body = {
        "action": "payment.updated",
        "api_version": "v1",
        "data": {
            "id": id,
        },
        "date_created": "2020-12-14T20:58:52Z",
        "id": 6792428255,
        "live_mode": False,
        "type": "payment",
        "user_id": "670854424"
    }

    header = {
        "Host": "localhost:8000",
        "User-Agent": "MercadoPago WebHook v1.0 payment",
        "Content-Length": "185",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Forwarded-For": "34.236.9.110",
        "X-Forwarded-Proto": "http",
        "X-Rest-Pool-Name": "pool_postExternal",
        "X-Socket-Timeout": "25000"
    }
    return body, header

body, header = get_request_data(id=1231935157)

cases = {
    "PUT": requests.put('https://api.mercadopago.com/v1/payments/1231935157', json={"status":"approved"}, headers={"Authorization": "Bearer TEST-5363032924027795-111104-87699c155b89e8fe293aa74af75664d3-670854424"}).json(),
    "GET":requests.get('https://api.mercadopago.com/v1/payments/1231935157', headers={"Authorization": "Bearer TEST-5363032924027795-111104-87699c155b89e8fe293aa74af75664d3-670854424"}).json(),
    "WEBHOOK": requests.post('http://127.0.0.1:8000/plugins/mercadopago/webhooks/', data=json.dumps(body), headers=header),
}

response = cases.get("WEBHOOK")
print(response)