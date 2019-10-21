from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.carts.models import OrderInfo, OrderGoods
from apps.meiduo_admin.utils.pagination import MeiduoPagination
from apps.meiduo_admin.serializers.order import OrderSimpleSerializer, OrderSerializer


class OrderViewSet(ReadOnlyModelViewSet):
    # queryset = OrderInfo.objects.order_by('-create_time')
    serializer_class = OrderSimpleSerializer
    pagination_class = MeiduoPagination

    # 重写查询方法
    def get_queryset(self):
        # 从查询参数中获取数据
        keyword = self.request.query_params.get('keyword')

        # 接收查询参数
        queryset = OrderInfo.objects
        if keyword:
            queryset = queryset.filter(order_id__contains=keyword)
        queryset = queryset.order_by('-create_time')
        return queryset

    # 判断查询一条还是多条
    def get_serializer_class(self):
        # list===>OrderSimpleSerializer
        # retrieve===>OrderSerializer
        # if self.request.kwargs
        # self.action===>当前请求要执行的方法名称
        if self.action == 'list':
            # 查询多条
            return OrderSimpleSerializer
        elif self.action == 'retrieve':
            # 查询一条
            return OrderSerializer

    # 修改订单信息
    @action(methods=['PUT'], detail=True)
    def status(self, request, *args, **kwargs):
        # detail=True==> put /orders/(?P<pk>[^/.]+)/status/
        # detail=False==>put /oders/status/
        # 修改指定订单的状态
        instance = self.get_object()
        instance.status = 3
        instance.save()

        return Response({
            'order_id': instance.order_id,
            'status': instance.status
        }, status=201)