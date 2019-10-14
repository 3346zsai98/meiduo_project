from rest_framework import serializers
from apps.goods.models import GoodsCategory


# 三级商品分类序列化器
class Category3Serializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']
