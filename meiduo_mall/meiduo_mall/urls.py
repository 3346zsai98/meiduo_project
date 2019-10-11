"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include('apps.users.urls', namespace='users')),
    # 2.首页
    url(r'^', include('apps.contents.urls', namespace='contents')),
    # 3.图形验证码
    url(r'^', include('apps.verifications.urls', namespace='verifications')),
    # 4.QQ登陆
    url(r'^', include('apps.oauth.urls', namespace="qq")),
    # 5.城市数据
    url(r'^', include('apps.areas.urls', namespace="areas")),
    # 6.商品列表
    url(r'^', include('apps.goods.urls', namespace="goods")),
    # 7.购物车
    url(r'^', include('apps.carts.urls', namespace='carts')),
    # 8.订单
    url(r'^', include('apps.orders.urls', namespace='orders')),
    # 9.支付
    url(r'^', include('apps.payment.urls', namespace='payment')),
    # 10. 搜索
    url(r'^search/', include('haystack.urls')),
    # 11.　微博登陆
    url(r'^', include('apps.weibo.urls', namespace='weibo')),

    # 后台
    url(r'^meiduo_admin/', include('apps.meiduo_admin.urls')),

]
