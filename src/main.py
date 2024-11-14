"""
AI Tools Curator - Main Application
Discovers, evaluates, and publishes AI tools to GitHub with automated updates.

Author: Teddy Mavimbela
Version: 2.0.0
"""

import argparse
import sys
from utils.config import Config
from utils.error_handler import ErrorHandler
from utils.quality_scorer import QualityScorer
from utils.performance_optimizer import PerformanceOptimizer
from tools_discovery.crawler import ToolsDiscovery
from github_publisher.publisher import GitHubPublisher
from analytics.tracker import AnalyticsTracker
import schedule
import time
import logging
from pathlib import Path
import asyncio

class AIToolsCurator:
    def __init__(self):
        # Initialize logging with both file and console handlers
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'curator.log'),
                logging.StreamHandler(sys.stdout)  # Add console output
            ]
        )
        
        print("Initializing AI Tools Curator...")  # Visual feedback
        
        # Initialize components
        self.config = Config()
        self.error_handler = ErrorHandler(self.config)
        self.quality_scorer = QualityScorer(self.config)
        self.performance_optimizer = PerformanceOptimizer(self.config)
        self.tools_discovery = ToolsDiscovery(self.config)
        self.publisher = GitHubPublisher(self.config)
        self.analytics = AnalyticsTracker(self.config)
        
        logging.info("AIToolsCurator initialized successfully")
    
    async def run_cycle(self, mode='discover'):
        """Run one complete cycle with error handling and performance optimization"""
        try:
            print(f"\nStarting {mode} cycle...")  # Visual feedback
            logging.info(f"Starting new {mode} cycle")
            
            if mode == 'discover':
                # 1. Find new AI tools
                print("🔍 Discovering new AI tools...")
                new_tools = await self.performance_optimizer.optimize_task(
                    self.tools_discovery.find_new_tools,
                    priority=1
                )
                
                if not new_tools:
                    print("No new tools found this cycle")
                    return
                
                print(f"Found {len(new_tools)} new tools")
                
                # 2. Score and filter tools
                print("⭐ Evaluating tool quality...")
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
                
                print(f"{len(quality_tools)} tools passed quality threshold")
                
                # 3. Update GitHub repository
                print("📤 Updating repository...")
                await self.performance_optimizer.optimize_task(
                    self.publisher.update_repository,
                    priority=1,
                    new_tools=quality_tools
                )
            
            elif mode == 'generate':
                print("🏗️ Generating static site...")
                await self.publisher.update_repository([])  # Generate site with existing tools
            
            # 4. Track analytics
            analytics_report = await self.performance_optimizer.optimize_task(
                self.analytics.get_performance_report,
                priority=3
            )
            print(f"\n✅ Cycle completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            self.error_handler.handle_error(e, 'main', 'run_cycle')

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Tools Curator')
    parser.add_argument('--mode', choices=['discover', 'generate'], 
                      default='discover', help='Operation mode')
    args = parser.parse_args()
    
    curator = AIToolsCurator()
    await curator.run_cycle(mode=args.mode)

if __name__ == "__main__":
    asyncio.run(main())