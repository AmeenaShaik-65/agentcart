import datetime
import json

# Define strict business safety rules
MAX_SPEND_LIMIT_INR = 5000  # An AI buyer can never spend more than 5000 INR in one go
AUDIT_LOG_FILE = "audit_trail.json"

def log_audit_event(event_type: str, details: dict):
    """
    Creates an immutable audit trail record for every single money or inventory action.
    """
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": details
    }
    
    # Append to our local audit log file
    try:
        try:
            with open(AUDIT_LOG_FILE, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
            
        logs.append(log_entry)
        
        with open(AUDIT_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)
            
    except Exception as e:
        print(f"Audit log error: {e}")

def verify_spending_guardrail(total_amount: int) -> tuple[bool, str]:
    """
    Gates and bounds financial actions. Checks if the requested amount 
    exceeds our safety limit.
    """
    if total_amount <= 0:
        return False, "Invalid transaction amount. Amount must be greater than zero."
        
    if total_amount > MAX_SPEND_LIMIT_INR:
        log_audit_event("GUARDRAIL_BREACH_BLOCKED", {"attempted_amount": total_amount, "limit": MAX_SPEND_LIMIT_INR})
        return False, f"Blocked by AgentCart Safety Guardrail: Requested amount {total_amount} INR exceeds maximum allowed limit of {MAX_SPEND_LIMIT_INR} INR."
        
    return True, "Guardrail passed successfully."