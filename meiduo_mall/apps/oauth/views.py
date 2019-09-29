from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from pymysql import DatabaseError

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE


# 判断是否绑定openid
def is_bind_openid(openid, request):
    # 判断 openid 在不在 QQ等录表OAuthQQUser
    try:
        qq_user = OAuthQQUser.objects.get(openid=openid)
    except OAuthQQUser.DoesNotExist:
        # 不存在--跳转到 绑定页面
        context = {'openid': openid}
        response = render(request, 'oauth_callback.html', context)
    else:
        # 存在
        user = qq_user.user
        # 1.保持登录装填
        login(request, user)
        # 2. cookie保存用户名
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=14 * 2 * 24 * 3600)

        # 3. 重定向首页
    return response


# 2.用户扫码登陆的回调处理
class QQAuthUserView(View):
    def get(self, request):
        """
        Oauth2.0认证
        :param request:
        :return:
        """
        # 提取code请求参数
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少参数')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        # 使用code向QQ服务器请求access_token
        access_token = oauth.get_access_token(code)

        # 使用access_token向QQ服务器请求openid
        openid = oauth.get_open_id(access_token)

        # 4. 判断是否绑定openid
        response = is_bind_openid(openid, request)

        return response

    def post(self, request):
        # 1.接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        # 2. 正则校验

        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 3. 判断 手机号 --存不存在
        # 存在的额=---密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:

            # 不存在--新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:

            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        try:
            # 4.绑定openid 操作OAuthQQUser表--新建数据
            OAuthQQUser.objects.create(user=user, openid=openid)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 1.保持登录装填
        login(request, user)
        # 2. cookie保存用户名
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=14 * 2 * 24 * 3600)
        # 合并购物车
        merge_cart_cookie_to_redis(request=request, response=response)
        # 5.返回首页
        return response


# 1.QQ登陆页面
class QQAuthURLView(View):
    """
        提供QQ登录页面网址
        https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    """
    def get(self, request):
        next = request.GET.get('next')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
