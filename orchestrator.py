import datetime
from guardrails import log_audit_event

def run_campaign_orchestrator(db_session, product_model) -> dict:
    """
    Proactive AI Campaign Orchestrator: Analyzes merchant stock and performance 
    to automatically trigger revenue-boosting flash campaigns or clearance events.
    """
    products = db_session.query(product_model).all()
    campaign_actions = []

    for p in products:
        # If stock is high, orchestrator triggers an automated flash sale campaign to grow revenue
        if p.stock > 15:
            campaign_id = f"camp_flash_{p.product_id}_{datetime.datetime.now().strftime('%Y%m%d')}"
            action = {
                "campaign_id": campaign_id,
                "target_product": p.name,
                "strategy": "Automated Volume Push & Cross-Sell Bundle",
                "status": "active_broadcasted_to_ai_buyers"
            }
            campaign_actions.append(action)
            log_audit_event("CAMPAIGN_ORCHESTRATED", action)
            
    return {
        "orchestrator_status": "success",
        "active_campaigns_count": len(campaign_actions),
        "campaigns": campaign_actions
    }