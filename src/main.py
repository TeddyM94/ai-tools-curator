"""
AI Tools Curator - Main Application
Discovers, evaluates, and promotes AI tools through Twitter with affiliate marketing integration.

Author: Teddy Mavimbela
Version: 1.0.0
"""

from utils.config import Config
from utils.error_handler import ErrorHandler
from utils.quality_scorer import QualityScorer
from utils.ab_tester import ABTester
from utils.performance_optimizer import PerformanceOptimizer
from tools_discovery.crawler import ToolsDiscovery
from twitter_poster.poster import TwitterPoster
from affiliate_manager.manager import AffiliateManager
from analytics.tracker import AnalyticsTracker
import schedule
import time
import logging
from pathlib import Path
import asyncio

class AIToolsCurator:
    """
    Main curator class that orchestrates the entire system.
    
    Attributes:
        config: Configuration settings
        error_handler: Manages system errors
        quality_scorer: Evaluates tool quality
        ab_tester: Manages A/B testing
        performance_optimizer: Optimizes system performance
        tools_discovery: Finds new AI tools
        twitter: Handles Twitter posting
        affiliate: Manages affiliate links
        analytics: Tracks system performance
    """
    
    def __init__(self):
        # Initialize logging
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / 'curator.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize components
        self.config = Config()
        self.error_handler = ErrorHandler(self.config)
        self.quality_scorer = QualityScorer(self.config)
        self.ab_tester = ABTester(self.config)
        self.performance_optimizer = PerformanceOptimizer(self.config)
        self.tools_discovery = ToolsDiscovery(self.config)
        self.twitter = TwitterPoster(self.config)
        self.affiliate = AffiliateManager()
        self.analytics = AnalyticsTracker(self.config)
        
        logging.info("AIToolsCurator initialized successfully")
    
    async def run_cycle(self):
        """Run one complete cycle with error handling and performance optimization"""
        try:
            logging.info("Starting new discovery cycle")
            
            # 1. Find new AI tools (optimized)
            new_tools = await self.performance_optimizer.optimize_task(
                self.tools_discovery.find_new_tools,
                priority=1
            )
            
            if not new_tools:
                logging.info("No new tools found this cycle")
                return
            
            logging.info(f"Found {len(new_tools)} new tools")
            
            # 2. Score and filter tools (optimized)
            quality_tools = []
            for tool in new_tools:
                score_result = await self.performance_optimizer.optimize_task(
                    self.quality_scorer.score_tool,
                    priority=2,
                    tool=tool
                )
                if score_result['passed_threshold']:
                    tool['quality_score'] = score_result['overall_score']
                    tool['quality_details'] = score_result
                    quality_tools.append(tool)
            
            logging.info(f"{len(quality_tools)} tools passed quality threshold")
            
            # 3. Add affiliate links (optimized)
            tools_with_links = await self.performance_optimizer.optimize_task(
                self.affiliate.add_affiliate_links,
                priority=2,
                tools=quality_tools
            )
            
            # 4. Post to Twitter (optimized)
            for tool in tools_with_links:
                tweet_id = await self.performance_optimizer.optimize_task(
                    self.twitter.post_tool,
                    priority=1,
                    tool=tool
                )
                
                if tweet_id:
                    await self.performance_optimizer.optimize_task(
                        self.analytics.track_post,
                        priority=3,
                        tool=tool,
                        tweet_id=tweet_id,
                        program=self.affiliate._match_affiliate_program(tool)['name']
                    )
                    logging.info(f"Successfully posted tool: {tool['name']}")
                    
                    # Get performance metrics
                    perf_report = self.performance_optimizer.get_performance_report()
                    logging.info(f"Performance metrics: {perf_report}")
                    
                    # Respect rate limits
                    await asyncio.sleep(self.config.MIN_HOURS_BETWEEN_POSTS * 3600)
            
            # 5. Generate reports (optimized)
            analytics_report = await self.performance_optimizer.optimize_task(
                self.analytics.get_performance_report,
                priority=3
            )
            logging.info(f"Cycle completed. Performance: {analytics_report['summary']}")
            
        except Exception as e:
            self.error_handler.handle_error(e, 'main', 'run_cycle')

async def main():
    curator = AIToolsCurator()
    
    # Schedule runs
    for posting_time in curator.config.get_posting_schedule():
        schedule.every().day.at(posting_time.strftime("%H:%M")).do(
            lambda: asyncio.create_task(curator.run_cycle())
        )
    
    logging.info("Scheduler initialized")
    
    # Initial run
    await curator.run_cycle()
    
    # Keep running
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())