from django.conf.urls import url
from . import views

urlpatterns = [
    # 购物车增删改查
    url(r'^carts/$', views.CartsView.as_view(), name='carts'),
    # 全选购物车
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view(), name='selectall'),
    # 首页简单购物车展示
    url(r'^carts/simple/$', views.CartsSimpleView.as_view(), name='simple'),
]