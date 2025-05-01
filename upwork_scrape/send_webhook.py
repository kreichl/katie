import requests


payload = {
    "action": "stop_applying"
}


webhook_url = "https://hook.us2.make.com/sob2e12my47qxkan9c3cgg34xiefbopi"
res = requests.post(webhook_url, json=payload)

print(f"Sent to Make ({res.status_code}):", res.text)