# server/utils.py

class SuccessResponseBuilder:
    def __init__(self):
        self.message = "Success"
        self.code = 0
        self.data = {}
        self.pagination = None

    def with_message(self, message: str):
        self.message = message
        return self

    def with_code(self, code: int):
        self.code = code
        return self

    def with_data(self, data: dict):
        self.data = data
        return self

    def with_cursor_pagination(self, paginator):
        self.pagination = get_cursor_pagination_data(paginator)
        return self

    def with_page_pagination(self, paginator, page):
        self.pagination = get_page_pagination_data(paginator, page)
        return self

    def build(self):
        response = {
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }
        if self.pagination is not None:
            response["pagination"] = self.pagination
        return response


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


def get_cursor_pagination_data(paginator):
    return {
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'page_size': paginator.page_size,
    }


def get_page_pagination_data(paginator, page):
    return {
        'count': paginator.page.paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'page_size': paginator.page_size,
        'current_page': paginator.page.number,
        'total_pages': paginator.page.paginator.num_pages
    }