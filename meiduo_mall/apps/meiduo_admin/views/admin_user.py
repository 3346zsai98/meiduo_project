from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.serializers.admin_user import UserSerializer
from apps.users.models import User
from apps.meiduo_admin.utils.pagination import MeiduoPagination


class UserViewSet(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer
    pagination_class = MeiduoPagination