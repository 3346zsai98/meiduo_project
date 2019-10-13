from django.db.models import Q
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from apps.meiduo_admin.serializers.users import UserSerializer, UserCreateSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination
from apps.users.models import User


class UserView(ListCreateAPIView):
    # permission_classes = [IsAdminUser]
    # 指定查询序列化器
    # queryset = User.objects.filter(is_staff=False)
    def get_queryset(self):
        # self===>UserView的对象
        # 获取搜索关键字
        keyword = self.request.query_params.get('keyword')
        # 在用户名上进行关键字模糊查询
        if keyword == '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(
                Q(username__contains=keyword) | Q(mobile__contains=keyword) | Q(email__contains=keyword),
                is_staff=False)

    # serializer_class = UserSerializer
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserCreateSerializer

    # 重写分页方法中返回的数据
    pagination_class = MeiduoPagination
