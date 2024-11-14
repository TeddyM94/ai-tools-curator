"""
Utility helper functions for the AI Tools Curator.
"""

import re
from typing import Any, Dict, List
from datetime import datetime
import unicodedata

def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    Example: "Hello World!" -> "hello-world"
    """
    # Convert to lowercase and normalize unicode characters
    text = str(text).lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    
    # Replace any non-alphanumeric character with a hyphen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text

def format_date(date_str: str) -> str:
    """Format ISO date string to human-readable format."""
    date = datetime.fromisoformat(date_str)
    return date.strftime('%B %d, %Y')

def sort_tools(tools: Dict[str, Any], sort_by: str = 'date') -> List[Dict[str, Any]]:
    """Sort tools by specified criteria."""
    tools_list = list(tools.values())
    
    if sort_by == 'date':
        return sorted(tools_list, key=lambda x: x.get('added_date', ''), reverse=True)
    elif sort_by == 'score':
        return sorted(tools_list, key=lambda x: x.get('quality_score', 0), reverse=True)
    elif sort_by == 'name':
        return sorted(tools_list, key=lambda x: x.get('name', '').lower())
    
    return tools_list

def get_tool_categories(tools: Dict[str, Any]) -> List[str]:
    """Get sorted list of unique tool categories."""
    categories = set(tool.get('category', '') for tool in tools.values())
    return sorted(list(filter(None, categories)))

def truncate_text(text: str, length: int = 200) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'