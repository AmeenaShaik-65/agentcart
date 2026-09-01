import hmac
import hashlib
import requests
import json

WEBHOOK_SECRET = "buildathon_webhook_secret_99"

def dispatch_uap_webhook(target_url: str, event_type: str, payload: dict):
    if not target_url:
        return {"dispatched": False, "reason": "No target webhook URL provided."}
        
    body_str = json.dumps(payload)
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body_str.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-UAP-Signature": signature,
        "X-UAP-Event": event_type
    }

    try:
        response = requests.post(target_url, data=body_str, headers=headers, timeout=3)
        return {"dispatched": True, "status_code": response.status_code}
    except Exception as e:
        return {"dispatched": False, "error": str(e)}