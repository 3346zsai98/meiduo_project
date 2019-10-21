from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from apps.goods.models import GoodsChannel, GoodsChannelGroup
from apps.meiduo_admin.serializers.channels import ChannelsSerializer, ChannelTypesSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


class ChannelsViewSet(ModelViewSet):
    queryset = GoodsChannel.objects.all()
    serializer_class = ChannelsSerializer
    pagination_class = MeiduoPagination


# 获取频道组
class ChannelTypeView(ListAPIView):
    queryset = GoodsChannelGroup.objects.all()
    serializer_class = ChannelTypesSerializer

