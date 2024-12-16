class ResponseCheck:
    """Class to store response message from server. This is used to check if the report request was successful"""

    response = None

    @classmethod
    def set_response(cls, response) -> None:
        cls.response = response

    @classmethod
    def get_response(cls) -> str:
        return cls.response

    @classmethod
    def check_response(cls, expected_response) -> bool:
        result = cls.response == expected_response
        cls.response = None
        return result
