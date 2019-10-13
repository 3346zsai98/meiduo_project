from rest_framework.generics import ListAPIView

from apps.goods.models import SPU
from apps.meiduo_admin.serializers.spuzsg import SPUSerializer


# 保存多条数据
class SPUSimpleViewSet(ListAPIView):
    serializer_class = SPUSerializer
    queryset = SPU.objects.all()
