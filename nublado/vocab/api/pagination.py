from core.api.views_api import StandardPagination


class SmallPagination(StandardPagination):
    page_size = 10


class LargePagination(StandardPagination):
    page_size = 100
