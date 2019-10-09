import json
from datetime import datetime

from decimal import Decimal
import time
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.carts.models import OrderInfo, OrderGoods
from apps.goods.models import SKU
from apps.users.models import Address
from utils.response_code import RETCODE


# 详情页展示评价信息
class OrderComments(View):
    def get(self, request, sku_id):
        # 获取被评价的订单商品的信息
        goods_list = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')[:30]
        comment_list = []
        for goods in goods_list:
            username = goods.order.user.username
            comment_list.append({
                'username': username[0] + '***' + username[-1] if goods.is_anonymous else username,
                'comment': goods.comment,
                'score': goods.score,
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'comment_list': comment_list})


# 展示商品评价页面
class OrderComment(View):
    # 展示商品评价页面
    def get(self, request):
        order_id = request.GET.get('order_id')
        user = request.user
        try:
            OrderInfo.objects.get(user=user, order_id=order_id)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')
        try:
            # 获取订单商品信息
            goods_list = OrderGoods.objects.filter(order=order_id, is_commented=False)
        except Exception as e:
            return http.HttpResponseForbidden('订单商品出错')

        # 创建列表存储多条订单信息
        uncomment_goods_list = []
        for goods in goods_list:
            # 获取每条订单的信息
            goods_dict = {
                'order_id': goods.order.order_id,
                'sku_id': goods.sku.id,
                'name': goods.sku.name,
                'price': str(goods.price),
                'default_image_url': goods.sku.default_image.url,
                'comment': goods.comment,
                'score': goods.score,
                'is_anonymous': str(goods.is_anonymous),
            }
            # 追加添加每条订单
            uncomment_goods_list.append(goods_dict)
        context = {"uncomment_goods_list": uncomment_goods_list}
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        # 接收前端传来的参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # 校验参数
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden("请填写所有内容")
        # 判断订单是否存在
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单不存在')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        # 判断订单内商品是否存在以及是否评价
        try:
            OrderGoods.objects.get(order_id=order_id, is_commented=False, sku=sku_id)
        except OrderGoods.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在或已经评价')
        # 修改数据库中订单信息以及状态
        OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).\
            update(is_anonymous=is_anonymous, score=score, comment=comment, is_commented=True)

        # 累计评论数据
        sku.comments += 1
        sku.save()
        sku.spu.comments += 1
        sku.spu.save()

        # 如果所有订单商品都已经评价，则修改订单状态为已完成
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})


# 我的订单展示
class OrderMy(LoginRequiredMixin,View):
    def get(self, request, page_num):
        # 获取登陆用户
        user = request.user
        # 获取所有订单数据
        orders = user.orderinfo_set.all().order_by('-create_time')
        # 遍历获取所有订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 绑定支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            # 遍历订单商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.price = order_good.price
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        # 分页
        try:
            paginator = Paginator(orders, 5)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except Exception as e:
            return http.HttpResponseNotFound('订单不存在')
        context = {
            # 每页显示的内容
            "page_orders": page_orders,
            # 总页数
            'total_page': total_page,
            # 当前页
            'page_num': page_num,
        }

        return render(request, 'user_center_order.html', context)


# 订单提交成功
class OrderSuccessView(LoginRequiredMixin, View):
    """订单提交成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


# 保存订单
class OrderCommitView(LoginRequiredMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 获取当前要保存的订单数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传的参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('暂不支持这种支付方式！')

        # 获取登陆用户
        user = request.user
        # 订单表－－生成订单编号：年月分时分秒＋用户编号
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        from django.db import transaction

        # ------设置事物起始--------
        with transaction.atomic():
            # -------事物保存点------
            save_id = transaction.savepoint()
            try:

                # 创建订单表数据（单个）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,

                    total_count=0,
                    total_amount=Decimal('0'),

                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # 从购物车 取出选中的商品
                redis_client = get_redis_connection('carts')
                carts_data = redis_client.hgetall(user.id)
                carts_dict = {}
                for key, value in carts_data.items():
                    sku_id = int(key.decode())
                    sku_dict = json.loads(value.decode())

                    if sku_dict['selected']:
                        carts_dict[sku_id] = sku_dict

                sku_ids = carts_dict.keys()
                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)

                        # 原始销量和库存量
                        origin_sales = sku.sales
                        origin_stock = sku.stock

                        # 　判断库存是否充足
                        cart_count = carts_dict[sku_id]['count']
                        if cart_count > sku.stock:
                            # ---------事物回滚-------
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                        # 模拟资源抢夺
                        # time.sleep(10)
                        # sku库存减少　销量增加
                        # sku.stock -= cart_count
                        # sku.sales += cart_count
                        # sku.save()

                        # 使用乐观锁，更新库存量
                        new_stock = origin_stock - cart_count
                        new_sales = origin_sales + cart_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)

                        # 如果下单失败，库存足够则继续下单，知道下单成功或者库存不足
                        if result == 0:
                            continue

                        # spu 销量增加
                        sku.spu.sales += cart_count
                        sku.spu.save()

                        # 创建订单商品数据（多个）
                        OrderGoods.objects.create(
                            order_id=order_id,
                            sku=sku,
                            count=carts_dict[sku_id]['count'],
                            price=sku.price
                        )

                        # 总个数 和 总金额（没运费）
                        order.total_count += carts_dict[sku_id]['count']
                        order.total_amount += sku.price * carts_dict[sku_id]['count']

                        # 下单成功　或失败跳出
                        break

                # 加运费　总金额
                order.total_amount += order.freight
                order.save()
            except:
                # -------事物回滚-------
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单失败'})
            # ------提交事物-------
            transaction.savepoint_commit(save_id)
        # 清空购物车内购买的数据
        redis_client.hdel(user.id, *carts_dict)

        # 返回响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


# 结算订单
class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 获取登陆用户
        user = request.user

        # 1.查询地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except:
            # 如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
            addresses = None

        # 2.查询选中商品
        redis_client = get_redis_connection('carts')
        carts_data = redis_client.hgetall(user.id)
        # 转换格式
        carts_dict = {}
        for key, value in carts_data.items():
            sku_id = int(key.decode())
            sku_dict = json.loads(value.decode())
            if sku_dict['selected']:
                carts_dict[sku_id] = sku_dict

        # 3.计算金额＋邮费
        total_count = 0
        total_amount = Decimal(0.00)

        skus = SKU.objects.filter(id__in=carts_dict.keys())

        for sku in skus:
            sku.count = carts_dict[sku.id].get('count')
            sku.amount = sku.count * sku.price
            # 计算总数量和总金额
            total_count += sku.count
            total_amount += sku.count * sku.price

        # 运费
        freight = Decimal('10.00')

        # 4.构建前端显示的数据
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
            'default_address_id': user.default_address_id
        }
        return render(request, 'place_order.html', context)
