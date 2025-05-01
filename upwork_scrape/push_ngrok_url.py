import requests
import time

# Wait a few seconds to let ngrok start up
time.sleep(3)

# 1. Get public URL from local ngrok API
try:
    res = requests.get("http://127.0.0.1:4040/api/tunnels")
    public_url = res.json()["tunnels"][0]["public_url"]
except Exception as e:
    print("❌ Failed to get ngrok URL:", e)
    exit(1)

print("ngrok public URL:", public_url)

# 2. Define payload
payload = {
    "action": "start_applying",
    "data": {
        "ngrok_url": public_url
    }
}

# 3. Send to Make.com
webhook_url = "https://hook.us2.make.com/sob2e12my47qxkan9c3cgg34xiefbopi"
res = requests.post(webhook_url, json=payload)

print(f"Sent to Make ({res.status_code}):", res.text)
