from rest_framework import serializers
from apps.goods.models import GoodsChannel, GoodsChannelGroup


# 增加查询修改删除
class ChannelsSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()
    group = serializers.StringRelatedField(read_only=True)
    group_id = serializers.IntegerField()

    class Meta:
        model = GoodsChannel
        fields = '__all__'


# 频道管理中新增数据时获取频道组
class ChannelTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsChannelGroup
        fields = "__all__"
