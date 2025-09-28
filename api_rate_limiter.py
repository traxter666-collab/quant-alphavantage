#!/usr/bin/env python3
"""
AlphaVantage API Rate Limiter - Prevents API quota exhaustion
Manages API calls during high-frequency periods like market open
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable
import threading

class APIRateLimiter:
    def __init__(self, calls_per_minute: int = 75):
        """
        Initialize rate limiter
        calls_per_minute: API limit (75 for premium, 5 for free)
        """
        self.calls_per_minute = calls_per_minute
        self.call_log = []
        self.lock = threading.Lock()
        
        # API call tracking
        self.daily_calls = 0
        self.daily_limit = 500  # Adjust based on your plan
        self.day_start = datetime.now().date()
        
    def can_make_call(self) -> bool:
        """Check if we can make an API call without hitting limits"""
        with self.lock:
            now = time.time()
            
            # Remove calls older than 1 minute
            self.call_log = [call_time for call_time in self.call_log if now - call_time < 60]
            
            # Check daily limit
            current_date = datetime.now().date()
            if current_date != self.day_start:
                self.daily_calls = 0
                self.day_start = current_date
            
            if self.daily_calls >= self.daily_limit:
                print(f"❌ Daily API limit reached: {self.daily_calls}/{self.daily_limit}")
                return False
            
            # Check per-minute limit
            if len(self.call_log) >= self.calls_per_minute:
                wait_time = 60 - (now - self.call_log[0])
                print(f"⚠️  Rate limit reached. Wait {wait_time:.1f} seconds")
                return False
            
            return True
    
    def record_call(self):
        """Record that an API call was made"""
        with self.lock:
            self.call_log.append(time.time())
            self.daily_calls += 1
    
    def wait_for_availability(self, max_wait: int = 60) -> bool:
        """
        Wait until we can make an API call
        Returns True if available, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.can_make_call():
                return True
            time.sleep(1)
        
        return False
    
    def get_status(self) -> Dict:
        """Get current rate limiting status"""
        with self.lock:
            now = time.time()
            recent_calls = len([t for t in self.call_log if now - t < 60])
            
            return {
                'calls_this_minute': recent_calls,
                'per_minute_limit': self.calls_per_minute,
                'daily_calls': self.daily_calls,
                'daily_limit': self.daily_limit,
                'can_make_call': self.can_make_call()
            }

class MarketOpenAPIManager:
    """Prioritized API call manager for market open"""
    
    def __init__(self, rate_limiter: APIRateLimiter):
        self.rate_limiter = rate_limiter
        self.priority_calls = {
            1: [],  # Critical (SPX price, major breakouts)
            2: [],  # High (MAG 7 status, volume analysis) 
            3: [],  # Medium (technical indicators)
            4: [],  # Low (news sentiment, extended analysis)
        }
    
    def add_priority_call(self, priority: int, func: Callable, *args, **kwargs):
        """Add API call to priority queue"""
        call_data = {
            'function': func,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time()
        }
        self.priority_calls[priority].append(call_data)
    
    def execute_priority_calls(self) -> Dict:
        """Execute calls in priority order with rate limiting"""
        results = {}
        total_calls = 0
        
        print("🚀 Executing market open API calls...")
        
        # Process by priority (1 = highest)
        for priority in sorted(self.priority_calls.keys()):
            calls = self.priority_calls[priority]
            
            for call_data in calls:
                if not self.rate_limiter.wait_for_availability(max_wait=30):
                    print(f"⚠️  Skipping priority {priority} calls - rate limited")
                    break
                
                try:
                    func = call_data['function']
                    result = func(*call_data['args'], **call_data['kwargs'])
                    
                    self.rate_limiter.record_call()
                    total_calls += 1
                    
                    # Store result with function name
                    func_name = func.__name__ if hasattr(func, '__name__') else str(func)
                    results[f"priority_{priority}_{func_name}"] = result
                    
                    print(f"✅ Priority {priority}: {func_name}")
                    
                    # Small delay between calls
                    time.sleep(0.8)
                    
                except Exception as e:
                    print(f"❌ API call failed: {e}")
                    continue
        
        print(f"📊 Market open calls completed: {total_calls} total")
        return results

# Market Open Priority Setup
def setup_market_open_calls(api_manager: MarketOpenAPIManager):
    """Configure priority API calls for market open"""
    
    # Priority 1: Critical market data
    # api_manager.add_priority_call(1, get_spx_price)
    # api_manager.add_priority_call(1, get_spy_quote)
    
    # Priority 2: MAG 7 monitoring  
    # for symbol in ['NVDA', 'MSFT', 'GOOGL', 'META', 'TSLA', 'AAPL', 'AMZN']:
    #     api_manager.add_priority_call(2, get_stock_quote, symbol)
    
    # Priority 3: Technical indicators
    # api_manager.add_priority_call(3, get_spy_rsi)
    # api_manager.add_priority_call(3, get_spy_volume)
    
    # Priority 4: Extended analysis
    # api_manager.add_priority_call(4, get_news_sentiment)
    # api_manager.add_priority_call(4, get_earnings_calendar)
    
    print("🎯 Market open API calls configured")

if __name__ == "__main__":
    # Test rate limiter
    limiter = APIRateLimiter(calls_per_minute=5)  # Free tier for testing
    api_manager = MarketOpenAPIManager(limiter)
    
    # Show status
    status = limiter.get_status()
    print(f"📊 Rate Limiter Status: {status}")