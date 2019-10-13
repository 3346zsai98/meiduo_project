from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MeiduoPagination(PageNumberPagination):
    # 默认页大小
    page_size = 10
    # 页大小最大值
    max_page_size = 100
    # 查询参数中页大小的键
    page_size_query_param = 'pagesize'

    # 重写分页的响应体方法，指定前端需要的字典
    def get_paginated_response(self, data):
        return Response({
            # 当前总条数
            'counts': self.page.paginator.count,
            # 当前页数据
            'lists': data,
            # 当前页码
            'page': self.page.number,
            # 总页数
            'pages': self.page.paginator.num_pages,
            # 每页容量
            'pagesize': self.page_size
        })
