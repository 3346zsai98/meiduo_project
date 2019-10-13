from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPUSpecification
from apps.meiduo_admin.serializers.specs import SPUSpecificationSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


# 查询一条、修改、删除都已经被封装好，不需要编写代码
class SpecsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecificationSerializer
    pagination_class = MeiduoPagination