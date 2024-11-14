"""
Configuration management for AI Tools Curator.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Site settings
        self.site_settings = {
            'site_title': os.getenv('SITE_TITLE', 'AI Tools Curator'),
            'site_description': os.getenv('SITE_DESCRIPTION', 'Discover the best AI tools'),
            'base_url': os.getenv('BASE_URL', 'https://ai-tools-curator.github.io'),
        }
        
        # Discovery settings
        self.discovery_settings = {
            'max_tools_per_source': int(os.getenv('MAX_TOOLS_PER_SOURCE', 10)),
            'min_quality_score': float(os.getenv('MIN_QUALITY_SCORE', 0.6)),
            'use_sample_data': os.getenv('USE_SAMPLE_DATA', 'True').lower() == 'true'
        }
        
        # System settings
        self.system_settings = {
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'data_dir': Path('data'),
            'docs_dir': Path('docs'),
            'templates_dir': Path('templates'),
            'max_retries': int(os.getenv('MAX_RETRIES', 3))  # Added this
        }
        
        # GitHub settings
        self.github_settings = {
            'token': os.getenv('GITHUB_TOKEN'),
            'repo_name': os.getenv('GITHUB_REPO', 'ai-tools-curator'),
            'branch': os.getenv('GITHUB_BRANCH', 'main')
        }
        
        # Add direct access to common settings
        self.MAX_RETRIES = self.system_settings['max_retries']  # Added this

    def get(self, key, default=None):
        """Get configuration value by key."""
        # Check site settings
        if key in self.site_settings:
            return self.site_settings[key]
            
        # Check discovery settings
        if key in self.discovery_settings:
            return self.discovery_settings[key]
            
        # Check system settings
        if key in self.system_settings:
            return self.system_settings[key]
            
        # Check GitHub settings
        if key in self.github_settings:
            return self.github_settings[key]
            
        return default

    def __getitem__(self, key):
        """Allow dictionary-style access to config."""
        return self.get(key)