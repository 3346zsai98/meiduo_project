from rest_framework import serializers
from apps.carts.models import OrderInfo, OrderGoods


# 查询所有订单信息
class OrderSimpleSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    create_time = serializers.DateTimeField()


# 1119623958
class SkuRelatedSerializer(serializers.Serializer):
    name = serializers.CharField()
    default_image = serializers.ImageField()


#
class DetailRelatedSerializer(serializers.ModelSerializer):
    sku = SkuRelatedSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['count', 'price', 'sku']


# 查询一条订单的所有信息
class OrderSerializer(serializers.ModelSerializer):
    # 用户
    user = serializers.StringRelatedField(read_only=True)
    # 订单商品
    skus = DetailRelatedSerializer(read_only=True, many=True)

    class Meta:
        model = OrderInfo
        fields = "__all__"
