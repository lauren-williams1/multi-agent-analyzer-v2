# sample_data.py

SAMPLE_DATASETS = {
    "ecommerce_sales": {
        "Q4_2024": {
            "total_revenue": "$2.4M",
            "units_sold": 45600,
            "avg_order_value": "$52.63",
            "top_categories": [
                {"name": "Electronics", "revenue": "$890K", "growth": "+15%"},
                {"name": "Home & Garden", "revenue": "$650K", "growth": "+8%"},
                {"name": "Clothing", "revenue": "$540K", "growth": "-3%"},
                {"name": "Sports", "revenue": "$320K", "growth": "+22%"}
            ],
            "traffic_sources": {
                "organic_search": "35%",
                "paid_ads": "28%",
                "direct": "22%",
                "social_media": "15%"
            },
            "conversion_rate": "3.2%",
            "cart_abandonment": "68%",
            "returning_customers": "42%"
        },
        "Q3_2024": {
            "total_revenue": "$1.9M",
            "units_sold": 38200,
            "avg_order_value": "$49.74"
        }
    },
    "saas_metrics": {
        "monthly_data": {
            "mrr": "$450K",
            "arr": "$5.4M",
            "total_customers": 1250,
            "new_signups": 87,
            "churned_customers": 23,
            "churn_rate": "1.84%",
            "ltv": "$4800",
            "cac": "$1200",
            "ltv_cac_ratio": 4.0,
            "net_retention": "112%"
        }
    },
    "marketing_campaign": {
        "Q4_campaign": {
            "total_spend": "$125K",
            "impressions": "2.4M",
            "clicks": "48K",
            "ctr": "2.0%",
            "conversions": 856,
            "conversion_rate": "1.78%",
            "cpa": "$146",
            "roas": 3.2,
            "channels": [
                {"name": "Google Ads", "spend": "$65K", "conversions": 520, "roas": 3.8},
                {"name": "Facebook", "spend": "$35K", "conversions": 210, "roas": 2.4},
                {"name": "LinkedIn", "spend": "$25K", "conversions": 126, "roas": 2.8}
            ]
        }
    }
}

def get_relevant_data(query: str) -> dict:
    """
    Simple keyword matching to return relevant sample data
    """
    query_lower = query.lower()
    
    # E-commerce keywords
    if any(word in query_lower for word in ["ecommerce", "e-commerce", "sales", "revenue", "q4"]):
        return {
            "data_source": "E-commerce Sales Database",
            "data": SAMPLE_DATASETS["ecommerce_sales"]
        }
    
    # SaaS keywords
    elif any(word in query_lower for word in ["saas", "churn", "subscription", "mrr", "arr"]):
        return {
            "data_source": "SaaS Metrics Dashboard",
            "data": SAMPLE_DATASETS["saas_metrics"]
        }
    
    # Marketing keywords
    elif any(word in query_lower for word in ["marketing", "campaign", "roi", "roas", "ads"]):
        return {
            "data_source": "Marketing Analytics Platform",
            "data": SAMPLE_DATASETS["marketing_campaign"]
        }
    
    # Default - return e-commerce data
    else:
        return {
            "data_source": "General Business Database",
            "data": SAMPLE_DATASETS["ecommerce_sales"]
        }