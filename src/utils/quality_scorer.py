"""
Quality Scoring System
Evaluates AI tools based on multiple quality criteria.

Metrics:
- Description quality
- Name quality
- URL validity
- Keyword relevance
- Feature completeness
"""

from datetime import datetime
import re
from typing import Dict, Any
import logging

class QualityScorer:
    """
    Evaluates the quality of AI tools using multiple metrics.
    
    Attributes:
        config: Configuration settings
        quality_thresholds: Minimum acceptable scores
        quality_keywords: Keywords indicating tool quality
    
    Methods:
        score_tool: Main method to evaluate a tool
        _score_description: Evaluates description quality
        _score_name: Evaluates tool name
        _score_url: Validates and scores URL
        _score_keyword_relevance: Checks AI relevance
        _score_features: Evaluates feature completeness
    """
    
    def __init__(self, config):
        self.config = config
        self.quality_thresholds = {
            'description_length': 50,  # Minimum characters
            'url_valid': True,
            'min_score': 0.7,  # Minimum overall score to pass
            'keyword_relevance': 0.5  # Minimum keyword relevance score
        }
        
        # Keywords that indicate quality
        self.quality_keywords = {
            'high_value': [
                'ai', 'machine learning', 'neural', 'automation',
                'productivity', 'workflow', 'integration'
            ],
            'features': [
                'api', 'dashboard', 'analytics', 'customizable',
                'scalable', 'secure', 'enterprise'
            ],
            'trust': [
                'trusted', 'verified', 'secure', 'guaranteed',
                'money-back', 'support', 'documentation'
            ]
        }
    
    def score_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive quality score for a tool"""
        scores = {
            'description_quality': self._score_description(tool.get('description', '')),
            'name_quality': self._score_name(tool.get('name', '')),
            'url_quality': self._score_url(tool.get('url', '')),
            'keyword_relevance': self._score_keyword_relevance(tool),
            'feature_completeness': self._score_features(tool)
        }
        
        # Calculate weighted average
        weights = {
            'description_quality': 0.3,
            'name_quality': 0.1,
            'url_quality': 0.15,
            'keyword_relevance': 0.25,
            'feature_completeness': 0.2
        }
        
        overall_score = sum(score * weights[metric] 
                          for metric, score in scores.items())
        
        result = {
            'scores': scores,
            'overall_score': overall_score,
            'passed_threshold': overall_score >= self.quality_thresholds['min_score'],
            'improvements': self._get_improvement_suggestions(scores)
        }
        
        return result
    
    def _score_description(self, description: str) -> float:
        """Score the quality of tool description"""
        if not description:
            return 0.0
        
        scores = []
        
        # Length score
        min_length = self.quality_thresholds['description_length']
        length_score = min(len(description) / min_length, 1.0)
        scores.append(length_score * 0.4)
        
        # Keyword score
        keywords_found = sum(1 for keyword in self._get_all_keywords() 
                           if keyword in description.lower())
        keyword_score = min(keywords_found / 5, 1.0)
        scores.append(keyword_score * 0.3)
        
        # Readability score (simplified)
        words = description.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        readability_score = 1.0 if 4 <= avg_word_length <= 8 else 0.7
        scores.append(readability_score * 0.3)
        
        return sum(scores)
    
    def _score_name(self, name: str) -> float:
        """Score the quality of tool name"""
        if not name:
            return 0.0
        
        scores = []
        
        # Length score
        length_score = 1.0 if 3 <= len(name) <= 30 else 0.5
        scores.append(length_score * 0.4)
        
        # Memorability score (simplified)
        memorable_score = 1.0 if re.match(r'^[a-zA-Z0-9\s]+$', name) else 0.7
        scores.append(memorable_score * 0.3)
        
        # AI relevance score
        ai_terms = ['ai', 'ml', 'bot', 'auto', 'smart', 'intel']
        relevance_score = any(term in name.lower() for term in ai_terms)
        scores.append(float(relevance_score) * 0.3)
        
        return sum(scores)
    
    def _score_url(self, url: str) -> float:
        """Score the quality and validity of URL"""
        if not url:
            return 0.0
        
        scores = []
        
        # HTTPS score
        https_score = 1.0 if url.startswith('https://') else 0.5
        scores.append(https_score * 0.4)
        
        # Domain quality
        domain = url.split('/')[2] if len(url.split('/')) > 2 else ''
        domain_score = 1.0
        if any(tld in domain for tld in ['.io', '.ai', '.com']):
            domain_score = 1.0
        else:
            domain_score = 0.7
        scores.append(domain_score * 0.6)
        
        return sum(scores)
    
    def _score_keyword_relevance(self, tool: Dict[str, Any]) -> float:
        """Score how relevant the tool is to AI/automation"""
        text = f"{tool.get('name', '')} {tool.get('description', '')}".lower()
        
        relevant_keywords = set(self._get_all_keywords())
        found_keywords = sum(1 for keyword in relevant_keywords 
                           if keyword in text)
        
        return min(found_keywords / 5, 1.0)  # Ideal: 5+ relevant keywords
    
    def _score_features(self, tool: Dict[str, Any]) -> float:
        """Score the completeness of tool features"""
        required_fields = ['name', 'description', 'url', 'features']
        optional_fields = ['pricing', 'documentation', 'api_available']
        
        # Required fields score
        required_score = sum(1 for field in required_fields 
                           if tool.get(field)) / len(required_fields)
        
        # Optional fields score
        optional_score = sum(1 for field in optional_fields 
                           if tool.get(field)) / len(optional_fields)
        
        return (required_score * 0.7) + (optional_score * 0.3)
    
    def _get_all_keywords(self) -> list:
        """Get all quality keywords"""
        all_keywords = []
        for category in self.quality_keywords.values():
            all_keywords.extend(category)
        return all_keywords
    
    def _get_improvement_suggestions(self, scores: Dict[str, float]) -> list:
        """Generate improvement suggestions based on scores"""
        suggestions = []
        
        if scores['description_quality'] < 0.7:
            suggestions.append("Improve description length and quality")
        
        if scores['keyword_relevance'] < 0.7:
            suggestions.append("Add more relevant AI/automation keywords")
        
        if scores['feature_completeness'] < 0.7:
            suggestions.append("Add more feature details and documentation")
        
        return suggestions