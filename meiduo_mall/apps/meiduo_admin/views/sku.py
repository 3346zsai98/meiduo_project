from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKU
from apps.meiduo_admin.serializers.sku import SkuModelSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


class SkuViewSet(ModelViewSet):

    # 指定序列化器
    serializer_class = SkuModelSerializer
    # 指定分页器
    pagination_class = MeiduoPagination

    # 重写get_queryset方法，判断是否传递keyword查询参数
    def get_queryset(self):
        # 1.接受查询参数中的关键字keyword
        keyword = self.request.query_params.get('keyword')

        # 2.拼接查询语句
        queryset = SKU.objects
        if keyword:
            # 标题和副标题包含指定关键字
            queryset = queryset.filter(Q(name__contains=keyword) | Q(caption__contains=keyword))
        queryset = queryset.order_by('-id')
        return queryset