from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
import re

from apps.users.models import User


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供注册界面
        :param request: 请求对象
        :return: 注册界面
        """
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        pic_code = request.POST.get('pic_code')
        msg_code = request.POST.get('msg_code')
        allow = request.POST.get('allow')

        # 判断是否为空
        if not all([username, password, password2, mobile, pic_code, msg_code]):
            return render(request, 'register.html', {'register_message': '缺少参数'})

        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return render(request, 'register.html', {'register_message': '请输入5-20个字符的用户名'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return render(request, 'register.html', {'register_message': '请输入8-20位的密码'})
        # 判断两次密码是否一致
        if password != password2:
            return render(request, 'register.html', {'register_message': '两次输入的密码不一致'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return render(request, 'register.html', {'register_message': '请输入正确的手机号码'})
        # 判断是否勾选用户协议
        if allow != 'on':
            return render(request, 'register.html', {'register_message': '请勾选用户协议'})
        # 判断密码是否一致
        if password != password2:
            return render(request, 'register.html', {'register_message': '两次密码不一致，请重新输入'})
        try:
                user = User.objects.get(mobile=mobile)

        except:
            pass
        else:
            if user:
                return render(request, 'register.html', {'register_message': '该手机号已经被注册'})

        # 判断用户名是否被注册
        try:
            user = User.objects.get(username=username)
        except:
            pass
        else:
            if user:
                return render(request, 'register.html', {'register_message': '该用户名已经被注册'})

        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        user.save()

        login(request, user)
        return redirect(reverse('goods:index'))