"""
Analytics Tracking System
Monitors and analyzes system performance and engagement.

Metrics:
- Post engagement
- Affiliate conversions
- System performance
- Quality scores
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Any
import statistics

class AnalyticsTracker:
    """
    Tracks and analyzes system performance.
    
    Attributes:
        config: Configuration settings
        metrics_history: Historical performance data
        engagement_metrics: Post engagement data
        conversion_data: Affiliate conversion tracking
    
    Methods:
        track_post: Records post performance
        track_conversion: Tracks affiliate conversions
        get_performance_report: Generates analytics report
        _calculate_metrics: Processes raw metrics
    """
    
    def __init__(self, config):
        self.config = config
        self.data_dir = Path('data/analytics')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data files
        self.posts_file = self.data_dir / 'posts.json'
        self.conversions_file = self.data_dir / 'conversions.json'
        self.metrics_file = self.data_dir / 'metrics.json'
        
        # Load existing data
        self.posts = self._load_json(self.posts_file)
        self.conversions = self._load_json(self.conversions_file)
        self.metrics = self._load_json(self.metrics_file)
        
        # Performance tracking
        self.start_time = datetime.now()
    
    def track_post(self, tool: Dict[str, Any], tweet_id: str, program: str) -> None:
        """
        Track a new post and its initial metrics.
        
        Args:
            tool: Tool information
            tweet_id: Twitter post ID
            program: Affiliate program name
        """
        post_data = {
            'tool_name': tool['name'],
            'tweet_id': tweet_id,
            'affiliate_program': program,
            'quality_score': tool.get('quality_score', 0),
            'posted_at': datetime.now().isoformat(),
            'initial_metrics': {
                'likes': 0,
                'retweets': 0,
                'replies': 0,
                'clicks': 0
            }
        }
        
        self.posts[tweet_id] = post_data
        self._save_json(self.posts_file, self.posts)
        logging.info(f"Tracked new post for {tool['name']}")
    
    def track_conversion(self, tweet_id: str, amount: float) -> None:
        """
        Track an affiliate conversion.
        
        Args:
            tweet_id: Associated Twitter post ID
            amount: Conversion amount
        """
        if tweet_id not in self.posts:
            logging.error(f"Unknown tweet_id for conversion: {tweet_id}")
            return
        
        conversion_data = {
            'tweet_id': tweet_id,
            'tool_name': self.posts[tweet_id]['tool_name'],
            'program': self.posts[tweet_id]['affiliate_program'],
            'amount': amount,
            'converted_at': datetime.now().isoformat()
        }
        
        self.conversions[f"conv_{datetime.now().isoformat()}"] = conversion_data
        self._save_json(self.conversions_file, self.conversions)
        logging.info(f"Tracked conversion for {conversion_data['tool_name']}")
    
    def update_metrics(self, tweet_id: str, metrics: Dict[str, int]) -> None:
        """
        Update engagement metrics for a post.
        
        Args:
            tweet_id: Twitter post ID
            metrics: Updated metrics dictionary
        """
        if tweet_id in self.posts:
            self.posts[tweet_id]['metrics'] = metrics
            self.posts[tweet_id]['last_updated'] = datetime.now().isoformat()
            self._save_json(self.posts_file, self.posts)
    
    def get_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent data
        recent_posts = {
            k: v for k, v in self.posts.items()
            if datetime.fromisoformat(v['posted_at']) > cutoff_date
        }
        
        recent_conversions = {
            k: v for k, v in self.conversions.items()
            if datetime.fromisoformat(v['converted_at']) > cutoff_date
        }
        
        # Calculate metrics
        engagement_stats = self._calculate_engagement_stats(recent_posts)
        conversion_stats = self._calculate_conversion_stats(recent_conversions)
        quality_stats = self._calculate_quality_stats(recent_posts)
        
        return {
            'summary': {
                'total_posts': len(recent_posts),
                'total_conversions': len(recent_conversions),
                'conversion_rate': conversion_stats['conversion_rate'],
                'average_engagement': engagement_stats['average_engagement'],
                'revenue': conversion_stats['total_revenue']
            },
            'engagement': engagement_stats,
            'conversions': conversion_stats,
            'quality': quality_stats,
            'period': f"Last {days} days",
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_engagement_stats(self, posts: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate engagement statistics"""
        if not posts:
            return {'average_engagement': 0, 'engagement_rate': 0}
        
        engagements = []
        for post in posts.values():
            metrics = post.get('metrics', {})
            engagement = (
                metrics.get('likes', 0) +
                metrics.get('retweets', 0) * 2 +
                metrics.get('replies', 0) * 3
            )
            engagements.append(engagement)
        
        return {
            'average_engagement': statistics.mean(engagements),
            'engagement_rate': statistics.mean(engagements) / len(posts),
            'best_time': self._find_best_posting_time(posts)
        }
    
    def _calculate_conversion_stats(self, conversions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate conversion statistics"""
        if not conversions:
            return {'conversion_rate': 0, 'total_revenue': 0}
        
        total_revenue = sum(conv['amount'] for conv in conversions.values())
        
        return {
            'conversion_rate': len(conversions) / len(self.posts) if self.posts else 0,
            'total_revenue': total_revenue,
            'average_conversion': total_revenue / len(conversions)
        }
    
    def _calculate_quality_stats(self, posts: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality score statistics"""
        if not posts:
            return {'average_quality': 0}
        
        quality_scores = [post.get('quality_score', 0) for post in posts.values()]
        
        return {
            'average_quality': statistics.mean(quality_scores),
            'quality_trend': self._calculate_trend(quality_scores)
        }
    
    def _find_best_posting_time(self, posts: Dict[str, Any]) -> str:
        """Find the most engaging posting time"""
        time_engagements = {}
        
        for post in posts.values():
            posted_at = datetime.fromisoformat(post['posted_at'])
            hour = posted_at.hour
            
            metrics = post.get('metrics', {})
            engagement = (
                metrics.get('likes', 0) +
                metrics.get('retweets', 0) * 2 +
                metrics.get('replies', 0) * 3
            )
            
            if hour not in time_engagements:
                time_engagements[hour] = []
            time_engagements[hour].append(engagement)
        
        if not time_engagements:
            return "No data"
        
        best_hour = max(
            time_engagements.items(),
            key=lambda x: statistics.mean(x[1])
        )[0]
        
        return f"{best_hour:02d}:00"
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "neutral"
        
        avg_first_half = statistics.mean(values[:len(values)//2])
        avg_second_half = statistics.mean(values[len(values)//2:])
        
        if avg_second_half > avg_first_half * 1.05:
            return "increasing"
        elif avg_second_half < avg_first_half * 0.95:
            return "decreasing"
        return "stable"
    
    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON data from file"""
        try:
            if file_path.exists():
                return json.loads(file_path.read_text())
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
        return {}
    
    def _save_json(self, file_path: Path, data: Dict) -> None:
        """Save data to JSON file"""
        try:
            file_path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logging.error(f"Error saving to {file_path}: {e}")