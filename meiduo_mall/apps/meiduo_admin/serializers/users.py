import re
from rest_framework import serializers

from apps.users.models import User


# 查询用户序列化器
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email']


# 创建用户序列化器
class UserCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    mobile = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    # 验证用户名
    def validate_username(self, value):
        # 字符,长度限制
        if not re.match(r'^[a-zA-Z0-9]{5,20}$', value):
            raise serializers.ValidationError('用户名为5-20个字符')
        # 是否存在
        if User.objects.filter(username=value).count() > 0:
            raise serializers.ValidationError("用户名已经存在")
        return value

    # 验证手机号
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        if User.objects.filter(mobile=value).count() > 0:
            raise serializers.ValidationError('手机号已经存在')
        return value

    # 验证邮箱，密码
    def create(self, validated_data):
        # 自定义create()方法，需要将密码加密再保存
        user = User.objects.create_user(**validated_data)

        return user
