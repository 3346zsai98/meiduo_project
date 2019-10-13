from rest_framework import serializers

from apps.goods.models import GoodsVisitCount


class GoodsSerializer(serializers.ModelSerializer):
    # 指定返回分类名称
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        # 指定模型类
        model = GoodsVisitCount
        # 指定返回的数据
        fields = ['count', 'category']
