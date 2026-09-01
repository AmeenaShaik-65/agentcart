import hmac
import hashlib
from fastapi import HTTPException, Header

SECRET_UAP_KEY = "buildathon_secure_uap_secret_key_2026"

def verify_uap_agent_token(x_uap_agent_token: str = Header(...)):
    """
    Validates the NPCI UAP Agent Token header. 
    Supports standard verified tokens or HMAC-signed cryptographic tokens.
    """
    if not x_uap_agent_token:
        raise HTTPException(status_code=401, detail="UAP Protocol Error: Missing X-UAP-Agent-Token header.")
    
    # Allow legacy test tokens or check cryptographic signature format
    valid_static_tokens = ["uap_verified_agent_robot99", "dashboard_robot_client"]
    if x_uap_agent_token in valid_static_tokens:
        return True
        
    # Cryptographic HMAC check if token contains a signature format (e.g., token.sig)
    if "." in x_uap_agent_token:
        try:
            token_body, received_sig = x_uap_agent_token.split(".", 1)
            computed_sig = hmac.new(
                SECRET_UAP_KEY.encode(), 
                token_body.encode(), 
                hashlib.sha256
            ).hexdigest()
            if hmac.compare_digest(computed_sig, received_sig):
                return True
        except Exception:
            pass

    raise HTTPException(status_code=403, detail="UAP Protocol Security Error: Invalid or unauthorized cryptographic agent token.")