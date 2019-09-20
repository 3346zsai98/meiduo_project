from django.conf.urls import url

from . import views

urlpatterns = [
    # 首页
    url(r'^areas/$', views.AreasView.as_view()),
]