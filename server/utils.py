# server/utils.py

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
        response = {
            "code": self.code,
            "message": self.message,
        }
        
        if self.errors:
            response["errors"] = self.errors
            
        return response
