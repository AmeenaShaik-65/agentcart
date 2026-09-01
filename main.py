from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import SessionLocal, init_db, ProductModel
from payment import create_razorpay_order
from guardrails import verify_spending_guardrail, log_audit_event
from negotiator import calculate_dynamic_bundle_discount
from upsell import generate_cross_sell_suggestion
from orchestrator import run_campaign_orchestrator
from uap_security import verify_uap_agent_token
from a2a_engine import evaluate_agent_counter_offer
from webhooks import dispatch_uap_webhook
import json

# Initialize Database on Startup
init_db()

app = FastAPI(
    title="AgentCart B2B Merchant API",
    description="Autonomous commerce endpoint for AI buyer agents featuring NPCI UAP protocol security, SQLite, discounts, guardrails, audit trails, and campaign orchestration.",
    version="2.3.0"
)

from fastapi.middleware.cors import CORSMiddleware

# Add CORS Middleware right after app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend origins for development & testing
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers (including X-UAP-Agent-Token)
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CheckoutRequest(BaseModel):
    ai_buyer_id: str
    items: list[CartItem]

class NegotiationRequest(BaseModel):
    ai_buyer_id: str
    items: list[CartItem]
    requested_discount_percentage: float

@app.get("/")
def home():
    return {"status": "online", "message": "AgentCart Merchant Node v2.3 (NPCI UAP Compliant) Active"}

@app.get("/catalog")
def get_catalog(db: Session = Depends(get_db)):
    # Catalog remains publicly discoverable for AI buyer discovery
    products = db.query(ProductModel).all()
    catalog_dict = {
        p.product_id: {
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
            "description": p.description
        } for p in products
    }
    return {"merchant_id": "merchant_razorpay_test_01", "available_items": catalog_dict}

@app.post("/agent/checkout")
def process_agent_checkout(
    order_req: CheckoutRequest, 
    db: Session = Depends(get_db),
    uap_auth: bool = Depends(verify_uap_agent_token)
):
    """
    Protected Checkout: Requires valid NPCI UAP token header ('X-UAP-Agent-Token').
    """
    subtotal = 0
    purchased_items = []

    try:
        for item in order_req.items:
            product = db.query(ProductModel).filter(ProductModel.product_id == item.product_id).first()
            if not product:
                log_audit_event("CHECKOUT_FAILED", {"buyer": order_req.ai_buyer_id, "reason": f"Product {item.product_id} not found."})
                raise HTTPException(status_code=400, detail=f"Graceful Recovery: Product ID '{item.product_id}' does not exist.")
            
            if product.stock < item.quantity:
                log_audit_event("CHECKOUT_FAILED", {"buyer": order_req.ai_buyer_id, "reason": f"Out of stock for {product.name}"})
                raise HTTPException(status_code=400, detail=f"Graceful Recovery: Insufficient stock for {product.name}.")
                
            subtotal += product.price * item.quantity
            purchased_items.append(item)

        final_amount, discount_message = calculate_dynamic_bundle_discount(purchased_items, subtotal)

        is_allowed, guardrail_message = verify_spending_guardrail(final_amount)
        if not is_allowed:
            raise HTTPException(status_code=403, detail=guardrail_message)

        receipt_code = f"rcpt_{order_req.ai_buyer_id[:6]}_{int(final_amount)}"
        razorpay_response = create_razorpay_order(final_amount, receipt_code)

        if not razorpay_response.get("success"):
            raise HTTPException(status_code=500, detail="Payment gateway connection failed.")

        upsells = generate_cross_sell_suggestion(purchased_items)

        log_audit_event("CHECKOUT_SUCCESS", {
            "buyer": order_req.ai_buyer_id,
            "subtotal_INR": subtotal,
            "discount_applied_INR": subtotal - final_amount,
            "final_amount_INR": final_amount,
            "razorpay_order": razorpay_response["order_id"]
        })

        # Dispatch signed webhook notification to registered AI buyer endpoint
        dispatch_uap_webhook(
            target_url="https://webhook.site/test-ai-buyer-endpoint", 
            event_type="CHECKOUT_SUCCESS", 
            payload={"order_id": razorpay_response["order_id"], "amount": final_amount}
        )

        return {
            "status": "success",
            "message": "Autonomous checkout order created successfully under UAP protocol security.",
            "buyer_id": order_req.ai_buyer_id,
            "subtotal_inr": subtotal,
            "discount_message": discount_message,
            "total_amount_inr": final_amount,
            "upsell_recommendations": upsells,
            "razorpay_order_details": razorpay_response
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        log_audit_event("UNEXPECTED_ERROR", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Graceful Failure Recovery Error: {str(e)}")

@app.post("/agent/campaigns")
def trigger_campaign_orchestrator(
    db: Session = Depends(get_db),
    uap_auth: bool = Depends(verify_uap_agent_token)
):
    """Triggers the Campaign Orchestrator with UAP security validation."""
    result = run_campaign_orchestrator(db, ProductModel)
    return result

@app.post("/agent/negotiate")
def agent_negotiation_endpoint(
    neg_req: NegotiationRequest,
    db: Session = Depends(get_db),
    uap_auth: bool = Depends(verify_uap_agent_token)
):
    """A2A Protocol: Autonomous price negotiation endpoint for AI buyer agents."""
    result = evaluate_agent_counter_offer(neg_req.items, neg_req.requested_discount_percentage, db, ProductModel)
    log_audit_event("A2A_NEGOTIATION", {"buyer": neg_req.ai_buyer_id, "result": result})
    return result

@app.get("/audit/logs")
def get_audit_logs():
    try:
        with open("audit_trail.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"logs": [], "message": "No audit events recorded yet."}