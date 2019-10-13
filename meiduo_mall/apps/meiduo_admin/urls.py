from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.views import spuzsg
from apps.meiduo_admin.views import specs
from apps.meiduo_admin.views import statistical
from apps.meiduo_admin.views import users
from rest_framework.routers import DefaultRouter
urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    # 1.用户总数统计
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    # 2.用户日增统计
    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    # 3.日活跃统计
    url(r'^statistical/day_active/$', statistical.UserActiveCountView.as_view()),
    # 4.日下单用户统计
    url(r'^statistical/day_orders/$', statistical.UserOrderCountView.as_view()),
    # 5.月增用户统计
    url(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    # 6.日分类商品统计
    url(r'^statistical/goods_day_views/$', statistical.GoodsDayView.as_view()),

    # 用户管理
    # 1.获取查询用户
    url(r'^users/$', users.UserView.as_view()),
    # 2.保存规格表数据
    url('^goods/simple/$', spuzsg.SPUSimpleViewSet.as_view()),

]

router = DefaultRouter()
router.register('goods/specs', specs.SpecsViewSet, base_name='specs')
urlpatterns += router.urls
