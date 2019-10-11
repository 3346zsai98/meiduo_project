from django.conf import settings
from django.contrib.auth.backends import ModelBackend
import re

from apps.users.models import User



def get_user_by_account(account):
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 手机号登陆
            user = User.objects.get(mobile=account)
        else:
            # 用户名登陆　
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


# 生成邮箱验证连接的函数
def generate_verify_email_url(user):
    """
    :param user: 用户对象
    :return:
    """
    host_url = settings.EMAIL_ACTIVE_URL
    # 1.加密的数据
    data_dict = {'user_id': user.id,"email": user.email}

    # 2. 进行加密数据
    from utils.secret import SecretOauth
    secret_data = SecretOauth().dumps(data_dict)

    # 3. 返回拼接url
    verify_url = host_url + '?token=' + secret_data
    return verify_url


class UsernameMobileAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 区分是前台调用登录还是后台调用登录
        # if 'meiduo_admin/' in request.path:
        #     pass # 后台
        # else:
        #     pass # 前台

        if request is None:
            # 后台：jwt调用时未传递request对象
            try:
                # 查询指定用户名，并且是管理员
                user = User.objects.get(username=username)
            except:
                return None
            else:
                # 判断密码是否正确
                if user.check_password(password):
                  return user
                else:
                    return None

        else:
            # 前台：调用时传递request对象

            # 根据传入的username获取user对象。username可以是手机号也可以是用户名
            user = get_user_by_account(username)

            # 校验user是否存在并校验密码是否正确
            if user and user.check_password(password):
                return user
            else:
                return None
