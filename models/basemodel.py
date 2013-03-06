

class BaseModel(object):
    """BaseModel is just an abstract baseclass to show which operations
    must be supported by your models

    create - create path
    read - read data from path
    update - update data into path
    delete - delete given path
    list - list childs to the path

    Generic Exceptions

    Raises KeyError if path leading to path is not found

    """

    def is_dir(path):
        """Override this. Returns true if node should be listed
        as directory"""
        assert "Not implemented"

    def access(path):
        """Override this. Check if path exists with minimal effort.

        Return True if so
        """
        assert "Not implemented"

    def read(self, path, offset=0, count=-1):
        """Override this. Should return data for given path, offset and key."""
        assert "Not implemented"

    def update(self, path, data, offset=0):
        """Override this. Should update data given by path, data and offset."""
        assert "Not implemented"

    def create(self, path):
        """Override this. Should create path."""
        assert "Not implemented"

    def delete(self, path):
        """Override this. Should delete path."""
        assert "Not implemented"

    def list(self, path):
        """Override this. Should list childs at path."""
        assert "Not implemented"
