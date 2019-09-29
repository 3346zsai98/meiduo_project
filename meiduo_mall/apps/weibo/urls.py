from django.conf.urls import url
from . import views

urlpatterns = [
    # 微博登陆页面
    url(r'^sina/login/$', views.SiNaLogin.as_view()),
    # 回调
    url(r'^sina_callback/$', views.SiNaCallback.as_view()),
    # 提交登陆
    url(r'^oauth/sina/user/$', views.SiNaUser.as_view()),
]
