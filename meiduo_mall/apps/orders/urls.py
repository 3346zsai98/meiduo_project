from django.conf.urls import url
from . import views

urlpatterns = [
    # 订单
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),
    # 保存订单
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
    # 提交订单成功
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),
    # 我的订单展示
    url(r'^orders/info/(?P<page_num>\d+)/$', views.OrderMy.as_view()),
    # 评价订单页面展示
    url(r'^orders/comment/$', views.OrderComment.as_view()),
    # 展示评价信息
    url(r'^comments/(?P<sku_id>\d+)/$', views.OrderComments.as_view()),

]