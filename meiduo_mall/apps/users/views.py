import json
from django import http
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
import re

from django_redis import get_redis_connection

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.goods import models
from apps.goods.models import SKU
from apps.users.models import User, Address

from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE
from utils.secret import SecretOauth


# 13.5 新密码
class NewPwd(View):
    def post(self, request, user_id):
        json_dict = json.loads(request.body.decode())
        password = json_dict.get('password')
        password2 = json_dict.get('password2')
        access_token = json_dict.get('access_token')
        if access_token != 'zxc':
            return JsonResponse({'status': 5001, 'message': 'token有错'})
            # 判断密码是否为空
        if not all([password, password2, access_token]):
            return http.HttpResponseForbidden("参数不能为空")
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse('请输入8-20个数字或字母')
        # 判断两次密码是否一致
        if password != password2:
            return JsonResponse('请输入8-20个数字或字母')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 5002, 'message': 'user_id有错'})

        user.set_password(password)
        user.save()

        return JsonResponse({'status': 5000, 'message': '修改密码成功'})


# 13.4 短信提交
class TiJiao(View):
    def get(self, request, mobile):
        sms_code = request.GET.get('sms_code')
        access_token = 'zxc'
        from django_redis import get_redis_connection
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get("sms_%s" % mobile)

        if not mobile:
            return JsonResponse({'status': 5004})
        if sms_code != redis_code.decode():
            return JsonResponse({'status': 5001})
        user = User.objects.get(mobile=mobile)

        return JsonResponse({"status": 200, 'user_id': user.id, 'access_token': access_token})


# 13.3 发送短信
class GetCode(View):
    def get(self, request, mobile):
        access_token = request.GET.get('access_token')
        if access_token != 'zxc':
            return JsonResponse({'status': 5001, 'message': 'token错误'})
        from random import randint
        sms_code = "%06d" % randint(0, 999999)
        sms_redis_client = get_redis_connection('sms_code')
        sms_redis_client.setex("sms_%s" % mobile, 300, sms_code)

        # 4.让第三方 容联云-给手机号-发送短信
        #                        手机号           验证码  过期时间5分钟 ,类型默认1
        #  CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        print("当前验证码是:", sms_code)
        return JsonResponse({'status': 5000, 'message': '短信发送成功', "access_token": access_token},)


# 13.2 忘记密码验证用户
class FindUser(View):
    def get(self, request, username):
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 判断用户是否存在
        try:
            user = User.objects.get(username=username)
        except:
            return JsonResponse({'status': 5004})
        # 判断图形验证码是否正确
        # 根据uuid去redis数据库查询　图形验证码
        image_redis_client = get_redis_connection('verify_image_code')
        redis_img_code = image_redis_client.get('img_%s' % uuid)
        try:
            image_redis_client.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        if image_code.lower() != redis_img_code.decode().lower():
            return JsonResponse({'status': 5001})
        access_token = 'zxc'
        mobile = user.mobile
        return JsonResponse({'status': 5000, 'mobile': mobile, 'access_token': access_token})


# 13.1 忘记密码页面展示
class FindPassword(View):

    def get(self, request):

        return render(request, 'find_password.html')


    # 12.查询保存用户浏览记录


# 12. 用户浏览记录
class UserBrowseHistory(LoginRequiredMixin, View):
    """用户浏览记录"""

    def post(self, request):
        """保存用户浏览记录"""
        # 1.接收json参数
        sku_id = json.loads(request.body.decode()).get('sku_id')

        # 2.根据sku_id 查询sku
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('商品不存在!')

        # 3.如果有sku,保存到redis
        history_redis_client = get_redis_connection('history')
        history_key = 'history_%s' % request.user.id

        redis_pipeline = history_redis_client.pipeline()
        # 3.1 去重
        history_redis_client.lrem(history_key, 0, sku_id)
        # 3.2 存储
        history_redis_client.lpush(history_key, sku_id)
        # 3.3 截取 5个
        history_redis_client.ltrim(history_key, 0, 4)
        redis_pipeline.execute()

        # 响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)

        # 根据sku_ids列表数据，查询出商品sku信息
        skus = []
        for sku_id in sku_ids:
            sku = models.SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})


# 11.修改密码及显示
class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        # 展示修改密码页面
        return render(request, 'user_center_pass.html')
    def post(self, request):
        # 修改密码
        # 接收参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 校验密码是否正确
        result = request.user.check_password(old_password)
        # result 为false 密码不正确
        if not result:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response


# 13.修改地址标题
class UpdateTitleAddressView(LoginRequiredMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


# 12 设置默认地址
class DefaultAddressView(LoginRequiredMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


# 11.修改及删除收货地址
class UpdateDestroyAddressView(LoginRequiredMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


# 10.新增地址
class AddressAddView(LoginRequiredMixin, View):
    def post(self, request):
        # 限制增加个数 不能超过20个
        count = Address.objects.filter(user=request.user, is_deleted=False).count()
        # count = request.user.addresses.filter(is_deleted=False).count()
        if count > 20:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 1. 接收参数 form, json
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2.校验 判空 正则:


        # 3. orm = create() save()
        address = Address.objects.create(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email,
        )

        # 设置用户的默认地址
        if not request.user.default_address:
            request.user.default_address = address
            request.user.save()

        # 4.数据转换—>dict
        address_dict = {
            "id": address.id,
            "title": address.title,

            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


# 9 展示收货地址
class AddressView(View):
    def get(self, request):
        # 1.根据用户 查询所有地址  filter()
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # 2.转换前端的数据格式
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })

        context = {
            'default_address_id': request.user.default_address_id,
            'addresses': addresses_list
        }
        return render(request, 'user_center_site.html', context)


# 8.验证邮箱
class EmailVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.接收参数  request.GET
        token = request.GET.get('token')

        # 解密
        data_dict = SecretOauth().loads(token)

        user_id = data_dict.get('user_id')
        email = data_dict.get('email')

        # 2.校验
        try:
            user = User.objects.get(id=user_id, email=email)
        except Exception as e:
            print(e)
            return http.HttpResponseForbidden('token无效的!')

        # 3. 修改 email_active
        user.email_active = True
        user.save()

        # 4. 返回
        return redirect(reverse('users:info'))


# 7.保存邮箱
class EmailView(LoginRequiredMixin, View):
    """添加邮箱"""

    def put(self, request):
        """实现添加邮箱逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 赋值email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        # 4.异步发送邮件
        verify_url = 'http://www.itcast.cn'
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        # 响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 6.判断用户是否登陆
class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


# 5.用户退出登陆
class LogoutView(View):

    def get(self, request):
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = redirect(reverse('contents:index'))
        # 退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response


# 4.用户登陆
class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 1.接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2.校验参数
        if not all([username, password]):
            return HttpResponseForbidden('参数不齐全')
            # 2.1 用户名
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
            # 2.2 密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')

        # 3.验证用户名和密码--django自带的认证
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 4.保持登陆状态
        login(request, user)

        # 5.是否记住用户名
        if remembered != 'on':
            #　不记住用户名，浏览器结束会话就过期
            request.session.set_expiry(0)
        else:
            #　记住用户名，浏览器会话保持两周
            request.session.set_expiry(None)
        # 操作 next
        next = request.GET.get('next')

        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        response.set_cookie('username', user.username, max_age=3600*24*14)

        # 合并购物车
        merge_cart_cookie_to_redis(request=request, response=response)
        # 6.返回响应结果　
        return response


# 3.判断手机号是否重复
class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 2.判断用户名是否重复注册
class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 1.用户注册
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

        sms_code = request.POST.get('msg_code')

        from django_redis import get_redis_connection
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get("sms_%s" % mobile)

        if redis_code is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})

        if sms_code != redis_code.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 保存注册数据
        try:
            user = User.objects.get(username=username)
        except:
            pass
        # else:
        #     if user:
        #         return render(request, 'register.html', {'register_message': '该用户名已经被注册'})
        #
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        user.save()
        #　保持登陆状态
        login(request, user)
        # 重定向到首页
        return redirect(reverse('contents:index'))




