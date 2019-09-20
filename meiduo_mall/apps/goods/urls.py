from django.conf.urls import url
from . import views

urlpatterns = [
    # 首页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/?$', views.QQAuthURLView.as_view()),

]