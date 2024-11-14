"""
Test suite for GitHub publishing system.
Tests content generation, GitHub updates, and site deployment.
"""

import pytest
from pathlib import Path
import json
import shutil
from datetime import datetime
import os
from unittest.mock import Mock, patch

from src.github_publisher.publisher import GitHubPublisher
from src.github_publisher.static_generator import StaticGenerator
from src.utils.config import Config

@pytest.fixture
def config():
    return Config({
        'github': {
            'repository': 'test/ai-tools',
            'branch': 'main',
            'commit_message': 'Update AI tools data',
            'author': {
                'name': 'Test Bot',
                'email': 'test@example.com'
            }
        },
        'site': {
            'title': 'AI Tools Discovery',
            'description': 'Discover the latest AI tools',
            'url': 'https://test.github.io/ai-tools'
        }
    })

@pytest.fixture
def publisher(config, tmp_path):
    pub = GitHubPublisher(config)
    pub.data_dir = tmp_path / 'data'
    pub.content_dir = tmp_path / 'content'
    pub.data_dir.mkdir()
    pub.content_dir.mkdir()
    return pub

@pytest.fixture
def sample_tools():
    return {
        'tool-1': {
            'name': 'Test Tool 1',
            'description': 'A test AI tool',
            'url': 'https://test1.com',
            'category': 'Testing',
            'features': ['Feature 1', 'Feature 2'],
            'added_date': datetime.now().isoformat(),
            'quality_score': 0.85
        },
        'tool-2': {
            'name': 'Test Tool 2',
            'description': 'Another test AI tool',
            'url': 'https://test2.com',
            'category': 'Development',
            'features': ['Feature 3', 'Feature 4'],
            'added_date': datetime.now().isoformat(),
            'quality_score': 0.92
        }
    }

def test_update_tools_data(publisher, sample_tools):
    """Test updating tools data"""
    new_tools = [{
        'name': 'New Tool',
        'description': 'A new AI tool',
        'url': 'https://new-tool.com',
        'category': 'Testing',
        'features': ['Feature 5', 'Feature 6']
    }]
    
    publisher._update_tools_data(new_tools)
    
    # Verify data was saved
    tools_file = publisher.data_dir / 'tools.json'
    assert tools_file.exists()
    
    saved_data = json.loads(tools_file.read_text())
    assert 'new-tool' in saved_data
    assert saved_data['new-tool']['name'] == 'New Tool'

def test_generate_readme(publisher, sample_tools):
    """Test README generation"""
    publisher.tools_data = sample_tools
    publisher._update_readme()
    
    readme_file = publisher.content_dir / 'README.md'
    assert readme_file.exists()
    
    content = readme_file.read_text()
    assert 'AI Tools Discovery' in content
    assert 'Test Tool 1' in content
    assert 'Test Tool 2' in content

@pytest.mark.asyncio
async def test_update_repository(publisher, sample_tools):
    """Test repository update process"""
    with patch('src.github_publisher.publisher.GitHubPublisher._push_to_github') as mock_push:
        await publisher.update_repository([{
            'name': 'New Tool',
            'description': 'A new AI tool',
            'url': 'https://new-tool.com',
            'category': 'Testing',
            'features': ['Feature 5', 'Feature 6']
        }])
        
        assert mock_push.called

def test_static_site_generation(publisher, sample_tools, tmp_path):
    """Test static site generation"""
    publisher.tools_data = sample_tools
    
    # Setup templates
    templates_dir = tmp_path / 'templates'
    templates_dir.mkdir()
    (templates_dir / 'base.html').write_text('<html>{{ content }}</html>')
    (templates_dir / 'index.html').write_text('{% extends "base.html" %}{% block content %}{{ tools }}{% endblock %}')
    
    generator = StaticGenerator(publisher.config)
    generator.template_dir = templates_dir
    generator.output_dir = tmp_path / 'docs'
    
    generator.generate_site(sample_tools)
    
    # Verify generated files
    assert (generator.output_dir / 'index.html').exists()
    assert (generator.output_dir / 'tools').exists()

def test_weekly_digest_generation(publisher, sample_tools):
    """Test weekly digest generation"""
    publisher.tools_data = sample_tools
    digest = publisher._create_weekly_digest()
    
    assert digest['week_number'] > 0
    assert digest['year'] == datetime.now().year
    assert len(digest['new_tools']) > 0
    assert len(digest['trending_tools']) > 0

def test_error_handling(publisher):
    """Test error handling during publishing"""
    with pytest.raises(Exception):
        publisher._push_to_github()  # Should raise without proper git setup

def test_data_validation(publisher):
    """Test data validation during updates"""
    invalid_tools = [{
        'name': 'Invalid Tool',
        # Missing required fields
    }]
    
    with pytest.raises(ValueError):
        publisher._update_tools_data(invalid_tools)

def test_category_organization(publisher, sample_tools):
    """Test category-based organization"""
    publisher.tools_data = sample_tools
    categories = publisher._get_categories()
    
    assert 'Testing' in categories
    assert 'Development' in categories

def test_metrics_tracking(publisher, sample_tools):
    """Test metrics tracking during updates"""
    publisher.tools_data = sample_tools
    metrics = publisher._generate_metrics()
    
    assert metrics['total_tools'] == len(sample_tools)
    assert metrics['categories'] == len(publisher._get_categories())
    assert 'last_updated' in metrics

@pytest.mark.asyncio
async def test_concurrent_updates(publisher):
    """Test handling of concurrent updates"""
    update_tasks = []
    for _ in range(3):
        update_tasks.append(publisher.update_repository([{
            'name': f'Concurrent Tool {_}',
            'description': 'A test tool',
            'url': f'https://test{_}.com',
            'category': 'Testing',
            'features': ['Feature']
        }]))
    
    await asyncio.gather(*update_tasks)
    
    # Verify data integrity
    tools_file = publisher.data_dir / 'tools.json'
    assert tools_file.exists()
    data = json.loads(tools_file.read_text())
    assert len(data) == 3

def test_cleanup_old_data(publisher, sample_tools):
    """Test cleanup of old data"""
    publisher.tools_data = sample_tools
    publisher._cleanup_old_data(days=30)
    
    # Verify old data was removed
    tools_file = publisher.data_dir / 'tools.json'
    data = json.loads(tools_file.read_text())
    assert all(
        datetime.fromisoformat(tool['added_date']).date() > (datetime.now().date() - timedelta(days=30))
        for tool in data.values()
    )