from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password', 'groups', 'user_permissions']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        instance = super().create(validated_data)

        # 将密码加密
        instance.set_password(validated_data.get('password'))
        # 设置管理员
        instance.is_staff = True
        instance.save()

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # 将密码加密
        instance.set_password(validated_data.get('password'))
        instance.save()

        return instance
