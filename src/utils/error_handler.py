import logging
from datetime import datetime
from pathlib import Path
import traceback
import json

class ErrorHandler:
    def __init__(self, config):
        self.config = config
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_dir / 'error.log',
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.error_counts = self._load_error_counts()
    
    def handle_error(self, error, component, operation):
        """Handle errors with retry logic and logging"""
        error_key = f"{component}_{operation}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        error_data = {
            'timestamp': str(datetime.now()),
            'component': component,
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'count': self.error_counts[error_key]
        }
        
        # Log the error
        logging.error(f"Error in {component} during {operation}: {str(error)}")
        
        # Save error counts
        self._save_error_counts()
        
        # Determine if operation should be retried
        if self.error_counts[error_key] <= self.config.MAX_RETRIES:
            return 'retry'
        
        return 'abort'
    
    def _load_error_counts(self):
        """Load existing error counts"""
        try:
            with open(self.log_dir / 'error_counts.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_error_counts(self):
        """Save error counts to file"""
        with open(self.log_dir / 'error_counts.json', 'w') as f:
            json.dump(self.error_counts, f, indent=4)
    
    def clear_error_counts(self, age_hours=24):
        """Clear old error counts"""
        current_time = datetime.now()
        cleared_counts = {}
        
        for key, count in self.error_counts.items():
            try:
                error_time = datetime.fromisoformat(key.split('_')[0])
                if (current_time - error_time).total_seconds() < age_hours * 3600:
                    cleared_counts[key] = count
            except:
                continue
        
        self.error_counts = cleared_counts
        self._save_error_counts()
    
    def get_error_summary(self):
        """Get summary of recent errors"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'errors_by_component': self._group_errors_by_component(),
            'most_common_errors': self._get_most_common_errors(5)
        }
    
    def _group_errors_by_component(self):
        """Group errors by component"""
        component_errors = {}
        for key, count in self.error_counts.items():
            component = key.split('_')[0]
            component_errors[component] = component_errors.get(component, 0) + count
        return component_errors
    
    def _get_most_common_errors(self, limit=5):
        """Get most common errors"""
        sorted_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return dict(sorted_errors[:limit])