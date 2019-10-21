from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SPU, Brand, GoodsCategory
from apps.meiduo_admin.utils.pagination import MeiduoPagination
from apps.meiduo_admin.serializers.spu import SPUSerializer, SPUDetailSerializer, SPUC1Serializer


# spu查询
class SpuViewSet(ModelViewSet):
    queryset = SPU.objects.all()
    serializer_class = SPUSerializer
    pagination_class = MeiduoPagination

    # def create(self, request, *args, **kwargs):


# 品牌查询
class SpuDetailView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = SPUDetailSerializer


# category1的查询
class SpuC1View(ListAPIView):
    queryset = GoodsCategory.objects.filter(parent__isnull=True)
    serializer_class = SPUC1Serializer


# category2,3的查询
class SPUC23View(ListAPIView):
    def get_queryset(self):
        keyword = self.kwargs.get('pk')
        if keyword:
            queryset = GoodsCategory.objects.filter(parent=keyword)
            return queryset
        else:
            return Response(status=400)

    serializer_class = SPUC1Serializer
