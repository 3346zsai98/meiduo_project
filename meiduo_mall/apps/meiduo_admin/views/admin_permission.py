from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from apps.meiduo_admin.serializers.admin_permission import PermissionSerializer, PermissionSimpleSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


# 系统－权限管理
class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = MeiduoPagination


class PermissionSimpleView(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSimpleSerializer
