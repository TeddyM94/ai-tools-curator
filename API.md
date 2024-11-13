# AI Tools Curator API Documentation

## Core Components API

### ToolsDiscovery
python
find_new_tools() -> List[Dict]
"""
Discovers new AI tools from various sources.
Returns: List of tool dictionaries with properties:
name: str
description: str
url: str
features: List[str]
source: str
discovered_at: str (ISO format)
"""

### QualityScorer
python
score_tool(tool: Dict) -> Dict
"""
Evaluates tool quality.
Returns: Dictionary with:
scores: Dict of individual metrics
overall_score: float
passed_threshold: bool
improvements: List[str]
"""

### TwitterPoster
python
post_tool(tool: Dict) -> str
"""
Posts tool to Twitter.
Returns: Tweet ID if successful, None if failed
Raises: TwitterAPIError if API issues
"""

### AffiliateManager
python
add_affiliate_links(tools: List[Dict]) -> List[Dict]
"""
Adds affiliate links to tools.
Returns: Tools list with affiliate_link added
"""

### AnalyticsTracker
python
track_post(tool: Dict, tweet_id: str, program: str) -> None
"""
Tracks post performance.
Stores: Engagement metrics, affiliate clicks, conversions
"""
get_performance_report() -> Dict
"""
Generates performance report.
Returns: Dictionary with metrics and analysis
"""

### PerformanceOptimizer
python
async optimize_task(task_func, priority: int, args, kwargs)
"""
Optimizes task execution.
Parameters:
task_func: Function to execute
priority: 1 (highest) to 3 (lowest)
Returns: Task result
"""

## Error Handling
ython
handle_error(error: Exception, component: str, operation: str) -> str
"""
Handles system errors.
Returns: 'retry' or 'abort'
"""

## Configuration
python
Required Environment Variables
TWITTER_API_KEY: str
TWITTER_API_SECRET: str
TWITTER_ACCESS_TOKEN: str
TWITTER_ACCESS_TOKEN_SECRET: str
GETRESPONSE_AFFILIATE_ID: str
SYSTEME_AFFILIATE_ID: str
Optional Configuration
MIN_HOURS_BETWEEN_POSTS: int = 6
MAX_RETRIES: int = 3
RETRY_DELAY: int = 60

## Usage Example
python
from src.main import AIToolsCurator
curator = AIToolsCurator()
await curator.run_cycle()
