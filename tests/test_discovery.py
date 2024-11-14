"""
Test suite for tools discovery system.
Tests web scraping, data extraction, and validation.
"""

import pytest
from pathlib import Path
import json
from bs4 import BeautifulSoup
import responses
from datetime import datetime

from src.tools_discovery.crawler import ToolsDiscovery
from src.utils.config import Config

# Test data
MOCK_HTML = """
<div class="tool-listing">
    <h3>Test AI Tool</h3>
    <p>An amazing AI tool for testing</p>
    <div class="features">
        <span>Feature 1</span>
        <span>Feature 2</span>
    </div>
    <a href="https://test-ai-tool.com">Visit</a>
</div>
"""

@pytest.fixture
def config():
    return Config({
        'discovery': {
            'sources': {
                'test_source': {
                    'url': 'https://test-source.com',
                    'selector': 'div.tool-listing',
                    'name_selector': 'h3',
                    'description_selector': 'p',
                    'link_selector': 'a'
                }
            },
            'max_tools_per_source': 10,
            'min_description_length': 20
        }
    })

@pytest.fixture
def discovery(config):
    return ToolsDiscovery(config)

@responses.activate
def test_find_new_tools(discovery):
    """Test tool discovery from mock webpage"""
    # Setup mock response
    responses.add(
        responses.GET,
        'https://test-source.com',
        body=MOCK_HTML,
        status=200
    )
    
    # Run discovery
    tools = discovery.find_new_tools()
    
    # Verify results
    assert len(tools) == 1
    tool = tools[0]
    assert tool['name'] == 'Test AI Tool'
    assert tool['description'] == 'An amazing AI tool for testing'
    assert tool['url'] == 'https://test-ai-tool.com'
    assert len(tool['features']) == 2

def test_clean_text(discovery):
    """Test text cleaning functionality"""
    dirty_text = "  Test   Text\nWith\tSpaces  "
    clean = discovery._clean_text(dirty_text)
    assert clean == "Test Text With Spaces"

def test_clean_url(discovery):
    """Test URL cleaning functionality"""
    urls = {
        'test.com': 'https://test.com',
        'https://test.com': 'https://test.com',
        'http://test.com': 'http://test.com',
        '  test.com  ': 'https://test.com'
    }
    
    for input_url, expected in urls.items():
        assert discovery._clean_url(input_url) == expected

def test_is_valid_url(discovery):
    """Test URL validation"""
    valid_urls = [
        'https://test.com',
        'http://test.com',
        'https://sub.test.com/path',
        'http://localhost:8000'
    ]
    
    invalid_urls = [
        'not-a-url',
        'ftp://test.com',
        'test',
        'http://'
    ]
    
    for url in valid_urls:
        assert discovery._is_valid_url(url)
    
    for url in invalid_urls:
        assert not discovery._is_valid_url(url)

def test_record_tool(discovery, tmp_path):
    """Test tool recording functionality"""
    # Setup temporary data directory
    discovery.data_dir = tmp_path
    discovery.discovered_file = tmp_path / 'discovered_tools.json'
    
    tool = {
        'name': 'Test Tool',
        'url': 'https://test.com',
        'discovered_at': datetime.now().isoformat()
    }
    
    # Record tool
    discovery._record_tool(tool)
    
    # Verify recorded data
    assert discovery.discovered_file.exists()
    data = json.loads(discovery.discovered_file.read_text())
    assert 'Test Tool' in data
    assert data['Test Tool']['url'] == 'https://test.com'

def test_load_discovered_tools(discovery, tmp_path):
    """Test loading discovered tools"""
    # Setup test data
    discovery.data_dir = tmp_path
    discovery.discovered_file = tmp_path / 'discovered_tools.json'
    
    test_data = {
        'Test Tool': {
            'url': 'https://test.com',
            'discovered_at': datetime.now().isoformat()
        }
    }
    
    discovery.discovered_file.write_text(json.dumps(test_data))
    
    # Load data
    loaded_data = discovery._load_discovered_tools()
    
    # Verify loaded data
    assert loaded_data == test_data

@pytest.mark.asyncio
async def test_async_discovery(discovery):
    """Test asynchronous tool discovery"""
    # Setup mock response
    responses.add(
        responses.GET,
        'https://test-source.com',
        body=MOCK_HTML,
        status=200
    )
    
    # Run async discovery
    tools = await discovery.async_find_new_tools()
    
    # Verify results
    assert isinstance(tools, list)
    assert all('name' in tool for tool in tools)
    assert all('url' in tool for tool in tools)
    assert all('description' in tool for tool in tools)

def test_discovery_rate_limiting(discovery):
    """Test rate limiting functionality"""
    start_time = datetime.now()
    
    # Make multiple requests
    for _ in range(3):
        responses.add(
            responses.GET,
            'https://test-source.com',
            body=MOCK_HTML,
            status=200
        )
        discovery.find_new_tools()
    
    # Verify minimum time elapsed
    elapsed = (datetime.now() - start_time).total_seconds()
    assert elapsed >= 2  # Assuming 1 second delay between requests