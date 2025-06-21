"""
Performance Optimization Module for The Signal Cartographer
Handles memory management, rendering optimizations, and error handling
"""

import gc
import time
import traceback
import weakref
from typing import Any, Dict, List, Optional, Callable
from functools import wraps, lru_cache
import threading
import queue


class MemoryManager:
    """Manages memory usage and cleanup for the game"""
    
    def __init__(self):
        # Use a simple list instead of WeakSet for better compatibility
        self.tracked_object_count = 0
        self.cleanup_threshold = 100  # Cleanup after 100 allocations
        self.allocation_count = 0
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # Cleanup every 60 seconds
        
    def track_object(self, obj):
        """Track an object for memory management"""
        # Just increment counters instead of storing weak references
        self.tracked_object_count += 1
        self.allocation_count += 1
        
        # Periodic cleanup
        if (self.allocation_count >= self.cleanup_threshold or 
            time.time() - self.last_cleanup > self.cleanup_interval):
            self.cleanup()
    
    def cleanup(self):
        """Perform memory cleanup"""
        # Force garbage collection
        collected = gc.collect()
        
        # Reset counters
        self.allocation_count = 0
        self.last_cleanup = time.time()
        
        return collected
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        return {
            'tracked_objects': self.tracked_object_count,
            'allocation_count': self.allocation_count,
            'last_cleanup': time.time() - self.last_cleanup,
            'gc_stats': len(gc.get_stats()) if hasattr(gc, 'get_stats') else 0
        }


class RenderCache:
    """Caching system for expensive rendering operations"""
    
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached render result"""
        if key in self.cache:
            self.access_times[key] = time.time()
            self.hit_count += 1
            return self.cache[key]
        
        self.miss_count += 1
        return None
    
    def put(self, key: str, value: Any):
        """Cache a render result"""
        # Cleanup if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def _evict_oldest(self):
        """Remove the oldest cache entry"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self):
        """Clear the entire cache"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate
        }


class ErrorHandler:
    """Centralized error handling with graceful degradation"""
    
    def __init__(self):
        self.error_count = {}
        self.error_callbacks = {}
        self.max_errors_per_type = 5
        self.suppressed_errors = set()
    
    def handle_error(self, error: Exception, context: str = "unknown", 
                    fallback: Callable = None) -> Any:
        """Handle an error with graceful fallback"""
        error_type = type(error).__name__
        
        # Track error frequency
        if error_type not in self.error_count:
            self.error_count[error_type] = 0
        self.error_count[error_type] += 1
        
        # Suppress repeated errors
        if (error_type in self.suppressed_errors or 
            self.error_count[error_type] > self.max_errors_per_type):
            if fallback:
                return fallback()
            return None
        
        # Log error (in a real app, this would go to a proper logger)
        error_msg = f"Error in {context}: {error_type}: {str(error)}"
        print(f"[ERROR] {error_msg}")
        
        # Call registered callback if available
        if error_type in self.error_callbacks:
            try:
                return self.error_callbacks[error_type](error, context)
            except Exception as callback_error:
                print(f"[ERROR] Callback failed: {callback_error}")
        
        # Execute fallback
        if fallback:
            try:
                return fallback()
            except Exception as fallback_error:
                print(f"[ERROR] Fallback failed: {fallback_error}")
        
        return None
    
    def register_callback(self, error_type: str, callback: Callable):
        """Register a callback for a specific error type"""
        self.error_callbacks[error_type] = callback
    
    def suppress_error_type(self, error_type: str):
        """Suppress further logging of a specific error type"""
        self.suppressed_errors.add(error_type)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'error_counts': self.error_count.copy(),
            'suppressed_errors': list(self.suppressed_errors),
            'total_errors': sum(self.error_count.values())
        }


def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Log performance data even on error
            duration = time.time() - start_time
            print(f"[PERF] {func.__name__} failed after {duration:.3f}s: {e}")
            raise
        finally:
            duration = time.time() - start_time
            if duration > 0.1:  # Log slow operations
                print(f"[PERF] {func.__name__} took {duration:.3f}s")
    
    return wrapper


def debounce(wait_time: float):
    """Decorator to debounce function calls"""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait_time:
                last_called[0] = now
                return func(*args, **kwargs)
            return None
        
        return wrapper
    return decorator


# Global instances
memory_manager = MemoryManager()
render_cache = RenderCache()
error_handler = ErrorHandler()


def optimize_ascii_rendering(render_func: Callable) -> Callable:
    """Optimize ASCII rendering with caching and debouncing"""
    @debounce(0.05)  # Debounce to 20 FPS max
    @performance_monitor
    def optimized_render(*args, **kwargs):
        # Generate cache key from arguments
        cache_key = f"{render_func.__name__}_{hash(str(args))}"
        
        # Check cache first
        cached_result = render_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Render with error handling
        try:
            result = render_func(*args, **kwargs)
            render_cache.put(cache_key, result)
            return result
        except Exception as e:
            return error_handler.handle_error(
                e, f"rendering_{render_func.__name__}",
                lambda: ["[Error rendering display]"]
            )
    
    return optimized_render


def cleanup_old_data(data_dict: Dict, max_age: float = 300.0):
    """Clean up old data entries (older than max_age seconds)"""
    current_time = time.time()
    keys_to_remove = []
    
    for key, value in data_dict.items():
        # Assume data has a 'timestamp' attribute
        if hasattr(value, 'timestamp'):
            if current_time - value.timestamp > max_age:
                keys_to_remove.append(key)
        elif isinstance(value, dict) and 'timestamp' in value:
            if current_time - value['timestamp'] > max_age:
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del data_dict[key]
    
    return len(keys_to_remove)


class PerformanceProfiler:
    """Simple performance profiler for identifying bottlenecks"""
    
    def __init__(self):
        self.timings = {}
        self.call_counts = {}
    
    def time_function(self, func_name: str, duration: float):
        """Record timing for a function"""
        if func_name not in self.timings:
            self.timings[func_name] = []
            self.call_counts[func_name] = 0
        
        self.timings[func_name].append(duration)
        self.call_counts[func_name] += 1
        
        # Keep only recent timings
        if len(self.timings[func_name]) > 100:
            self.timings[func_name] = self.timings[func_name][-50:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        for func_name in self.timings:
            timings = self.timings[func_name]
            if timings:
                stats[func_name] = {
                    'call_count': self.call_counts[func_name],
                    'avg_time': sum(timings) / len(timings),
                    'max_time': max(timings),
                    'min_time': min(timings),
                    'total_time': sum(timings)
                }
        
        return stats
    
    def get_slowest_functions(self, limit: int = 5) -> List[tuple]:
        """Get the slowest functions by average time"""
        stats = self.get_stats()
        sorted_funcs = sorted(stats.items(), 
                            key=lambda x: x[1]['avg_time'], 
                            reverse=True)
        return sorted_funcs[:limit]


# Global profiler instance
profiler = PerformanceProfiler()
