import time
import json
import os

CACHE_EXPIRY_SECONDS = 604800  # 7 days (7 * 24 * 60 * 60 seconds)

class CacheManager:
    def __init__(self, filename, data_getter=None):
        self.filename = filename
        self.data_getter = data_getter  # Function to get the data to save (for save)

    def save(self):
        if self.data_getter is None:
            raise ValueError("No data_getter function provided for saving cache.")
        data = self.data_getter()
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        with open(self.filename, 'w') as f:
            json.dump(cache_data, f)
        print(f"Saved {self.filename}")

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                cache_data = json.load(f)
                if time.time() - cache_data.get('timestamp', 0) < CACHE_EXPIRY_SECONDS:
                    data = cache_data.get('data', {})
                    
                    # Update the in-memory cache in api_endpoints
                    if hasattr(self, 'data_getter'):
                        import api.api_endpoints as api_endpoints
                        # Determine which cache to update based on filename
                        if self.filename == 'term_cache.json':
                            api_endpoints.term_cache.update(data)
                        elif self.filename == 'course_cache.json':
                            api_endpoints.course_cache.update(data)
                        elif self.filename == 'user_cache.json':
                            api_endpoints.user_cache.update(data)
                            
                    return data
        except Exception:
            pass
        return {}

    def clear(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print(f"Cleared {self.filename}")

# --- Setup for endpoints.py caches ---
def _get_term_cache():
    import api.api_endpoints as api_endpoints
    return api_endpoints.term_cache

def _get_course_cache():
    import api.api_endpoints as api_endpoints
    return api_endpoints.course_cache

def _get_user_cache():
    import api.api_endpoints as api_endpoints
    return api_endpoints.user_cache

term_cache_mgr = CacheManager('term_cache.json', _get_term_cache)
course_cache_mgr = CacheManager('course_cache.json', _get_course_cache)
user_cache_mgr = CacheManager('user_cache.json', _get_user_cache)

# --- Public API ---
def save_term_cache():
    term_cache_mgr.save()

def load_term_cache():
    return term_cache_mgr.load()

def save_course_cache():
    course_cache_mgr.save()

def load_course_cache():
    return course_cache_mgr.load()

def save_user_cache():
    user_cache_mgr.save()

def load_user_cache():
    return user_cache_mgr.load()

def clear_all_caches():
    term_cache_mgr.clear()
    course_cache_mgr.clear()
    user_cache_mgr.clear()
    print("All caches cleared.")