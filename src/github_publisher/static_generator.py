"""
Static site generator for AI Tools Curator.
"""

import logging
from pathlib import Path
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
import shutil

class StaticGenerator:
    def __init__(self, config):
        self.config = config
        self.output_dir = Path('docs')
        self.template_dir = Path('templates')
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        
        # Add custom filters
        self.env.filters['format_date'] = self.format_date
        
    def format_date(self, date_str: str) -> str:
        """Format ISO date string to human-readable format."""
        try:
            if isinstance(date_str, str):
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date = date_str
            return date.strftime('%B %d, %Y')
        except Exception as e:
            logging.error(f"Error formatting date {date_str}: {e}")
            return date_str

    def generate_site(self, tools_data: dict) -> None:
        """Generate static site from tools data."""
        try:
            print("🏗️ Generating static site...")
            
            # Prepare data
            tools_list = list(tools_data.values())
            categories = self._get_categories(tools_list)
            
            # Calculate stats
            stats = self._calculate_stats(tools_list)
            
            # Prepare category tools
            category_tools = self._prepare_category_tools(tools_list)
            
            # Generate index page
            self._generate_index(tools_list, categories, stats, category_tools)
            
            # Generate category pages
            for category in categories:
                self._generate_category(category, tools_list, stats)
            
            # Generate individual tool pages
            for tool in tools_list:
                self._generate_tool_page(tool, tools_list)
            
            # Copy static assets
            self._copy_static_assets()
            
            print("✨ Site generated successfully!")
            logging.info("Static site generated successfully")
            
        except Exception as e:
            logging.error(f"Error generating static site: {str(e)}")
            raise

    def _get_categories(self, tools: list) -> list:
        """Get sorted list of unique categories."""
        return sorted(list(set(tool['category'] for tool in tools if 'category' in tool)))

    def _calculate_stats(self, tools: list) -> dict:
        """Calculate site statistics."""
        now = datetime.now(timezone.utc)
        week_ago = now.timestamp() - (7 * 24 * 60 * 60)
        
        return {
            'total_tools': len(tools),
            'categories': len(self._get_categories(tools)),
            'this_week': len([t for t in tools if 
                datetime.fromisoformat(t['added_date'].replace('Z', '+00:00')).timestamp() > week_ago
            ]),
            'avg_quality': sum(t.get('quality_score', 0) for t in tools) / len(tools) if tools else 0
        }

    def _prepare_category_tools(self, tools: list) -> dict:
        """Prepare tools organized by category."""
        category_tools = {}
        for tool in tools:
            category = tool.get('category')
            if category:
                if category not in category_tools:
                    category_tools[category] = []
                category_tools[category].append(tool)
        return category_tools

    def _prepare_tool_data(self, tool: dict) -> dict:
        """Prepare tool data with all required fields."""
        tool_data = tool.copy()
        
        # Ensure basic fields
        tool_data['id'] = tool_data.get('id') or tool_data['name'].lower().replace(' ', '-')
        
        # Create metrics dictionary
        metrics = {
            'views': 0,
            'clicks': 0,
            'rating': tool_data.get('quality_score', 0) * 5  # Convert 0-1 score to 0-5 rating
        }
        
        # Update with existing metrics if they exist
        if 'metrics' in tool_data:
            metrics.update(tool_data['metrics'])
        tool_data['metrics'] = metrics
        
        # Handle quality details
        quality_score = tool_data.get('quality_score', 0)
        if 'quality_details' not in tool_data:
            tool_data['quality_details'] = {
                'Description': quality_score,
                'Features': quality_score,
                'Documentation': quality_score
            }
        elif isinstance(tool_data['quality_details'], dict):
            if 'scores' in tool_data['quality_details']:
                # Convert from quality_details.scores format
                tool_data['quality_details'] = {
                    k.replace('_quality', '').title(): v 
                    for k, v in tool_data['quality_details']['scores'].items()
                }
        
        return tool_data

    def _generate_index(self, tools: list, categories: list, stats: dict, category_tools: dict) -> None:
        """Generate index page."""
        template = self.env.get_template('index.html')
        
        # Prepare all tools with required fields
        prepared_tools = [self._prepare_tool_data(tool) for tool in tools]
        
        # Sort tools by date for latest tools
        latest_tools = sorted(
            prepared_tools,
            key=lambda x: datetime.fromisoformat(x['added_date'].replace('Z', '+00:00')),
            reverse=True
        )[:10]
        
        # Sort tools by quality score for top rated
        top_rated = sorted(
            prepared_tools,
            key=lambda x: x.get('quality_score', 0),
            reverse=True
        )[:6]
        
        # Prepare category tools
        prepared_category_tools = {
            category: [self._prepare_tool_data(tool) for tool in tools]
            for category, tools in category_tools.items()
        }
        
        content = template.render(
            latest_tools=latest_tools,
            top_rated=top_rated,
            categories=categories,
            category_tools=prepared_category_tools,
            stats=stats,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        (self.output_dir / 'index.html').write_text(content)

    def _generate_category(self, category: str, tools: list, stats: dict) -> None:
        """Generate category page."""
        template = self.env.get_template('category.html')
        
        # Filter and prepare tools for this category
        category_tools = [
            self._prepare_tool_data(tool) 
            for tool in tools 
            if tool.get('category') == category
        ]
        
        content = template.render(
            category=category,
            tools=category_tools,
            stats=stats,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        category_dir = self.output_dir / 'categories'
        category_dir.mkdir(exist_ok=True)
        (category_dir / f'{category.lower().replace(" ", "-")}.html').write_text(content)

    def _generate_tool_page(self, tool: dict, all_tools: list) -> None:
        """Generate individual tool page."""
        try:
            logging.info(f"Starting to generate page for tool: {tool.get('name', 'unknown')}")
            
            # Prepare tool data with all required fields
            tool_data = self._prepare_tool_data(tool)
            
            # Find similar tools and prepare them
            similar_tools = [
                self._prepare_tool_data(t) 
                for t in self._find_similar_tools(tool_data, all_tools)
            ]
            
            template = self.env.get_template('tool.html')
            content = template.render(
                tool=tool_data,
                similar_tools=similar_tools,
                metrics=tool_data['metrics'],
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            
            tools_dir = self.output_dir / 'tools'
            tools_dir.mkdir(exist_ok=True)
            (tools_dir / f"{tool_data['id']}.html").write_text(content)
            
            logging.info(f"Successfully generated page for {tool_data.get('name')}")
            
        except Exception as e:
            logging.error(f"Error generating page for tool {tool.get('name', 'unknown')}: {str(e)}")
            logging.error(f"Tool data: {tool}")
            logging.error(f"Traceback:", exc_info=True)
            raise

    def _find_similar_tools(self, tool: dict, all_tools: list, limit: int = 3) -> list:
        """Find similar tools based on category."""
        return [t for t in all_tools 
                if t['category'] == tool['category'] 
                and t['name'] != tool['name']][:limit]

    def _copy_static_assets(self) -> None:
        """Copy static assets to output directory."""
        static_src = self.template_dir / 'static'
        static_dest = self.output_dir / 'static'
        
        if static_src.exists():
            if static_dest.exists():
                shutil.rmtree(static_dest)
            shutil.copytree(static_src, static_dest)
            logging.info("Static assets copied successfully")
        else:
            logging.warning("No static assets directory found")