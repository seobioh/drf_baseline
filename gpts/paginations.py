# gpts/paginations.py
app_name = "gpts"

from rest_framework.pagination import CursorPagination

class GPTChatMessagePagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    cursor_query_param = 'cursor'
    ordering = '-id'