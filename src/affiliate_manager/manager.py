"""
Affiliate Management System
Handles affiliate link generation and tracking.

Features:
- Link generation
- Program matching
- Conversion tracking
- Revenue analysis
"""

import json
from pathlib import Path
import logging
from typing import Dict, List, Any
from datetime import datetime
import re

class AffiliateManager:
    """
    Manages affiliate marketing integration.
    
    Attributes:
        config: Configuration settings
        affiliate_programs: Available programs
        conversion_tracker: Tracks conversions
    
    Methods:
        add_affiliate_links: Generates affiliate links
        track_conversion: Records conversions
        get_revenue_report: Analyzes affiliate revenue
        _match_affiliate_program: Matches tools to programs
    """
    
    def __init__(self):
        self.data_dir = Path('data/affiliate')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data files
        self.programs_file = self.data_dir / 'programs.json'
        self.conversions_file = self.data_dir / 'conversions.json'
        
        # Load or create affiliate programs data
        self.affiliate_programs = self._load_programs()
        self.conversions = self._load_conversions()
        
        # Initialize tracking
        self.start_time = datetime.now()
    
    def add_affiliate_links(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add affiliate links to tools.
        
        Args:
            tools: List of tool dictionaries
            
        Returns:
            Updated tools list with affiliate links
        """
        for tool in tools:
            program = self._match_affiliate_program(tool)
            if program:
                tool['affiliate_link'] = self._generate_affiliate_link(
                    tool['url'],
                    program
                )
                tool['affiliate_program'] = program['name']
            else:
                tool['affiliate_link'] = tool['url']
                tool['affiliate_program'] = None
        
        return tools
    
    def track_conversion(self, tool_name: str, amount: float, program: str) -> None:
        """
        Track an affiliate conversion.
        
        Args:
            tool_name: Name of the tool
            amount: Conversion amount
            program: Affiliate program name
        """
        conversion = {
            'tool': tool_name,
            'program': program,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
        
        conversion_id = f"conv_{datetime.now().isoformat()}"
        self.conversions[conversion_id] = conversion
        self._save_conversions()
        
        logging.info(f"Tracked conversion for {tool_name}: ${amount}")
    
    def get_revenue_report(self) -> Dict[str, Any]:
        """
        Generate revenue report.
        
        Returns:
            Dictionary containing revenue metrics
        """
        report = {
            'total_revenue': 0,
            'by_program': {},
            'by_tool': {},
            'conversion_count': len(self.conversions),
            'period': {
                'start': self.start_time.isoformat(),
                'end': datetime.now().isoformat()
            }
        }
        
        for conversion in self.conversions.values():
            amount = conversion['amount']
            program = conversion['program']
            tool = conversion['tool']
            
            # Update totals
            report['total_revenue'] += amount
            
            # Update program totals
            if program not in report['by_program']:
                report['by_program'][program] = 0
            report['by_program'][program] += amount
            
            # Update tool totals
            if tool not in report['by_tool']:
                report['by_tool'][tool] = 0
            report['by_tool'][tool] += amount
        
        return report
    
    def _match_affiliate_program(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match tool to appropriate affiliate program.
        
        Args:
            tool: Tool dictionary
            
        Returns:
            Matching program dictionary or None
        """
        tool_url = tool['url'].lower()
        tool_name = tool['name'].lower()
        
        for program in self.affiliate_programs:
            # Check domain matches
            if any(domain in tool_url for domain in program['domains']):
                return program
            
            # Check name matches
            if any(name in tool_name for name in program['tool_names']):
                return program
            
            # Check category matches
            tool_text = f"{tool_name} {tool.get('description', '')}".lower()
            if any(category in tool_text for category in program['categories']):
                return program
        
        return None
    
    def _generate_affiliate_link(self, url: str, program: Dict[str, Any]) -> str:
        """
        Generate affiliate link for a tool.
        
        Args:
            url: Original tool URL
            program: Affiliate program dictionary
            
        Returns:
            Affiliate link
        """
        # Clean the URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Apply program-specific link generation
        template = program['link_template']
        affiliate_id = program['affiliate_id']
        
        # Replace placeholders
        link = template.replace('{url}', url)
        link = link.replace('{affiliate_id}', affiliate_id)
        
        return link
    
    def _load_programs(self) -> List[Dict[str, Any]]:
        """Load affiliate programs data"""
        try:
            if self.programs_file.exists():
                return json.loads(self.programs_file.read_text())
        except Exception as e:
            logging.error(f"Error loading affiliate programs: {e}")
        
        # Return default programs if file doesn't exist
        return [
            {
                'name': 'GetResponse',
                'domains': ['getresponse.com'],
                'tool_names': ['getresponse'],
                'categories': ['email', 'marketing', 'automation'],
                'link_template': 'https://www.getresponse.com/?a={affiliate_id}&c={url}',
                'affiliate_id': 'DEFAULT_ID'
            },
            {
                'name': 'Systeme',
                'domains': ['systeme.io'],
                'tool_names': ['systeme'],
                'categories': ['marketing', 'sales', 'funnel'],
                'link_template': 'https://systeme.io/{affiliate_id}?via={url}',
                'affiliate_id': 'DEFAULT_ID'
            }
        ]
    
    def _load_conversions(self) -> Dict[str, Any]:
        """Load conversion history"""
        try:
            if self.conversions_file.exists():
                return json.loads(self.conversions_file.read_text())
        except Exception as e:
            logging.error(f"Error loading conversions: {e}")
        return {}
    
    def _save_conversions(self) -> None:
        """Save conversion history"""
        try:
            self.conversions_file.write_text(json.dumps(self.conversions, indent=2))
        except Exception as e:
            logging.error(f"Error saving conversions: {e}")