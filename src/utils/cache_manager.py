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
                    return cache_data.get('data', {})
        except Exception:
            pass
        return {}

    def clear(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print(f"Cleared {self.filename}")


# --- Setup for endpoint caches ---
term_cache = {}
course_cache = {}
user_cache = {}

term_cache_mgr = CacheManager('term_cache.json', lambda: term_cache)
course_cache_mgr = CacheManager('course_cache.json', lambda: course_cache)
user_cache_mgr = CacheManager('user_cache.json', lambda: user_cache)

# --- Public API ---
def save_term_cache():
    term_cache_mgr.save()

def load_term_cache():
    term_cache.update(term_cache_mgr.load())
    return term_cache

def save_course_cache():
    course_cache_mgr.save()

def load_course_cache():
    course_cache.update(course_cache_mgr.load())
    return course_cache

def save_user_cache():
    user_cache_mgr.save()

def load_user_cache():
    user_cache.update(user_cache_mgr.load())
    return user_cache

def clear_all_caches():
    term_cache_mgr.clear()
    course_cache_mgr.clear()
    user_cache_mgr.clear()
    print("All caches cleared.")
