from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import Brand, SKUImage
from apps.meiduo_admin.serializers.brands import BrandsSerializer
from apps.meiduo_admin.utils.pagination import MeiduoPagination


class BrandsViewSet(ModelViewSet):
    queryset = Brand.objects.all().order_by('-id')
    serializer_class = BrandsSerializer
    pagination_class = MeiduoPagination

    def create(self, request, *args, **kwargs):
        # 接受
        name = request.data.get('name')
        first_letter = request.data.get('first_letter')
        logo = request.data.get('logo')

        # 验证
        if not all([name, first_letter, logo]):
            return Response({'detail': '数据不完整'}, status=400)

        # 处理
        # 1.上传图片
        image_client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        data = image_client.upload_by_buffer(logo.read())
        image_name = data.get("Remote file_id")

        # 2.创建图片模型类对象
        instance = Brand.objects.create(name=name, first_letter=first_letter, logo=image_name)

        # 响应
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        # 获取当前要修改的图片对象
        instance = self.get_object()

        # 接收
        name = request.data.get('name')
        first_letter = request.data.get('first_letter')
        logo = request.data.get('logo')

        # 验证
        if not all(['name', 'first_letter']):
            return Response({'detail:＇数据不完整'}, status=400)
        # 处理
        # 1.fdfs:删除旧图片，上传新图片
        if logo:
            # 如果用户上传图片则修改
            image_client = Fdfs_client(settings.FDFS_CLIENT_CONF)
            # 删除===>instance.logo.name===>获取图片的名称字符串
            image_client.delete_file(instance.logo.name)
            # 上传
            data = image_client.upload_by_buffer(logo.read())
            instance.logo = data.get("Remote file_id")
            instance.name = name
            instance.first_letter = first_letter
        else:
            instance.name = name
            instance.first_letter = first_letter
        # 2.保存对象
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
        image_client.delete_file(instance.logo.name)
        # 删除图片和数据
        instance.delete()

        # 响应
        return Response(status=204)
