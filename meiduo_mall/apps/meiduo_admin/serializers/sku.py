from rest_framework import serializers
from apps.goods.models import SKU, SKUSpecification


class SpecRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SkuModelSerializer(serializers.ModelSerializer):
    # 标准商品
    spu = serializers.StringRelatedField(read_only=True)
    # 第三级分类
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()
    # 规格信息
    specs = SpecRelatedSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = '__all__'
