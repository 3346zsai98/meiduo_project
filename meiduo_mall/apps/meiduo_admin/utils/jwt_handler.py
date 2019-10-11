# from rest_framework_jwt.utils import jwt_response_payload_handler
from rest_framework_jwt.utils import jwt_payload_handler
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
    }

def meiduo_payload_handler(user):
    # 重用某个方法中的代码，则调用这个方法执行
    payload = jwt_payload_handler(user)

    # 删除邮箱
    del payload['email']

    # 添加手机号
    payload['mobil']=user.mobile

    return payload