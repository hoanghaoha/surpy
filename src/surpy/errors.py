class Error(Exception):
    """Base class for all exception in surpy."""


class FileTypeError(Error):
    pass


class DataError(Error):
    pass
