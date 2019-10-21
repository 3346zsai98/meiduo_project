from rest_framework import serializers
from apps.goods.models import SKUImage


# 获取图片表数据序列化器
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'

