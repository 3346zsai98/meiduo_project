from django.conf.urls import url
from . import views

urlpatterns = [
    # 首页
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='qqlogin'),

    # 回调
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view()),
]