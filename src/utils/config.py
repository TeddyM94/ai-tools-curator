from dotenv import load_dotenv
import os
from datetime import timedelta

class Config:
    def __init__(self):
        load_dotenv()
        
        # Twitter API Credentials
        self.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
        self.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
        self.TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
        self.TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Affiliate Programs
        self.GETRESPONSE_AFFILIATE_ID = os.getenv('GETRESPONSE_AFFILIATE_ID')
        self.SYSTEME_AFFILIATE_ID = os.getenv('SYSTEME_AFFILIATE_ID')
        
        # Performance Settings
        self.MAX_TOOLS_PER_DAY = 8
        self.MIN_HOURS_BETWEEN_POSTS = 3
        self.MAX_HOURS_BETWEEN_POSTS = 6
        
        # Tool Discovery Settings
        self.MIN_TOOL_QUALITY_SCORE = 0.7
        self.KEYWORD_MATCH_THRESHOLD = 0.6
        self.MAX_DESCRIPTION_LENGTH = 200
        
        # Analytics Settings
        self.TRACKING_ENABLED = True
        self.ANALYTICS_FILE = 'data/analytics.json'
        self.PERFORMANCE_METRICS_INTERVAL = timedelta(hours=24)
        
        # Error Handling
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 60  # seconds
        
    def validate(self):
        """Validate all required credentials are present"""
        required_vars = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET',
            'GETRESPONSE_AFFILIATE_ID',
            'SYSTEME_AFFILIATE_ID'
        ]
        
        missing = [var for var in required_vars if not getattr(self, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
    
    def get_posting_schedule(self):
        """Calculate optimal posting times based on settings"""
        from datetime import datetime, time
        
        # Best times to post (based on engagement data)
        prime_times = [
            time(9, 0),   # 9 AM
            time(12, 0),  # 12 PM
            time(15, 0),  # 3 PM
            time(17, 0),  # 5 PM
            time(20, 0)   # 8 PM
        ]
        
        return prime_times[:self.MAX_TOOLS_PER_DAY]
    
    def get_affiliate_settings(self, program_name):
        """Get specific affiliate program settings"""
        settings = {
            'getresponse': {
                'commission_rate': 0.33,
                'cookie_duration': 120,
                'min_payout': 50,
                'payment_frequency': 'monthly'
            },
            'systeme': {
                'commission_rate': 0.40,
                'cookie_duration': 90,
                'min_payout': 25,
                'payment_frequency': 'monthly'
            }
        }
        
        return settings.get(program_name.lower(), {})