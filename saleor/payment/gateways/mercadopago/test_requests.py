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


ID="1232601094"

body, header = get_request_data(ID)

#response = requests.put(f'https://api.mercadopago.com/v1/payments/{ID}', json={"status":"cancelled"}, headers={"Authorization": "Bearer TEST-5363032924027795-111104-87699c155b89e8fe293aa74af75664d3-670854424"}).json(),
#response = requests.get(f'https://api.mercadopago.com/v1/payments/{ID}', headers={"Authorization": "Bearer TEST-5363032924027795-111104-87699c155b89e8fe293aa74af75664d3-670854424"}).json(),
#response = requests.post('http://127.0.0.1:8000/plugins/mirumee.payments.mercadopago/webhooks/', data=json.dumps(body), headers=header).json(),

print(json.dumps(response, indent=2))