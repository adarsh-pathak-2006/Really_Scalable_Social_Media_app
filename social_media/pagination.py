from rest_framework.pagination import PageNumberPagination

class GeneralReelAndPostPagination(PageNumberPagination):
    page_size=10
    page_size_query_param='custom_page_size'
    max_page_size=100