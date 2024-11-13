"""
Performance Optimization System
Manages system resources and optimizes task execution.

Features:
- Resource monitoring
- Task prioritization
- Concurrent execution
- Performance metrics
"""

import psutil
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import time
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetrics:
    """Data class for storing performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    response_time: float
    requests_per_minute: int
    errors_count: int
    timestamp: str

class PerformanceOptimizer:
    """
    Optimizes system performance and resource usage.
    
    Attributes:
        config: Configuration settings
        thresholds: Resource usage limits
        task_queue: Priority queue for tasks
        thread_pool: Thread pool for concurrent execution
        metrics_history: Historical performance data
    
    Methods:
        optimize_task: Main method to optimize task execution
        _check_resources: Monitors system resources
        _wait_for_resources: Handles resource availability
        get_performance_report: Generates performance metrics
    """
    
    def __init__(self, config):
        self.config = config
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # Performance logs
        self.metrics_file = self.data_dir / 'performance_metrics.json'
        self.metrics_history = self._load_metrics_history()
        
        # Resource thresholds
        self.thresholds = {
            'cpu_max': 80.0,  # Maximum CPU usage percentage
            'memory_max': 75.0,  # Maximum memory usage percentage
            'requests_per_minute': 30,  # Rate limiting
            'max_concurrent_tasks': 3,  # Maximum concurrent operations
            'response_time_max': 5.0  # Maximum response time in seconds
        }
        
        # Initialize queues and pools
        self.task_queue = queue.PriorityQueue()
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.thresholds['max_concurrent_tasks']
        )
        
        # Performance monitoring
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
        # Initialize async event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    async def optimize_task(self, task_func, priority: int = 1, *args, **kwargs):
        """
        Optimize and execute a task with resource management.
        
        Args:
            task_func: Function to execute
            priority: Task priority (1=highest, 3=lowest)
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func
            
        Returns:
            Task execution result
        """
        try:
            # Check resource availability
            if not self._check_resources():
                await self._wait_for_resources()
            
            # Add task to queue
            task_id = f"task_{datetime.now().isoformat()}"
            self.task_queue.put((priority, task_id, task_func, args, kwargs))
            
            # Execute task with monitoring
            start_time = time.time()
            
            # Run in thread pool if CPU intensive
            if self._is_cpu_intensive(task_func):
                result = await self.loop.run_in_executor(
                    self.thread_pool,
                    task_func,
                    *args,
                    **kwargs
                )
            else:
                result = await self._execute_task(task_func, *args, **kwargs)
            
            # Record metrics
            response_time = time.time() - start_time
            self._record_metrics(response_time)
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logging.error(f"Task execution error: {e}")
            raise
    
    async def _execute_task(self, task_func, *args, **kwargs):
        """Execute a task with monitoring"""
        self.request_count += 1
        
        if asyncio.iscoroutinefunction(task_func):
            return await task_func(*args, **kwargs)
        else:
            return task_func(*args, **kwargs)
    
    def _check_resources(self) -> bool:
        """Check if system resources are available"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        return (
            cpu_usage < self.thresholds['cpu_max'] and
            memory_usage < self.thresholds['memory_max'] and
            self._get_current_rpm() < self.thresholds['requests_per_minute']
        )
    
    async def _wait_for_resources(self):
        """Wait for resources to become available"""
        while not self._check_resources():
            await asyncio.sleep(1)
    
    def _get_current_rpm(self) -> int:
        """Calculate current requests per minute"""
        time_running = (datetime.now() - self.start_time).total_seconds() / 60
        return int(self.request_count / time_running if time_running > 0 else 0)
    
    def _is_cpu_intensive(self, func) -> bool:
        """Determine if a function is CPU intensive"""
        cpu_intensive_operations = [
            'scrape_source',
            'process_tools',
            'analyze_tool',
            'generate_report'
        ]
        return any(op in func.__name__ for op in cpu_intensive_operations)
    
    def _record_metrics(self, response_time: float):
        """Record performance metrics"""
        metrics = PerformanceMetrics(
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            response_time=response_time,
            requests_per_minute=self._get_current_rpm(),
            errors_count=self.error_count,
            timestamp=datetime.now().isoformat()
        )
        
        self.metrics_history.append(asdict(metrics))
        self._save_metrics()
        
        # Log if thresholds are exceeded
        self._check_thresholds(metrics)
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if any metrics exceed thresholds"""
        if metrics.cpu_usage > self.thresholds['cpu_max']:
            logging.warning(f"High CPU usage: {metrics.cpu_usage}%")
        
        if metrics.memory_usage > self.thresholds['memory_max']:
            logging.warning(f"High memory usage: {metrics.memory_usage}%")
        
        if metrics.response_time > self.thresholds['response_time_max']:
            logging.warning(f"Slow response time: {metrics.response_time}s")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 records
        
        return {
            'average_response_time': sum(m['response_time'] for m in recent_metrics) / len(recent_metrics),
            'average_cpu_usage': sum(m['cpu_usage'] for m in recent_metrics) / len(recent_metrics),
            'average_memory_usage': sum(m['memory_usage'] for m in recent_metrics) / len(recent_metrics),
            'total_requests': self.request_count,
            'error_rate': (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    def _load_metrics_history(self) -> list:
        """Load metrics history from file"""
        try:
            if self.metrics_file.exists():
                return json.loads(self.metrics_file.read_text())
        except Exception as e:
            logging.error(f"Error loading metrics history: {e}")
        return []
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            self.metrics_file.write_text(json.dumps(self.metrics_history, indent=2))
        except Exception as e:
            logging.error(f"Error saving metrics: {e}")