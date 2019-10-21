from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from apps.meiduo_admin.serializers.admin_group import GroupSerializer, GroupSimpleSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


# 组管理
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MeiduoPagination


class GroupSimpleView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSimpleSerializer
