# custom_exceptions.py

class ConnectFailed(Exception):

    def __init__(self, message="Currency conversion failed"):
        super().__init__(message)
