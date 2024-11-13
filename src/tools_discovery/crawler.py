"""
Tools Discovery System
Finds and validates new AI tools from various sources.

Sources:
- Product Hunt
- AlternativeTo
- FutureTools
- Custom sources
"""

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
from urllib.parse import urljoin
import time
import random
from typing import Dict, List, Any

class ToolsDiscovery:
    """
    Discovers new AI tools from multiple sources.
    
    Attributes:
        config: Configuration settings
        sources: Tool discovery sources
        discovered_tools: Previously found tools
        session: HTTP session manager
    
    Methods:
        find_new_tools: Main discovery method
        _scrape_source: Scrapes specific source
        _parse_tool: Extracts tool information
        _process_tools: Validates and filters tools
    """
    
    def __init__(self, config):
        self.config = config
        
        # Initialize data storage
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.discovered_file = self.data_dir / 'discovered_tools.json'
        
        # Load previously discovered tools
        self.discovered_tools = self._load_discovered_tools()
        
        # Sources for AI tools
        self.sources = {
            'producthunt': {
                'url': 'https://www.producthunt.com/topics/artificial-intelligence',
                'selector': 'div[class*="item_"]',
                'name_selector': 'h3',
                'description_selector': 'p',
                'link_selector': 'a[href*="/posts/"]'
            },
            'alternativeto': {
                'url': 'https://alternativeto.net/category/artificial-intelligence/',
                'selector': 'div.app-listing',
                'name_selector': 'h2',
                'description_selector': 'div.description',
                'link_selector': 'a.app-link'
            },
            'futuretools': {
                'url': 'https://futuretools.io/',
                'selector': 'div.tool-card',
                'name_selector': 'h3.tool-name',
                'description_selector': 'p.tool-description',
                'link_selector': 'a.tool-link'
            }
        }
        
        # Initialize session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def find_new_tools(self) -> List[Dict[str, Any]]:
        """
        Find new AI tools from all sources.
        
        Returns:
            List of new tool dictionaries
        """
        new_tools = []
        
        for source_name, source_config in self.sources.items():
            try:
                logging.info(f"Scanning source: {source_name}")
                
                # Respect rate limits
                time.sleep(random.uniform(2, 5))
                
                # Scrape source
                tools = self._scrape_source(source_name, source_config)
                
                # Process and validate tools
                valid_tools = self._process_tools(tools, source_name)
                
                # Add new tools
                for tool in valid_tools:
                    if tool['name'] not in self.discovered_tools:
                        new_tools.append(tool)
                        self._record_tool(tool)
                
                logging.info(f"Found {len(valid_tools)} tools from {source_name}")
                
            except Exception as e:
                logging.error(f"Error scanning {source_name}: {e}")
        
        return new_tools
    
    def _scrape_source(self, source_name: str, source_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scrape tools from a specific source.
        
        Args:
            source_name: Name of the source
            source_config: Source configuration
            
        Returns:
            List of tool dictionaries
        """
        tools = []
        
        try:
            response = self.session.get(source_config['url'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select(source_config['selector'])
            
            for item in items:
                tool = self._parse_tool(item, source_config, source_name)
                if tool:
                    tools.append(tool)
        
        except Exception as e:
            logging.error(f"Error scraping {source_name}: {e}")
        
        return tools
    
    def _parse_tool(self, item: BeautifulSoup, config: Dict[str, str], source: str) -> Dict[str, Any]:
        """
        Extract tool information from HTML.
        
        Args:
            item: BeautifulSoup object
            config: Source configuration
            source: Source name
            
        Returns:
            Tool dictionary or None if invalid
        """
        try:
            # Extract name
            name_elem = item.select_one(config['name_selector'])
            if not name_elem:
                return None
            name = name_elem.text.strip()
            
            # Extract description
            desc_elem = item.select_one(config['description_selector'])
            description = desc_elem.text.strip() if desc_elem else ""
            
            # Extract URL
            link_elem = item.select_one(config['link_selector'])
            if not link_elem or not link_elem.get('href'):
                return None
            url = urljoin(config['url'], link_elem['href'])
            
            # Extract features (if available)
            features = self._extract_features(item)
            
            return {
                'name': name,
                'description': description,
                'url': url,
                'features': features,
                'source': source,
                'discovered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error parsing tool: {e}")
            return None
    
    def _process_tools(self, tools: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
        """
        Validate and clean tool data.
        
        Args:
            tools: List of tool dictionaries
            source: Source name
            
        Returns:
            List of validated tool dictionaries
        """
        valid_tools = []
        
        for tool in tools:
            # Skip if missing required fields
            if not all(k in tool for k in ['name', 'url']):
                continue
            
            # Clean and validate data
            tool['name'] = self._clean_text(tool['name'])
            tool['description'] = self._clean_text(tool.get('description', ''))
            tool['url'] = self._clean_url(tool['url'])
            
            # Validate URL
            if not self._is_valid_url(tool['url']):
                continue
            
            # Add metadata
            tool['source'] = source
            tool['discovered_at'] = datetime.now().isoformat()
            
            valid_tools.append(tool)
        
        return valid_tools
    
    def _extract_features(self, item: BeautifulSoup) -> List[str]:
        """Extract features from tool listing"""
        features = []
        
        # Common feature selectors
        feature_selectors = [
            'ul.features li',
            'div.features span',
            'div[class*="feature"]'
        ]
        
        for selector in feature_selectors:
            elements = item.select(selector)
            features.extend([elem.text.strip() for elem in elements])
        
        return [f for f in features if f]  # Remove empty strings
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Normalize whitespace
        text = ' '.join(text.split())
        # Remove special characters
        text = re.sub(r'[^\w\s\-.,!?]', '', text)
        return text
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def _record_tool(self, tool: Dict[str, Any]) -> None:
        """Record discovered tool"""
        self.discovered_tools[tool['name']] = {
            'discovered_at': tool['discovered_at'],
            'url': tool['url']
        }
        self._save_discovered_tools()
    
    def _load_discovered_tools(self) -> Dict[str, Any]:
        """Load previously discovered tools"""
        try:
            if self.discovered_file.exists():
                return json.loads(self.discovered_file.read_text())
        except Exception as e:
            logging.error(f"Error loading discovered tools: {e}")
        return {}
    
    def _save_discovered_tools(self) -> None:
        """Save discovered tools"""
        try:
            self.discovered_file.write_text(json.dumps(self.discovered_tools, indent=2))
        except Exception as e:
            logging.error(f"Error saving discovered tools: {e}")