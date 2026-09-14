import json
import logging
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


class SimpleBoundedCache:
    def __init__(self, max_size: int = 50):
        self._max_size = max_size
        self._store: OrderedDict[str, Any] = OrderedDict()

    def make_key(self, payload: dict) -> str:
        return json.dumps(payload, sort_keys=True, default=str)

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._store.move_to_end(key)
        if len(self._store) > self._max_size:
            self._store.popitem(last=False)


# Known limitation: no TTL and no invalidation on new document uploads.
# A repeated identical query will return a cached result even if new documents
# were ingested since the cache entry was created. Acceptable for demo
# purposes given cache entries are only reused within one running process
# and the max size is small.
dense_search_cache = SimpleBoundedCache(max_size=50)
