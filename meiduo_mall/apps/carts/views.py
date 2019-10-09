import http
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods import models
from apps.goods.models import SKU
from utils.cookiesecret import CookieSecret
from utils.response_code import RETCODE

# 展示简单购物车
class CartsSimpleView(View):
    def get(self, request):
        # 判断用户是否登陆
        user = request.user
        if user.is_authenticated:
            # 用户已登陆，查询Redis购物
            carts_redis_client = get_redis_connection('carts')
            carts_data = carts_redis_client.hgetall(user.id)
            # 转换格式
            cart_dict = {int(key.decode()): json.loads(value.decode()) for key,value in carts_data.items()}
        else:
            # 用户未登陆，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}

        # 构造简单购物车JSON数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })

        # 响应json列表数据
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})


# 全选购物车
class CartsSelectAllView(View):
    """全选购物车"""
    def put(self, request):
        # 接收和校验参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登陆
        user = request.user
        if user.is_authenticated:
            # 用户已经登陆，操作redis购物车
            carts_redis_client = get_redis_connection('carts')
            carts_data = carts_redis_client.hgetall(user.id)

            # 将所有商品的选中状态修改
            for key, value in carts_data.items():
                sku_id = int(key.decode())
                carts_dict = json.loads(value.decode())

                # 修改所有商品的选中状态
                carts_dict['selected'] = selected

                carts_redis_client.hset(user.id, sku_id, json.dumps(carts_dict))
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
        else:
            # 用户未登陆，操作cookie购物车
            carts_str = request.COOKIES.get('carts')
            response = JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            if carts_str is not None:
                carts_dict = CookieSecret.loads(carts_str)
                for sku_id in carts_dict:
                    carts_dict[sku_id]['selected'] = selected
                    cookie_cart = CookieSecret.dumps(carts_dict)
                    response.set_cookie('carts', cookie_cart, 24*30*3600)

            return response


# 购物车增删改查
class CartsView(View):
    """购物车管理"""

    # 添加购物车
    def post(self, request):

        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            # 3.1　登陆　使用redis存储
            carts_redis_client = get_redis_connection('carts')

            # 3.2 获取以前数据库的数据
            client_data = carts_redis_client.hgetall(user.id)

            # 如果商品已经存在就更新数据
            if str(sku_id).encode() in client_data:
                # 根据sku_id取出商品
                child_dict = json.loads(client_data[str(sku_id).encode()].decode())
                # 个数累加
                child_dict['count'] += count
                # 更新数据
                carts_redis_client.hset(user.id, sku_id, json.dumps(child_dict))
            else:
                # 如果商品不存在,直接增加商品到数据
                carts_redis_client.hset(user.id, sku_id, json.dumps({'count': count, 'selected': selected}))
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        else:
            # 用户未登录，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            # 如果用户操作过cookie购物车
            if cart_str:
                # 解密出明文
                cart_dict = CookieSecret.loads(cart_str)
            else: #用户没有操作过cookie购物车
                cart_dict = {}

            # 判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
            if sku_id in cart_dict:
                # 累加求和
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            # 转成密文
            cookie_cart_str = CookieSecret.dumps(cart_dict)

            # 创建响应对象
            response = JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=24 * 30 * 3600)
            return response

    # 修改购物车
    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')
        # 判断count是否是数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 判断selected是否是bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登陆
        user = request.user
        # 接收cookie最后的数据
        cookie_cart_str = ''
        if user.is_authenticated:
            # 用户已登陆，修改redis购物车
            # 1.链接　redis
            carts_redis_client = get_redis_connection('carts')
            # 2.覆盖redis以前的数据
            new_data = {'count': count, 'selected': selected}
            carts_redis_client.hset(user.id, sku_id, json.dumps(new_data))
        else:
            # 用户未登陆，修改cookie购物车
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = CookieSecret.loads(carts_str)
            else:
                cart_dict = {}
            # 覆盖以前的数据
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 转换成 密文数据
            cookie_cart_str = CookieSecret.dumps(cart_dict)

        # 构建前端的数据
        cart_sku = {
            'id': sku_id,
            'count': count,
            'selected': selected,
            'name': sku.name,
            'default_image_url': sku.default_image.url,
            'price': sku.price,
            'amount': sku.price * count,
        }
        respose = JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        if not user.is_authenticated:
            # 响应结果并将购物车数据写入到cookie
            respose.set_cookie('carts', cookie_cart_str, max_age=24 * 30 * 3600)
        return respose

    # 删除购物车
    def delete(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden("商品不存在")

        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登陆，删除redis购物车
            carts_redis_client = get_redis_connection('carts')

            carts_redis_client.hdel(user.id, sku_id)

            # 删除结束后，没有响应的数据，只需要响应状态码即可
            return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            # 用户未登陆，删除cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 转成明文
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}

            # 创建响应对象
            response = JsonResponse({'code': RETCODE.OK, 'errmsg': "删除购物车成功"})
            if sku_id in cart_dict:
                # 删除数据
                del cart_dict[sku_id]
                # 将字典转成密文
                cookie_cart_str = CookieSecret.dumps(cart_dict)
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('carts', cookie_cart_str, max_age=24 * 30 * 3600)
            return response

    # 展示购物车
    def get(self, request):
        """展示购物车"""
        user = request.user
        if user.is_authenticated:
            # 1.用户已经登陆,查询redis购物车
            carts_redis_client = get_redis_connection('carts')

            # 2.获取当前用户的　所有购物车数据
            carts_data = carts_redis_client.hgetall(request.user.id)

            # 3.转换格式-->和cookie一样的字典　方便后面构建数据
            carts_dict = {}
            for key, value in carts_data.items():
                sku_id = int(key.decode())
                sku_dict = json.loads(value.decode())
                carts_dict[sku_id] = sku_dict
            # carts_dict = {int(key.decode()):json.loads(value.decode()) for key, value in carts_data.items()}
        else:
            # 用户未登陆，查询cookies购物车
            cookie_str = request.COOKIES.get('carts')
            if cookie_str:
                carts_dict = CookieSecret.loads(cookie_str)
            else:
                carts_dict = {}

        sku_ids = carts_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus': cart_skus,
        }

        # 渲染购物车页面
        return render(request, 'cart.html', context)


