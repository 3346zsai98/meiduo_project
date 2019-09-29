from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 判断用户名是否重复　usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view(), name='usernames'),
    # 判断手机号是否重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view(), name='mobiles'),
    # 登陆
    url(r'^login/', views.LoginView.as_view(), name='login'),
    # 退出登陆
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    # 判断用户是否登陆
    url(r'^info/', views.UserInfoView.as_view(), name='info'),
    # 保存邮箱
    url(r'^emails/', views.EmailView.as_view(), name='email'),
    # 激活邮箱  emails/verification/
    url(r'^emails/verification/$', views.EmailVerifyView.as_view(), name="verify"),
    # 展示收货地址　address
    url(r'^address/$', views.AddressView.as_view(), name="address"),
    # 增加收货地址　address/create
    url(r'^addresses/create/$', views.AddressAddView.as_view(), name="addressAdd"),
    # 修改删除收货地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(), name="addressUpdate"),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name="addressAdd"),
    # 修改地址标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.DefaultAddressView.as_view(), name="addressAdd"),
    # 修改密码
    url(r'^password/$', views.ChangePasswordView.as_view(), name="password"),
    # 保存查询浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view(), name="password"),

    # 忘记密码首页展示
    url(r'^find_password/$', views.FindPassword.as_view()),
    # 忘记密码用户查询
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.FindUser.as_view()),
    # 忘记密码短信发送
    url(r'^find_password_sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.GetCode.as_view()),
    # 短信发送成功提交
    url(r'^accounts/(?P<mobile>[a-zA-Z0-9_-]{5,20})/password/token/$', views.TiJiao.as_view()),
    # 新密码
    url(r'^users/(?P<user_id>\d+)/new_password/$', views.NewPwd.as_view()),


]
