class Error(Exception):
    """Base class for all exception in surpy."""


class FilePathError(Error):
    pass


class FileTypeError(Error):
    pass


class DataError(Error):
    pass
