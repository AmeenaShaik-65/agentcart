def generate_cross_sell_suggestion(items: list) -> list[str]:
    """
    Analyzes the AI buyer's cart items and recommends complementary products
    to maximize merchant revenue programmatically.
    """
    product_ids = [item.product_id for item in items]
    suggestions = []
    
    # If buying charger but forgot the cable
    if "item_001" in product_ids and "item_002" not in product_ids:
        suggestions.append("AI Upsell Recommendation: Add 'Type-C Braided Cable 2m' (item_002) to unlock a 10% bundle discount!")
        
    # If buying cable but forgot the charger
    if "item_002" in product_ids and "item_001" not in product_ids:
        suggestions.append("AI Upsell Recommendation: Add 'Superfast 65W Phone Charger' (item_001) for optimal charging speeds and a 10% bundle discount.")
        
    return suggestions