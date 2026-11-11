from rest_framework.pagination import PageNumberPagination

API_PAGE_SIZE = 6
MAX_PAGE_SIZE = 100


class LimitPageNumberPagination(PageNumberPagination):
    page_size = API_PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE
