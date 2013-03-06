
class BaseModel(object):
    """BaseModel is just an abstract baseclass to show which operations
    must be supported by your models"""

    def read(self, path, offset = 0, count = -1):
        """Override this. Should return data for given path, offset and key."""
        assert "Not implemented"

    def update(self, path, data, offset = 0):
        """Override this. Should update data given by path, data and offset."""
        assert "Not implemented"

    def create(self, path):
        """Override this. Should create path.

        Raises

        KeyError if path leading to path is not found
        """
        assert "Not implemented"

    def delete(self, path):
        """Override this. Should delete path.

        Raises

        KeyError if path leading to path is not found
        """
        assert "Not implemented"

    def list(self, path):
        """Override this. Should list childs at path."""
        assert "Not implemented"
