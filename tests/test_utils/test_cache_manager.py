# import os
# import json
# import time
# import pytest
# from unittest.mock import MagicMock, patch
# from utils.cache_manager import CacheManager

# def test_save_and_load(tmp_path):
#     filename = tmp_path / 'cache.json'
#     data = {'foo': 'bar'}
#     data_getter = MagicMock(return_value=data)
#     mgr = CacheManager(str(filename), data_getter)
#     mgr.save()
#     loaded = mgr.load()
#     assert loaded == data
#     # Check file exists
#     assert os.path.exists(filename)

# def test_load_expired_cache(tmp_path):
#     filename = tmp_path / 'cache.json'
#     expired_time = time.time() - 604801 # 1 week plus 1 second
#     cache_data = {'timestamp': expired_time, 'data': {'foo': 'bar'}}
#     with open(filename, 'w') as f:
#         json.dump(cache_data, f)
#     mgr = CacheManager(str(filename))
#     assert mgr.load() == {}

# def test_save_without_data_getter(tmp_path):
#     filename = tmp_path / 'cache.json'
#     mgr = CacheManager(str(filename))
#     with pytest.raises(ValueError):
#         mgr.save()

# def test_clear(tmp_path):
#     filename = tmp_path / 'cache.json'
#     with open(filename, 'w') as f:
#         f.write('test')
#     mgr = CacheManager(str(filename))
#     assert os.path.exists(filename)
#     mgr.clear()
#     assert not os.path.exists(filename)

# def test_load_file_not_exist(tmp_path):
#     filename = tmp_path / 'cache.json'
#     mgr = CacheManager(str(filename))
#     assert mgr.load() == {}


# # WRITE MORE TESTS