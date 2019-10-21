from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.image import ImageSerializer
from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.sku import ImageSkuSimpleSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


# 图片创建和查询操作


class ImageViewSet(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = SKUImage.objects.all()
    # 分页
    pagination_class = MeiduoPagination

    # 重写create方法创建图片
    def create(self, request, *args, **kwargs):
        # 接受
        sku = request.data.get('sku')
        image = request.data.get('image')

        # 验证
        if not all([sku, image]):
            return Response({'detail': '数据不完整'}, status=400)

        # 处理
        # 1.上传图片
        image_client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        data = image_client.upload_by_buffer(image.read())
        image_name = data.get("Remote file_id")

        # 2.创建图片模型类对象
        instance = SKUImage.objects.create(sku_id=sku, image=image_name)

        # 响应
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=201)

    # 重写update方法修改图片
    def update(self, request, *args, **kwargs):
        # 获取当前要修改的图片对象
        instance = self.get_object()

        # 接收
        sku_id = request.data.get('sku')
        image = request.data.get('image')

        # 验证
        if not all([sku_id]):
            return Response({'detail:＇数据不完整'}, status=400)

        # 处理
        # 1.fdfs:删除旧图片，上传新图片
        if image:
            # 如果用户上传图片则修改
            image_client = Fdfs_client(settings.FDFS_CLIENT_CONF)
            # 删除===>instance.image.name===>获取图片的名称字符串
            image_client.delete_file(instance.image.name)
            # 上传
            data = image_client.upload_by_buffer(image.read())
            instance.image = data.get("Remote file_id")

        # 2.修改对象
        instance.sku_id = sku_id
        instance.save()

        # 响应
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=201)

    # 重写destroy方法删除图片和数据　
    def destroy(self, request, *args, **kwargs):
        # 查询当前对象
        instance = self.get_object()
        image_client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        # 删除===>instance.logo.name===>获取图片的名称字符串
        image_client.delete_file(instance.image.name)
        # 删除图片
        instance.delete()

        # 响应
        return Response(status=204)


# 图片创建中的SKU的id 的查询
class ImageSkuSimpleView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = ImageSkuSimpleSerializer
