import requests

def notify(msg):
    TOKEN = "TWÓJ_TOKEN"
    CHAT_ID = "TWÓJ_CHAT_ID"

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

print("Start trackera")

