# server/utils.py

class SuccessResponseBuilder:
    def __init__(self):
        self.message = "Success"
        self.code = 0
        self.data = {}

    def with_message(self, message: str):
        self.message = message
        return self

    def with_code(self, code: int):
        self.code = code
        return self

    def with_data(self, data: dict):
        self.data = data
        return self

    def build(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }


# Error Response Builder
class ErrorResponseBuilder:
    def __init__(self):
        self.message = "Error occurred"
        self.code = 1
        self.errors = {}

    def with_message(self, message: str):
        self.message = message
        return self

    def with_code(self, code: int):
        self.code = code
        return self

    def with_errors(self, errors: dict):
        self.errors = errors
        return self

    def build(self):
        return {
            "code": self.code,
            "message": self.message,
            "errors": self.errors,
        }