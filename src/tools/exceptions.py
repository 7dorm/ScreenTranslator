class IncorrectFileTypeException(Exception):
    """
    Exception raised when model receives invalid media type.
    """

    def __init__(self, filetype: str) -> None:
        """
        Initialize the exception with invalid filetype.
        """
        self.filetype = filetype
        self.message = "IncorrectFileTypeException"
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Return a string representation of the exception.
        """
        return f"{self.message}: attempted to pass incorrect type: {self.filetype}"


class VideoNotInitializedException(Exception):
    """
    Exception raised when model can't process video file
    """

    def __init__(self) -> None:
        """
        Initialize the exception with invalid filetype.
        """
        self.message = "VideoNotInitializedException"
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Return a string representation of the exception.
        """
        return f"{self.message}: video can't be loaded!"
