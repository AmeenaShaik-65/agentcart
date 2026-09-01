def calculate_dynamic_bundle_discount(items: list, subtotal: int) -> tuple[int, str]:
    """
    Simulates an intelligent merchant negotiation engine. 
    If an AI buyer purchases complementary items (e.g., Charger + Cable), 
    it automatically applies a dynamic 10% bundle discount.
    """
    product_ids = [item.product_id for item in items]
    
    # Check if both a charger and a cable are present in the cart
    if "item_001" in product_ids and "item_002" in product_ids:
        discount = int(subtotal * 0.10)  # 10% discount
        final_amount = subtotal - discount
        return final_amount, f"Applied Autonomous Bundle Discount: 10% off for pairing Charger and Cable (Saved {discount} INR)."
        
    return subtotal, "Standard pricing applied. No bundle triggers matched."