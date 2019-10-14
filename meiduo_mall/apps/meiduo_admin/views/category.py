from rest_framework.generics import ListAPIView
from apps.meiduo_admin.serializers.category import Category3Serializer
from apps.goods.models import GoodsCategory


class Category3View(ListAPIView):
    # 第三级分类的特点：没有子级分类,即subs为空
    queryset = GoodsCategory.objects.filter(subs__isnull=True)
    serializer_class = Category3Serializer
