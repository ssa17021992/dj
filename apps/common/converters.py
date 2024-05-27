class B64Converter:
    """B64 converter"""

    regex = "[a-zA-Z0-9-_]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
