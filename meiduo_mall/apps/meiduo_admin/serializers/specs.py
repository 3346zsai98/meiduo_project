from rest_framework import serializers
from apps.goods.models import SpecificationOption
from apps.goods.models import SPUSpecification


class SPUSpecificationSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'


# 规格选项序列化器
class OptionRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


# 规格序列化器
class SpecOptionSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    # 关联序列化返回　规格选项信息
    options = OptionRelatedSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'


# 规格选项表操作

class SpecsOptSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()
    class Meta:
        model = SpecificationOption
        fields = "__all__"
