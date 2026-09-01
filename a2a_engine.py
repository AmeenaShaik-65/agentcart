def evaluate_agent_counter_offer(items, requested_discount_pct, db, product_model):
    subtotal = 0
    min_allowable_subtotal = 0
    
    for item in items:
        prod = db.query(product_model).filter(product_model.product_id == item.product_id).first()
        if not prod:
            return {"status": "rejected", "reason": f"Product {item.product_id} not found."}
        subtotal += prod.price * item.quantity
        # Floor cost threshold set safely at 70% of retail price
        min_allowable_subtotal += (prod.price * 0.70) * item.quantity

    proposed_amount = subtotal * (1 - (requested_discount_pct / 100))

    if proposed_amount >= min_allowable_subtotal:
        return {
            "status": "accepted",
            "approved_amount_inr": round(proposed_amount, 2),
            "negotiation_message": f"Counter-offer accepted at {requested_discount_pct}% discount by Merchant UAP Node."
        }
    else:
        max_safe_discount = round(((subtotal - min_allowable_subtotal) / subtotal) * 100, 1)
        return {
            "status": "counter_offer",
            "maximum_allowed_discount_pct": max_safe_discount,
            "counter_offer_amount_inr": round(subtotal * (1 - (max_safe_discount / 100)), 2),
            "negotiation_message": f"Requested discount breaches floor margin. Counter-offer extended at {max_safe_discount}% max discount."
        }