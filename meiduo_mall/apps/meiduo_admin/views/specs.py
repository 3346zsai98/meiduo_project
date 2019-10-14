from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPUSpecification
from apps.meiduo_admin.serializers.specs import SPUSpecificationSerializer, SpecOptionSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


# 查询一条、修改、删除都已经被封装好，不需要编写代码
class SpecsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecificationSerializer
    pagination_class = MeiduoPagination


class SpecOptionView(ListAPIView):
    def get_queryset(self):
        # 需要从路中接受spu_id,用于查询指定spu的所有规格
        # self.kwargs===>获取路径中的关键字参数
        spu_id = self.kwargs.get('pk')
        # 根据spu的id值关联过滤查询出规格信息
        return SPUSpecification.objects.filter(spu_id=spu_id)

    serializer_class = SpecOptionSerializer
