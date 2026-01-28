import pandas as pd

def convert_sales_report_to_string(json_data: dict) -> str:
    output = ""

    # Brand & Product Mapping
    output += "# Brand & Product Mapping\n\n"
    
    brand_mapping = json_data.get("brand_product_mapping", {})
    naga_products = brand_mapping.get("naga_brand_products", {})
    
    if naga_products.get("products_list"):
        output += "A. Naga Brand Products\n\n"
        for product in naga_products.get("products_list", []):
            output += f"- {product}\n"

    else:
        output += "No Naga products mentioned.\n\n------------------------------------------------------------\n\n"
    
    output += "\nB. Competitor Brands Mentioned\n\n"
    competitor_list = json_data.get("competitive_intelligence_and_customer_psychology", {}).get('competitor_brand_analysis', [])
    
    if competitor_list:
        df = pd.DataFrame(competitor_list)
        # Ensure columns exist, filling missing ones with N/A
        expected_cols = ['brand_name', 'product', 'reasons_for_preference', 'category']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = "N/A"
                
        cols_to_keep = ['brand_name', 'product', 'reasons_for_preference', 'category']
        filtered_df = df[cols_to_keep]
        filtered_df = filtered_df.rename(columns={
            'brand_name': 'Competitor Brand Name',
            'product': 'Products',
            'reasons_for_preference': 'Preference Reasons',
            'category': 'Category'
        })
        table_string = filtered_df.to_markdown(index=False)
        output += table_string + "\n\n------------------------------------------------------------\n\n"
    else:
        output += "No competitor brands mentioned.\n\n------------------------------------------------------------\n\n"

    # 1. Conversation Summary
    output += "# 1. Conversation Summary\n\n"
    conversation_summary = json_data.get("conversation_summary", {})
    if conversation_summary.get('summary_points'):
        for point in conversation_summary.get("summary_points", []):
            output += f"- {point}\n"
    else:
        output += "No conversation summary available.\n"
    output += "\n------------------------------------------------------------\n\n"

    # 2. Sales Matrix
    output += "# 2. Sales Matrix\n\n"
    output += "**Naga Products Performance**\n\n"
    
    sales_matrix = json_data.get("sales_matrix", {})
    naga_performance = sales_matrix.get("naga_products_performance", {})
    if naga_performance:
        output += f"- **Naga products promoted**: {naga_performance.get('naga_products_promoted', 'N/A')}\n\n"
        output += f"- **Volume pushed / upselling**: {naga_performance.get('volume_pushed_upselling', 'N/A')}\n\n"
        
        schemes_offered = naga_performance.get("schemes_offered", {})
        output += "- **Schemes offered**:\n\n"
        if schemes_offered:
            output += f"{schemes_offered.get('description', 'No description available')}\n\n"
            for scheme in schemes_offered.get("scheme_details", []):
                output += f"  - **{scheme.get('product', 'N/A')}**: {scheme.get('scheme', 'N/A')}\n"
            output += "\n"
        else:
            output += "  No schemes offered.\n\n"

        output += f"- **Cross-selling within Naga portfolio**: {naga_performance.get('cross_selling_within_naga_portfolio', 'N/A')}\n\n"
        
        acceptance_rejection = naga_performance.get("acceptance_rejection", {})
        output += "- **Acceptance/Rejection**:\n\n"
        output += "  - **Accepted**: "
        accepted = acceptance_rejection.get("accepted", [])
        output += ", ".join(accepted) if accepted else "No products accepted"
        output += "\n\n  - **Rejected**: "
        rejected = acceptance_rejection.get("rejected", [])
        output += ", ".join(rejected) if rejected else "No products rejected"
        output += "\n\n"
    else:
        output += "No Naga products performance data available.\n\n"
    
    sales_barriers = sales_matrix.get("sales_barriers", {})
    if sales_barriers:
        output += "**Sales Barriers**\n\n"
        output += f"- **Objections raised**: {sales_barriers.get('objections_raised', 'No objections raised')}\n\n"
        output += f"- **Competitor advantages cited**: {sales_barriers.get('competitor_advantages_cited', 'No competitor advantages cited')}\n\n"
    else:
        output += "No sales barriers data available.\n\n"
    output += "------------------------------------------------------------\n\n"

    # 3. Customer Buying Patterns
    output += "# 3. Customer Buying Patterns\n\n"
    buying_patterns = json_data.get("customer_buying_patterns", {})
    if buying_patterns:
        regular = buying_patterns.get("regularly_buying_products", {})
        if regular.get('products'):
            output += f"A. Regularly buying products ({regular.get('description', 'N/A')})\n\n"
            regular_products = regular.get("products", [])
            for product in regular_products:
                output += f"- {product}\n"
        else:
            output += "No Regular buying products found\n"
        output += "\n"
        
        scheme_based = buying_patterns.get("scheme_based_orders", {})
        if scheme_based.get('products'):
            output += f"B. Scheme Based Orders ({scheme_based.get('description', 'N/A')})\n\n"
            scheme_products = scheme_based.get("products", [])
            for product in scheme_products:
                output += f"- {product}\n"
        else:
            output += "No Scheme Based Orders found\n"
    else:
        output += "No customer buying patterns data available.\n"
    output += "\n------------------------------------------------------------\n\n"

    # 4. Competitive Intelligence & Customer Psychology
    output += "# 4. Competitive Intelligence & Customer Psychology\n\n"
    competitive_intel = json_data.get("competitive_intelligence_and_customer_psychology", {})
    if competitive_intel:
        output += "A. Competitor Brand Analysis\n\n"
        if competitive_intel.get("competitor_brand_analysis"):
            for index, brand in enumerate(competitive_intel.get("competitor_brand_analysis", [])):
                output += f"**Brand {index + 1}:**\n\n"
                output += f"- **Brand Name**: {brand.get('brand_name', 'N/A')}\n"
                output += f"- **Products**: {brand.get('product', 'N/A')}\n"
                output += f"- **Customer's Current Status**: {brand.get('customer_current_status', 'N/A')}\n"
                output += f"- **Reasons for Preference**: {brand.get('reasons_for_preference', 'N/A')}\n"
                output += f"- **Category**: {brand.get('category', 'N/A')}\n\n"
        else:
            output += "No competitor brand analysis data available.\n\n"

        online_retailers = competitive_intel.get("online_retailers_mentioned", [])
        if online_retailers:
            output += "B. Online Retailers Mentioned\n\n"
            for index, retailer in enumerate(online_retailers):
                output += f"**Retailer {index + 1}:**\n\n"
                output += f"- **Name**: {retailer.get('name', 'N/A')}\n"
                output += f"- **Product Range**: {retailer.get('product_range', 'N/A')}\n"
                output += f"- **Pricing Strategy**: {retailer.get('pricing_strategy', 'N/A')}\n"
                output += f"- **Customer Perception**: {retailer.get('customer_perception', 'N/A')}\n"
                output += f"- **Unique Selling Points**: {retailer.get('unique_selling_points', 'N/A')}\n\n"

        customer_psychology = competitive_intel.get("customer_buying_psychology", {})
        if customer_psychology:
            output += "C. Customer Buying Psychology\n\n"
            output += "- **What truly drives purchase decisions**:\n\n"
            if customer_psychology.get("purchase_decision_drivers_ranked"):
                for index, driver in enumerate(customer_psychology.get("purchase_decision_drivers_ranked", [])):
                    output += f"  {index + 1}. {driver}\n"
            else:
                output += "  No purchase decision drivers data available.\n"
            output += "\n"
            output += f"- **Customer's risk tolerance**: {customer_psychology.get('risk_tolerance', 'N/A')}\n\n"
            output += f"- **Stock rotation preferences**: {customer_psychology.get('stock_rotation_preferences', 'N/A')}\n\n"
            output += f"- **Openness to switching brands**: {customer_psychology.get('openness_to_switching', 'N/A')}\n\n"
            output += f"- **How is the customer buying behaviour**: {customer_psychology.get('buying_behaviour', 'N/A')}\n\n"
        else:
            output += "No customer buying psychology data available.\n\n"
    else:
        output += "No competitive intelligence or customer psychology data available.\n\n"
    output += "------------------------------------------------------------\n\n"

    # 5. Salesperson Effectiveness Score
    output += "# 5. Salesperson Effectiveness Score\n\n"
    effectiveness = json_data.get("salesperson_effectiveness_score", {})
    scores = effectiveness.get("scores", {})
    if scores:
        product_promo = scores.get("product_promotion", {})
        output += f"**Product promotion ({product_promo.get('weight_percentage', 'N/A')}% weight):** {product_promo.get('score', 'N/A')}/10\n"
        output += f"- {product_promo.get('justification', 'N/A')}\n\n"
        
        scheme_lev = scores.get("scheme_leverage", {})
        output += f"**Scheme leverage ({scheme_lev.get('weight_percentage', 'N/A')}% weight):** {scheme_lev.get('score', 'N/A')}/10\n"
        output += f"- {scheme_lev.get('justification', 'N/A')}\n\n"
        
        competitor_handling = scores.get("competitor_handling", {})
        output += f"**Competitor handling ({competitor_handling.get('weight_percentage', 'N/A')}% weight):** {competitor_handling.get('score', 'N/A')}/10"
        if competitor_handling.get("is_na"):
            output += " (N/A)"
        output += "\n"
        output += f"- {competitor_handling.get('justification', 'N/A')}\n\n"
        
        cust_psych = scores.get("customer_psychology_understanding", {})
        output += f"**Customer psychology understanding ({cust_psych.get('weight_percentage', 'N/A')}% weight):** {cust_psych.get('score', 'N/A')}/10\n"
        output += f"- {cust_psych.get('justification', 'N/A')}\n\n"
    else:
        output += "No salesperson effectiveness scores available.\n\n"
    
    final_calc = effectiveness.get("final_score_calculation", {})
    if final_calc:
        output += "**Final Score Calculation:**\n\n"
        output += f"{final_calc.get('formula', 'N/A')} = {final_calc.get('final_score', 'N/A')} / 10\n\n"
    else:
        output += "No final score calculation available.\n\n"
    output += "------------------------------------------------------------\n\n"

    # 6. Salesperson Ability Analysis
    output += "# 6. Salesperson Ability Analysis\n\n"
    output += f"- {json_data.get('salesperson_ability_analysis', 'N/A')}\n\n"
    output += "------------------------------------------------------------\n\n"

    # 7. Product Price Analysis
    output += "# 7. Product Price Analysis\n\n"
    price_analysis = json_data.get("product_price_analysis", {})
    if price_analysis:
        output += f"- {price_analysis.get('summary', 'N/A')}\n\n"
        for product in price_analysis.get("high_price_products", []):
            output += f"  - **{product.get('product', 'N/A')}**\n"
            output += f"    - Price Point: {product.get('price_point', 'N/A')}\n"
            output += f"    - Customer's Exact Concerns: {product.get('customer_exact_concerns', 'N/A')}\n\n"
    else:
        output += "No product price analysis data available.\n\n"
    output += "------------------------------------------------------------\n\n"

    # 8. Salesperson Strengths
    output += "# 8. Salesperson Strengths\n\n"
    if json_data.get("salesperson_strengths"):
        for strength in json_data.get("salesperson_strengths", []):
            output += f"- {strength}\n"
    else:
        output += "No salesperson strengths found.\n"
    output += "\n------------------------------------------------------------\n\n"

    # 9. Areas for Improvement
    output += "# 9. Areas for Improvement\n\n"
    if json_data.get("areas_for_improvement"):
        for area in json_data.get("areas_for_improvement", []):
            output += f"- {area}\n"
    else:
        output += "No areas for improvement found.\n"
    output += "\n------------------------------------------------------------\n"

    return output