class LookupCache:
    """
    Generic in-memory lookup cache.
    """

    def __init__(self):

        self._data = {}

    def clear(self):

        self._data.clear()

    def add(self, key, value):

        self._data[key] = value

    def get(self, key, default=None):

        return self._data.get(key, default)

    def exists(self, key):

        return key in self._data

    def values(self):

        return self._data.values()

    def keys(self):

        return self._data.keys()

    def items(self):

        return self._data.items()

    def size(self):

        return len(self._data)