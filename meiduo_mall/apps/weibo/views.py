import json

from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse

from django.views import View

from apps.users.models import User
from apps.weibo.models import OAuthSinaUser
from utils import sinaweibopy3


# 微博登陆页面
from utils.response_code import RETCODE
from utils.secret import SecretOauth


# 绑定用户提交
class SiNaUser(View):
    def post(self, request):

        json_dict = json.loads(request.body.decode())

        mobile = json_dict.get('mobile')
        pwd = json_dict.get('password')
        sms_code = json_dict.get('sms_code')
        # uid = SecretOauth.loads(json_dict.get('uid'))
        uid = json_dict.get('uid')

        if not uid:
            return render(request, 'sina_callback.html', {'uid_errmsg': '无效的uid'})

        from django_redis import get_redis_connection
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get("sms_%s" % mobile)

        if redis_code is None:
            return render(request, 'sina_callback.html', {'sms_code_errmsg': '无效的短信验证码'})

        if sms_code != redis_code.decode():
            return render(request, 'sina_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})


        # 保存注册数据
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 如果用户存在，检查用户密码
            if not user.check_password(pwd):
                return render(request, 'sina_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 绑定用户
        OAuthSinaUser.objects.create(
            uid=uid,
            user=user,
        )

        # 保持登录状态
        login(request, user)
        response = http.JsonResponse({'status': 5000})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


# 微博登陆回调
class SiNaCallback(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少参数')
        client = sinaweibopy3.APIClient(
            # app_key： app_key值
            app_key=settings.APP_KEY,
            # app_secret：app_secret 值
            app_secret=settings.APP_SECRET,
            # redirect_uri ： 回调地址
            redirect_uri=settings.REDIRECT_URL,
        )
        result = client.request_access_token(code)
        access_token = result.access_token
        uid = result.uid

        try:
            sina_user = OAuthSinaUser.objects.get(uid=uid)
        except OAuthSinaUser.DoesNotExist:
            # uid = SecretOauth().dumps({'uid': uid})
            return render(request, 'sina_callback.html', context={'uid': uid})

        user = sina_user.user

        login(request, user)

        response = redirect(reverse('contents:index'))
        # response = http.JsonResponse({'status': 5000})
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response

# 跳转到微博登陆页面
class SiNaLogin(View):
    """
    APP_KEY='3305669385'
    APP_SECRET='74c7bea69d5fc64f5c3b80c802325276'
    REDIRECT_URL='http://www.meiduo.site:8000/sina_callback'
    """
    def get(self, request):
        client = sinaweibopy3.APIClient(
            # app_key： app_key值
            app_key=settings.APP_KEY,
            # app_secret：app_secret 值
            app_secret=settings.APP_SECRET,
            # redirect_uri ： 回调地址
            redirect_uri=settings.REDIRECT_URL,
        )
        login_url = client.get_authorize_url()

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": 'OK', "login_url": login_url})
