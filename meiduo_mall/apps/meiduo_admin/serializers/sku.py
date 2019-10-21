from rest_framework import serializers
from apps.goods.models import SKU, SKUSpecification
from django.db import transaction
from celery_tasks.detail.tasks import generate_task


# class SpecRelatedSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SKUSpecification
#         fields = ['spec_id', 'option_id']
class SpecRelatedSerializer(serializers.Serializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()


class SkuModelSerializer(serializers.ModelSerializer):
    # 标准商品
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    # 第三级分类
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()
    # 规格信息
    specs = SpecRelatedSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    # 保存SKU数据
    def create(self, validated_data):
        # 取出值specs
        specs = validated_data.pop('specs')

        # 禁止自动提交
        with transaction.atomic():
            # 开启事务
            sid = transaction.savepoint()
            try:
                # 1.创建sku对象
                sku = super().create(validated_data)

                # 2.创建sku的规格对象===>遍历
                for item in specs:
                    # sku规格对象需要指定：sku_id,spec_id,option_id
                    item['sku_id'] = sku.id
                    # 创建sku规格对象
                    SKUSpecification.objects.create(**item)
            except:
                # 回滚事务
                transaction.savepoint_rollback(sid)
                raise serializers.ValidationError('创建sku失败')
            else:
                # 没有异常，数据库操作成功，提交事务
                transaction.savepoint_commit(sid)

                # 执行异步任务生成静态文件
                generate_task.delay(sku.id)
                return sku

    # 修改商品
    def update(self, instance, validated_data):
        # 1.取出specs数据
        specs = validated_data.pop('specs')

        with transaction.atomic():
            # 开启事物
            sid = transaction.savepoint()
            try:
                # 2.调用父类方法修改实例
                instance = super().update(instance, validated_data)

                # 3.修改规格和选项
                # 3.1删除所有规格
                SKUSpecification.objects.filter(sku_id=instance.id).delete()

                # 3.2遍历，创建规格
                for item in specs:
                    item['sku_id'] = instance.id
                    SKUSpecification.objects.create(**item)
            except:
                transaction.savepoint_rollback(sid)
                raise serializers.ValidationError('修改sku失败')
            else:
                transaction.savepoint_commit(sid)
                # 执行异步任务生成静态文件
                generate_task.delay(instance.id)

                return instance


# 图片创建中获取SKU的id 和name
class ImageSkuSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
