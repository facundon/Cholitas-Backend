import requests
import json

# response = requests.put('https://api.mercadopago.com/v1/payments/1231871522', json={"status":"approved"}, headers={"Authorization": "Bearer TEST-5363032924027795-111104-87699c155b89e8fe293aa74af75664d3-670854424"}).json()
# print(json.dumps(response, indent=2))

# response = requests.get('https://api.mercadopago.com/v1/payments/1231906945', headers={"Authorization": "Bearer TEST-5363032924027795-111104-87699c155b89e8fe293aa74af75664d3-670854424"}).json()
# print(json.dumps(response, indent=2))

body = {
    "action": "payment.created",
    "api_version": "v1",
    "data": {
        "id": "1231918354",
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

response = requests.post('http://127.0.0.1:8000/plugins/mirumee.payments.mercadopago/webhooks/', data=json.dumps(body), headers=header)
print(response)