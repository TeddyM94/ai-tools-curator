from datetime import datetime, timedelta
import json
from pathlib import Path
import random
import logging
from typing import Dict, List, Any
import statistics

class ABTester:
    def __init__(self, config):
        self.config = config
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # Files for storing test data
        self.variants_file = self.data_dir / 'ab_variants.json'
        self.results_file = self.data_dir / 'ab_results.json'
        
        # Load existing data
        self.variants = self._load_variants()
        self.results = self._load_results()
        
        # Test variants
        self.tweet_variants = {
            'emoji_first': {
                'template': "🔥 {name}\n\n{description}\n\nTry it here: {link}",
                'description': "Emoji at start"
            },
            'question_first': {
                'template': "Want to supercharge your {category}?\n\n✨ {name}\n{description}\n\n{link}",
                'description': "Starts with question"
            },
            'features_first': {
                'template': "Top features of {name}:\n\n▫️ {features}\n\n Learn more: {link}",
                'description': "Features highlighted"
            }
        }
        
        # Initialize test tracking
        self.active_tests = {}
        self.confidence_threshold = 0.95  # 95% confidence level
    
    def get_variant(self, test_name: str, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Get A/B test variant for a specific test"""
        if test_name not in self.variants:
            self.variants[test_name] = self._create_test(test_name)
            self._save_variants()
        
        variant = self._select_variant(test_name)
        
        # Track this test instance
        test_id = f"{test_name}_{datetime.now().isoformat()}"
        self.active_tests[test_id] = {
            'test_name': test_name,
            'variant': variant,
            'tool': tool['name'],
            'start_time': datetime.now().isoformat()
        }
        
        return self.tweet_variants[variant]
    
    def record_result(self, test_id: str, metrics: Dict[str, int]) -> None:
        """Record the results of a test"""
        if test_id not in self.active_tests:
            logging.error(f"Test ID {test_id} not found in active tests")
            return
        
        test = self.active_tests[test_id]
        result = {
            'test_name': test['test_name'],
            'variant': test['variant'],
            'tool': test['tool'],
            'start_time': test['start_time'],
            'end_time': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        if test['test_name'] not in self.results:
            self.results[test['test_name']] = []
        
        self.results[test['test_name']].append(result)
        self._save_results()
        
        # Check if we can determine a winner
        self._check_for_winner(test['test_name'])
        
        # Cleanup
        del self.active_tests[test_id]
    
    def get_winning_variant(self, test_name: str) -> str:
        """Get the currently winning variant for a test"""
        if test_name not in self.variants:
            return list(self.tweet_variants.keys())[0]
        
        return self.variants[test_name].get('winner') or self._select_variant(test_name)
    
    def _create_test(self, test_name: str) -> Dict[str, Any]:
        """Create a new A/B test"""
        return {
            'variants': list(self.tweet_variants.keys()),
            'start_date': datetime.now().isoformat(),
            'status': 'active',
            'winner': None,
            'total_samples': 0
        }
    
    def _select_variant(self, test_name: str) -> str:
        """Select a variant for testing"""
        test = self.variants[test_name]
        
        if test['winner']:
            return test['winner']
        
        return random.choice(test['variants'])
    
    def _check_for_winner(self, test_name: str) -> None:
        """Check if we can determine a winning variant"""
        if test_name not in self.results:
            return
        
        results_by_variant = self._group_results_by_variant(test_name)
        
        if self._has_sufficient_data(results_by_variant):
            winner = self._calculate_winner(results_by_variant)
            if winner:
                self.variants[test_name]['winner'] = winner
                self.variants[test_name]['status'] = 'completed'
                self._save_variants()
                logging.info(f"Winner found for {test_name}: {winner}")
    
    def _group_results_by_variant(self, test_name: str) -> Dict[str, List[Dict]]:
        """Group test results by variant"""
        grouped = {}
        for result in self.results[test_name]:
            variant = result['variant']
            if variant not in grouped:
                grouped[variant] = []
            grouped[variant].append(result)
        return grouped
    
    def _has_sufficient_data(self, results_by_variant: Dict[str, List[Dict]]) -> bool:
        """Check if we have enough data to determine a winner"""
        min_samples = 100  # Minimum samples per variant
        return all(len(results) >= min_samples for results in results_by_variant.values())
    
    def _calculate_winner(self, results_by_variant: Dict[str, List[Dict]]) -> str:
        """Calculate the winning variant"""
        engagement_scores = {}
        
        for variant, results in results_by_variant.items():
            metrics = [r['metrics'] for r in results]
            
            # Calculate engagement score (likes + retweets * 2 + replies * 3)
            scores = [
                m['likes'] + (m['retweets'] * 2) + (m['replies'] * 3)
                for m in metrics
            ]
            
            engagement_scores[variant] = {
                'mean': statistics.mean(scores),
                'stdev': statistics.stdev(scores) if len(scores) > 1 else 0,
                'samples': len(scores)
            }
        
        # Find variant with highest mean engagement
        best_variant = max(
            engagement_scores.items(),
            key=lambda x: x[1]['mean']
        )[0]
        
        # Check if it's statistically significant
        if self._is_significant(engagement_scores, best_variant):
            return best_variant
        
        return None
    
    def _is_significant(self, scores: Dict[str, Dict], best_variant: str) -> bool:
        """Check if the difference is statistically significant"""
        # Simplified t-test implementation
        best_score = scores[best_variant]
        
        for variant, score in scores.items():
            if variant == best_variant:
                continue
                
            # Calculate t-statistic
            t_stat = (best_score['mean'] - score['mean']) / (
                (best_score['stdev']**2/best_score['samples'] + 
                 score['stdev']**2/score['samples'])**0.5
            )
            
            # If any comparison is not significant, return False
            if t_stat < 1.96:  # 95% confidence level
                return False
        
        return True
    
    def _load_variants(self) -> Dict:
        """Load A/B test variants from file"""
        try:
            if self.variants_file.exists():
                return json.loads(self.variants_file.read_text())
        except Exception as e:
            logging.error(f"Error loading A/B variants: {e}")
        return {}
    
    def _save_variants(self) -> None:
        """Save A/B test variants to file"""
        try:
            self.variants_file.write_text(json.dumps(self.variants, indent=2))
        except Exception as e:
            logging.error(f"Error saving A/B variants: {e}")
    
    def _load_results(self) -> Dict:
        """Load A/B test results from file"""
        try:
            if self.results_file.exists():
                return json.loads(self.results_file.read_text())
        except Exception as e:
            logging.error(f"Error loading A/B results: {e}")
        return {}
    
    def _save_results(self) -> None:
        """Save A/B test results to file"""
        try:
            self.results_file.write_text(json.dumps(self.results, indent=2))
        except Exception as e:
            logging.error(f"Error saving A/B results: {e}")