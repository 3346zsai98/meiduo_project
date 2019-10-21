from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.views import admin_user
from apps.meiduo_admin.views import admin_group
from apps.meiduo_admin.views import admin_permission
from apps.meiduo_admin.views import brands
from apps.meiduo_admin.views import category
from apps.meiduo_admin.views import channels
from apps.meiduo_admin.views import order
from apps.meiduo_admin.views import spu
from apps.meiduo_admin.views import spuzsg
from apps.meiduo_admin.views import specs
from apps.meiduo_admin.views import statistical
from apps.meiduo_admin.views import users
from apps.meiduo_admin.views import sku
from apps.meiduo_admin.views import image
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
    # 商品管理
    # 2.保存规格表数据
    url('^goods/simple/$', spuzsg.SPUSimpleViewSet.as_view()),
    # 3.三级分类查询
    url(r'^skus/categories/$', category.Category3View.as_view()),
    # 获取规格名称
    url(r'^goods/specs/simple/$', specs.SpucsSimpleView.as_view()),
    # 4.查询指定的spu规格和选项
    url('^goods/(?P<pk>\d+)/specs/$', specs.SpecOptionView.as_view()),

    # 图片管理
    # 图片创建中SKU的id 的查询
    url('^skus/simple/$', image.ImageSkuSimpleView.as_view()),
    # 系统管理－组管理－查询
    url('^permission/simple/$', admin_permission.PermissionSimpleView.as_view()),
    # 系统管理－管理员管理
    url('^permission/groups/simple/$', admin_group.GroupSimpleView.as_view()),
    # spu保存的相关操作
    # 品牌查询
    url('^goods/brands/simple/$', spu.SpuDetailView.as_view()),
    # category23查询
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spu.SPUC23View.as_view()),
    # category1查询
    url('^goods/channel/categories/$', spu.SpuC1View.as_view()),
    url('^goods/categories/$', spu.SpuC1View.as_view()),
    # 频道管理的频道组查询
    url('^goods/channel_types/$', channels.ChannelTypeView.as_view()),



]

router = DefaultRouter()
# 规格表管理
router.register('goods/specs', specs.SpecsViewSet, base_name='specs')
# 图片管理
router.register('skus/images', image.ImageViewSet, base_name='images')
# sku表管理
router.register('skus', sku.SkuViewSet, base_name='skus')
# 订单管理
router.register('orders', order.OrderViewSet, base_name='orders')
# 系统－权限管理
router.register('permission/perms', admin_permission.PermissionViewSet, base_name='permission')
# 系统－组管理
router.register('permission/groups', admin_group.GroupViewSet, base_name='group')
# 系统－管理员管理
router.register('permission/admins', admin_user.UserViewSet, base_name='admin')
# 图片表管理
router.register('goods/brands', brands.BrandsViewSet, base_name='brands')
# 频道表管理
router.register('goods/channels', channels.ChannelsViewSet, base_name='channels')
# SPU表数据获取
router.register('goods', spu.SpuViewSet, base_name='spu')
# 规格选项表操作
router.register('specs/options', specs.SpecsOptViewSet, base_name='guigexx')

urlpatterns += router.urls
