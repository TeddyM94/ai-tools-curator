import json
from datetime import datetime
import os

def save_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)

def load_json(filename):
    """Load data from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def is_valid_tool(tool):
    """Validate tool data structure"""
    required_fields = ['name', 'description', 'url']
    return all(field in tool for field in required_fields)

def format_price(price):
    """Format price string consistently"""
    if not price:
        return "Contact for pricing"
    try:
        price_float = float(str(price).replace('$', '').replace(',', ''))
        return f"${price_float:,.2f}"
    except:
        return str(price)