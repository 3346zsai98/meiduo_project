import json
from django_redis import get_redis_connection
from utils.cookiesecret import CookieSecret
def merge_cart_cookie_to_redis(request, response):
    """
    登录后合并cookie购物车数据到Redis
    :param request: 本次请求对象，获取cookie中的数据
    :param response: 本次响应对象，清除cookie中的数据
    :return: response
    """
    # 1. cookie_dict
    cookie_str = request.COOKIES.get('carts')

    if cookie_str is not None:
        # 2.解密
        cookie_dict = CookieSecret.loads(cookie_str)
        # 3.链接redis数据库
        client = get_redis_connection('carts')
        # 4. 覆盖redis的数据
        for sku_id in cookie_dict:
            client.hset(request.user.id, sku_id, json.dumps(cookie_dict[sku_id]))

        # 5. 删除cookie
        response.delete_cookie('carts')