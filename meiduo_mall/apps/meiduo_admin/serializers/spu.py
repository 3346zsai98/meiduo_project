from rest_framework import serializers
from apps.goods.models import SPU


# spu查询
class SPUSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()
    category1 = serializers.PrimaryKeyRelatedField(read_only=True)
    category2 = serializers.PrimaryKeyRelatedField(read_only=True)
    category3 = serializers.PrimaryKeyRelatedField(read_only=True)


    class Meta:
        model = SPU
        fields = "__all__"


# 品牌查询
class SPUDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()


# category1的查询
class SPUC1Serializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField(read_only=True)
