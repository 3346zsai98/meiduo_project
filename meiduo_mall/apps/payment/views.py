import os

from alipay import AliPay
from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.carts.models import OrderInfo
from apps.orders.models import Payment
from utils.response_code import RETCODE


# 保存订单支付结果
class PaymentStatusView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.接收　查询参数
        params_query_dict = request.GET

        # 2.类型强制转换---queryDict---->()
        data = params_query_dict.dict()
        # 3. pop('sign')
        signature = data.pop('sign')
        # 4. 支付宝二次校验
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        success = alipay.verify(data, signature)
        if success:
            # 5. 获取订单号　支付宝交易号码　－－持久化　－表　create()
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')

            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 6. 修改订单的状态－－待支付--->待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT']
            )
        # 7. 返回响应
            context = {
                'trade_id': trade_id
            }
        else:
            context = {
                'trade_id': '有内鬼，支付失败'
            }
        return render(request, 'pay_success.html', context)

class PaymentView(LoginRequiredMixin, View):
    def get(self,request, order_id):
        # 查询要支付的订单
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 生成登陆支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='美多商城%s' % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )
        # 响应登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' +order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
