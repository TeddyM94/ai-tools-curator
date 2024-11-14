"""
Test suite for quality scoring system.
Tests tool evaluation, scoring algorithms, and thresholds.
"""

import pytest
from datetime import datetime
import json

from src.utils.quality_scorer import QualityScorer
from src.utils.config import Config

@pytest.fixture
def config():
    return Config({
        'quality': {
            'weights': {
                'description_quality': 0.3,
                'feature_count': 0.2,
                'url_quality': 0.2,
                'content_uniqueness': 0.3
            },
            'thresholds': {
                'min_score': 0.6,
                'min_description_length': 50,
                'min_features': 2
            }
        }
    })

@pytest.fixture
def scorer(config):
    return QualityScorer(config)

def test_score_description():
    """Test description scoring"""
    scorer = QualityScorer(Config())
    
    descriptions = {
        # High quality descriptions
        "This is a comprehensive AI tool that helps developers automate testing processes with advanced machine learning algorithms and natural language processing.": 0.9,
        
        # Medium quality descriptions
        "An AI tool for testing automation.": 0.5,
        
        # Low quality descriptions
        "AI tool": 0.2,
        "": 0.0
    }
    
    for desc, expected in descriptions.items():
        score = scorer._score_description(desc)
        assert abs(score - expected) <= 0.1

def test_score_features():
    """Test feature scoring"""
    scorer = QualityScorer(Config())
    
    feature_sets = {
        # High quality feature sets
        tuple(['AI Testing', 'Automation', 'Reports', 'API Integration', 'Custom Rules']): 0.9,
        
        # Medium quality feature sets
        tuple(['Testing', 'Reports']): 0.5,
        
        # Low quality feature sets
        tuple(['Test']): 0.2,
        tuple([]): 0.0
    }
    
    for features, expected in feature_sets.items():
        score = scorer._score_features(list(features))
        assert abs(score - expected) <= 0.1

def test_score_url():
    """Test URL scoring"""
    scorer = QualityScorer(Config())
    
    urls = {
        # High quality URLs
        "https://enterprise-ai-tool.com": 0.9,
        "https://ai-platform.io": 0.8,
        
        # Medium quality URLs
        "https://my-ai-tool.netlify.app": 0.6,
        
        # Low quality URLs
        "https://free-ai-tools.blogspot.com": 0.3,
        "": 0.0
    }
    
    for url, expected in urls.items():
        score = scorer._score_url(url)
        assert abs(score - expected) <= 0.1

def test_check_uniqueness():
    """Test content uniqueness checking"""
    scorer = QualityScorer(Config())
    
    # Setup test cases
    existing_tools = {
        "Tool1": {
            "description": "A unique AI testing tool",
            "features": ["Test", "Automate"]
        },
        "Tool2": {
            "description": "Another different AI tool",
            "features": ["Report", "Analyze"]
        }
    }
    
    test_cases = [
        # Unique tool (high score)
        {
            "description": "A completely new kind of AI tool",
            "features": ["Novel", "Innovative"]
        },
        
        # Similar tool (medium score)
        {
            "description": "An AI testing tool with unique features",
            "features": ["Test", "Novel"]
        },
        
        # Very similar tool (low score)
        {
            "description": "A unique AI testing tool",
            "features": ["Test", "Automate"]
        }
    ]
    
    expected_scores = [0.9, 0.6, 0.3]
    
    for tool, expected in zip(test_cases, expected_scores):
        score = scorer._check_uniqueness(tool, existing_tools)
        assert abs(score - expected) <= 0.1

def test_score_tool():
    """Test overall tool scoring"""
    scorer = QualityScorer(Config())
    
    test_tools = [
        # High quality tool
        {
            "name": "Enterprise AI Testing",
            "description": "A comprehensive AI-powered testing automation platform with advanced features and enterprise-grade security.",
            "url": "https://enterprise-ai-testing.com",
            "features": ["AI Testing", "Automation", "Reports", "API", "Security"]
        },
        
        # Medium quality tool
        {
            "name": "Simple AI Tester",
            "description": "Basic AI testing tool.",
            "url": "https://simple-ai-test.netlify.app",
            "features": ["Test", "Report"]
        },
        
        # Low quality tool
        {
            "name": "Test",
            "description": "AI tool",
            "url": "https://test.blogspot.com",
            "features": ["Test"]
        }
    ]
    
    expected_results = [
        {"passed_threshold": True, "overall_score": 0.85},
        {"passed_threshold": False, "overall_score": 0.5},
        {"passed_threshold": False, "overall_score": 0.2}
    ]
    
    for tool, expected in zip(test_tools, expected_results):
        result = scorer.score_tool(tool)
        assert result["passed_threshold"] == expected["passed_threshold"]
        assert abs(result["overall_score"] - expected["overall_score"]) <= 0.1

def test_threshold_handling():
    """Test threshold configuration and handling"""
    config = Config({
        'quality': {
            'thresholds': {
                'min_score': 0.8,  # High threshold
                'min_description_length': 100,
                'min_features': 4
            }
        }
    })
    scorer = QualityScorer(config)
    
    # Test with a good but not excellent tool
    tool = {
        "name": "Good AI Tool",
        "description": "A very good AI testing tool with some nice features.",
        "url": "https://good-ai-tool.com",
        "features": ["Test", "Report", "Analyze"]
    }
    
    result = scorer.score_tool(tool)
    assert not result["passed_threshold"]  # Should fail due to high threshold

def test_weight_configuration():
    """Test weight configuration impact"""
    config = Config({
        'quality': {
            'weights': {
                'description_quality': 0.5,  # Heavy weight on description
                'feature_count': 0.1,
                'url_quality': 0.1,
                'content_uniqueness': 0.3
            }
        }
    })
    scorer = QualityScorer(config)
    
    # Test with tool having excellent description but mediocre other attributes
    tool = {
        "name": "Description Heavy Tool",
        "description": "An extremely comprehensive and well-written description of an advanced AI-powered testing automation platform with detailed explanations of all capabilities.",
        "url": "https://tool.netlify.app",
        "features": ["Test"]
    }
    
    result = scorer.score_tool(tool)
    assert result["overall_score"] > 0.6  # Should score well due to description weight