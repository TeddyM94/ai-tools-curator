"""
GitHub Publisher module for managing content updates and deployment.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from utils.helpers import slugify
from github_publisher.static_generator import StaticGenerator

class GitHubPublisher:
    def __init__(self, config):
        """Initialize the GitHub publisher with configuration."""
        self.config = config
        self.data_dir = Path('data')
        self.content_dir = Path('docs')
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.content_dir.mkdir(exist_ok=True)
        
        # Load existing data
        self.tools_data = self._load_tools_data()
        
    def _load_tools_data(self) -> Dict[str, Any]:
        """Load existing tools data from file."""
        tools_file = self.data_dir / 'tools.json'
        if not tools_file.exists():
            return {}
        try:
            return json.loads(tools_file.read_text())
        except json.JSONDecodeError:
            return {}

    def _update_tools_data(self, new_tools: List[Dict[str, Any]]) -> None:
        """Update tools data with new discoveries."""
        for tool in new_tools:
            tool_id = slugify(tool['name'])
            if tool_id not in self.tools_data:
                tool['added_date'] = datetime.now().isoformat()
            tool['last_updated'] = datetime.now().isoformat()
            self.tools_data[tool_id] = tool
        
        # Save updated data
        tools_file = self.data_dir / 'tools.json'
        tools_file.write_text(json.dumps(self.tools_data, indent=4))

    def _create_weekly_digest(self) -> Dict[str, Any]:
        """Create weekly digest of new and trending tools."""
        now = datetime.now()
        digest = {
            'id': f"{now.year}-w{now.isocalendar()[1]:02d}",
            'week_number': now.isocalendar()[1],
            'year': now.year,
            'published_date': now.isoformat(),
            'highlights': [],
            'featured_tools': [],
            'trends': [],
            'categories': list(set(tool['category'] for tool in self.tools_data.values())),
            'stats': {
                'total_new_tools': len(self.tools_data),
                'avg_quality_score': sum(t.get('quality_score', 0) for t in self.tools_data.values()) / len(self.tools_data) if self.tools_data else 0,
                'top_category': max(set(tool['category'] for tool in self.tools_data.values()), key=list(tool['category'] for tool in self.tools_data.values()).count) if self.tools_data else None
            }
        }
        
        # Save digest
        digests_file = self.data_dir / 'digests.json'
        existing_digests = json.loads(digests_file.read_text()) if digests_file.exists() else []
        existing_digests.append(digest)
        digests_file.write_text(json.dumps(existing_digests, indent=4))
        
        return digest

    async def update_repository(self, new_tools: List[Dict[str, Any]]) -> None:
        """Update repository with new tools and generate site."""
        if new_tools:
            self._update_tools_data(new_tools)
        
        # Generate static site
        generator = StaticGenerator(self.config)
        generator.generate_site(self.tools_data)
        
        # Create weekly digest if it's Sunday
        if datetime.now().weekday() == 6:
            self._create_weekly_digest()