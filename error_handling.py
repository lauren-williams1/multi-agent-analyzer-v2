# error_handling.py
import time
from typing import Callable, Any, Optional
from datetime import datetime
import json

class RetryHandler:
    """Handles retries with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def execute_with_retry(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> tuple[bool, Any, list]:
        """
        Execute function with retry logic
        
        Returns:
            (success, result, error_log)
        """
        error_log = []
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return True, result, error_log
            
            except Exception as e:
                error_info = {
                    "attempt": attempt + 1,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                error_log.append(error_info)
                
                # If last attempt, don't wait
                if attempt == self.max_retries - 1:
                    return False, None, error_log
                
                # Exponential backoff
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)
        
        return False, None, error_log


class FailureHandler:
    """Handles failures and provides fallbacks"""
    
    @staticmethod
    def get_fallback_response(agent_name: str, error: str) -> dict:
        """
        Provide fallback response when agent fails
        """
        fallback_messages = {
            "Data Collector": "Unable to collect data at this time. Please try a more specific query or check back later.",
            "Analysis Agent": "Analysis temporarily unavailable. The system encountered an error during data analysis.",
            "Insights Agent": "Unable to generate insights at this time. Please review the data collection and analysis outputs manually."
        }
        
        return {
            "agent": agent_name,
            "output": fallback_messages.get(agent_name, "Agent temporarily unavailable"),
            "status": "fallback",
            "error": error,
            "requires_human_review": True
        }
    
    @staticmethod
    def should_trigger_human_review(
        confidence_score: float,
        error_count: int,
        warnings: list
    ) -> tuple[bool, str]:
        """
        Determine if human review is needed
        
        Returns:
            (needs_review, reason)
        """
        # Low confidence
        if confidence_score < 0.5:
            return True, f"Low confidence score: {confidence_score:.2f}"
        
        # Multiple errors
        if error_count > 1:
            return True, f"Multiple errors encountered: {error_count}"
        
        # Safety warnings
        if warnings:
            return True, f"Safety warnings: {', '.join(warnings)}"
        
        return False, ""


class ExecutionLogger:
    """Logs all execution details for debugging and auditing"""
    
    def __init__(self):
        self.logs = []
    
    def log_event(
        self,
        event_type: str,
        agent_name: str,
        details: dict,
        success: bool = True
    ):
        """Log an execution event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent": agent_name,
            "success": success,
            "details": details
        }
        self.logs.append(log_entry)
    
    def get_execution_summary(self) -> dict:
        """Get summary of execution"""
        total_events = len(self.logs)
        successful = sum(1 for log in self.logs if log["success"])
        failed = total_events - successful
        
        return {
            "total_events": total_events,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total_events*100):.1f}%" if total_events > 0 else "0%",
            "logs": self.logs
        }
    
    def save_to_file(self, filename: str = "execution_log.json"):
        """Save logs to file"""
        with open(filename, 'w') as f:
            json.dump(self.logs, f, indent=2)