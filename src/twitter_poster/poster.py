"""
Twitter Posting System
Manages tool promotion through Twitter with A/B testing.

Features:
- Automated posting
- Engagement tracking
- A/B testing integration
- Rate limiting
"""

import tweepy
import time
from datetime import datetime
import logging
from pathlib import Path
import json
from utils.ab_tester import ABTester

class TwitterPoster:
    """
    Handles Twitter posting and engagement tracking.
    
    Attributes:
        config: Configuration settings
        api: Twitter API client
        ab_tester: A/B testing integration
        tweet_history: Historical tweet data
    
    Methods:
        post_tool: Main method to post a tool
        _create_tweet: Generates tweet content
        _get_tweet_metrics: Tracks engagement
        _generate_hashtags: Creates relevant hashtags
    """
    
    def __init__(self, config):
        self.config = config
        
        # Initialize Twitter API
        auth = tweepy.OAuthHandler(
            self.config.TWITTER_API_KEY,
            self.config.TWITTER_API_SECRET
        )
        auth.set_access_token(
            self.config.TWITTER_ACCESS_TOKEN,
            self.config.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Initialize A/B testing
        self.ab_tester = ABTester(config)
        
        # Initialize tweet history
        self.history_file = Path('data/tweet_history.json')
        self.history_file.parent.mkdir(exist_ok=True)
        self.tweet_history = self._load_history()
    
    def post_tool(self, tool):
        """
        Post a tool to Twitter with optimal formatting.
        
        Args:
            tool: Dictionary containing tool information
            
        Returns:
            str: Tweet ID if successful, None if failed
        """
        try:
            # Check if tool was recently posted
            if self._was_recently_posted(tool['name']):
                logging.info(f"Skipping {tool['name']}: Recently posted")
                return None
            
            # Create tweet content
            tweet = self._create_tweet(tool)
            
            # Post tweet
            response = self.api.update_status(tweet)
            tweet_id = response.id_str
            
            # Record in history
            self._record_tweet(tool['name'], tweet_id, tweet)
            
            # Wait for engagement metrics
            time.sleep(300)  # Wait 5 minutes for initial engagement
            
            # Get engagement metrics
            tweet_metrics = self._get_tweet_metrics(tweet_id)
            
            # Record A/B test results
            if 'ab_test_id' in tool:
                self.ab_tester.record_result(tool['ab_test_id'], tweet_metrics)
            
            logging.info(f"Successfully posted tweet about {tool['name']}")
            return tweet_id
            
        except Exception as e:
            logging.error(f"Error posting tweet for {tool['name']}: {e}")
            return None
    
    def _create_tweet(self, tool):
        """Create tweet content using A/B testing"""
        # Get test variant
        test_id = f"tweet_format_{datetime.now().isoformat()}"
        variant = self.ab_tester.get_variant('tweet_format', tool)
        
        # Format tweet using variant template
        tweet_data = {
            'name': tool['name'],
            'description': tool.get('description', '')[:100] + '...',
            'link': tool['affiliate_link'],
            'features': ', '.join(tool.get('features', [])[:3]),
            'category': self._get_tool_category(tool)
        }
        
        tweet = variant['template'].format(**tweet_data)
        
        # Add hashtags
        hashtags = self._generate_hashtags(tool)
        tweet = f"{tweet}\n\n{hashtags}"
        
        # Store test ID for later
        tool['ab_test_id'] = test_id
        
        return tweet[:280]  # Twitter character limit
    
    def _get_tool_category(self, tool):
        """Determine tool category"""
        name_and_desc = f"{tool['name']} {tool.get('description', '')}".lower()
        
        if any(word in name_and_desc for word in ['email', 'newsletter', 'marketing']):
            return 'email'
        elif any(word in name_and_desc for word in ['business', 'sales', 'revenue']):
            return 'business'
        else:
            return 'productivity'
    
    def _generate_hashtags(self, tool):
        """Generate relevant hashtags"""
        base_hashtags = ['#AI', '#Tools']
        
        # Add category-specific hashtags
        category_hashtags = {
            'email': ['#EmailMarketing', '#Automation'],
            'business': ['#Business', '#Entrepreneur'],
            'productivity': ['#Productivity', '#Workflow']
        }
        
        tool_category = self._get_tool_category(tool)
        hashtags = base_hashtags + category_hashtags.get(tool_category, [])
        
        return ' '.join(hashtags[:5])  # Limit to 5 hashtags
    
    def _was_recently_posted(self, tool_name):
        """Check if tool was posted in last 7 days"""
        if tool_name in self.tweet_history:
            last_posted = datetime.fromisoformat(self.tweet_history[tool_name]['last_posted'])
            days_since = (datetime.now() - last_posted).days
            return days_since < 7
        return False
    
    def _record_tweet(self, tool_name, tweet_id, content):
        """Record tweet in history"""
        self.tweet_history[tool_name] = {
            'last_posted': datetime.now().isoformat(),
            'tweet_id': tweet_id,
            'content': content
        }
        self._save_history()
    
    def _get_tweet_metrics(self, tweet_id):
        """Get engagement metrics for a tweet"""
        try:
            tweet = self.api.get_status(tweet_id)
            return {
                'likes': tweet.favorite_count,
                'retweets': tweet.retweet_count,
                'replies': len(self.api.get_status_replies(tweet_id))
            }
        except Exception as e:
            logging.error(f"Error getting tweet metrics: {e}")
            return {'likes': 0, 'retweets': 0, 'replies': 0}
    
    def _load_history(self):
        """Load tweet history"""
        try:
            if self.history_file.exists():
                return json.loads(self.history_file.read_text())
        except Exception as e:
            logging.error(f"Error loading tweet history: {e}")
        return {}
    
    def _save_history(self):
        """Save tweet history"""
        try:
            self.history_file.write_text(json.dumps(self.tweet_history, indent=2))
        except Exception as e:
            logging.error(f"Error saving tweet history: {e}")