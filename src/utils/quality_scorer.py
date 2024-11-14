"""
Quality scoring module for evaluating AI tools.
"""

import logging
from typing import Dict, Any
from datetime import datetime

class QualityScorer:
    def __init__(self, config):
        self.config = config
        self.min_score = 0.6
        self.weights = {
            'description_quality': 0.3,
            'features_quality': 0.3,
            'url_quality': 0.2,
            'metadata_quality': 0.2
        }

    async def score_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Score a tool based on various quality metrics."""
        try:
            scores = {
                'description_quality': self._score_description(tool.get('description', '')),
                'features_quality': self._score_features(tool.get('features', [])),
                'url_quality': self._score_url(tool.get('url', '')),
                'metadata_quality': self._score_metadata(tool)
            }

            # Calculate overall score
            overall_score = sum(
                scores[key] * self.weights[key] 
                for key in scores
            )

            result = {
                'overall_score': round(overall_score, 2),
                'scores': scores,
                'passed_threshold': overall_score >= self.min_score,
                'evaluated_at': datetime.utcnow().isoformat()
            }

            if result['passed_threshold']:
                logging.info(f"Tool '{tool['name']}' passed quality check with score {result['overall_score']}")
                print(f"✅ {tool['name']}: Quality Score {result['overall_score']}")
            else:
                logging.info(f"Tool '{tool['name']}' failed quality check with score {result['overall_score']}")
                print(f"❌ {tool['name']}: Quality Score {result['overall_score']}")

            return result

        except Exception as e:
            logging.error(f"Error scoring tool {tool.get('name', 'unknown')}: {str(e)}")
            return {
                'overall_score': 0,
                'scores': {},
                'passed_threshold': False,
                'error': str(e)
            }

    def _score_description(self, description: str) -> float:
        """Score the quality of the tool description."""
        if not description:
            return 0.0
        
        score = 0.0
        # Length check
        if len(description) >= 50:
            score += 0.5
        if len(description) >= 100:
            score += 0.3
        # Basic content checks
        if '.' in description:  # Complete sentences
            score += 0.2
        
        return min(1.0, score)

    def _score_features(self, features: list) -> float:
        """Score the quality of tool features."""
        if not features:
            return 0.0
        
        score = 0.0
        # Number of features
        score += min(len(features) * 0.2, 0.6)
        # Feature description quality
        if any(len(f) > 10 for f in features):
            score += 0.4
            
        return min(1.0, score)

    def _score_url(self, url: str) -> float:
        """Score the quality of the tool URL."""
        if not url:
            return 0.0
            
        score = 0.0
        # HTTPS check
        if url.startswith('https://'):
            score += 0.5
        # Domain quality
        if any(domain in url.lower() for domain in ['.com', '.io', '.ai', '.org']):
            score += 0.5
            
        return min(1.0, score)

    def _score_metadata(self, tool: Dict[str, Any]) -> float:
        """Score the quality of tool metadata."""
        score = 0.0
        
        # Category check
        if tool.get('category'):
            score += 0.3
        # Pricing information
        if tool.get('pricing'):
            score += 0.3
        # Additional metadata
        if tool.get('added_date'):
            score += 0.2
        if tool.get('last_updated'):
            score += 0.2
            
        return min(1.0, score)