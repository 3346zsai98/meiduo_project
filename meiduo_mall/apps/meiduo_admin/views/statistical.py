from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta

from apps.goods.models import GoodsVisitCount
from apps.meiduo_admin.serializers.statistical import GoodsSerializer
from apps.users.models import User


# 1.用户总数统计
class UserTotalCountView(APIView):
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()

        # 获取用户数量
        count = User.objects.filter(is_staff=False).count()
        dict = {
            'date': now_date,
            'count': count
        }
        return Response(dict)


# 2.日增用户统计
class UserDayCountView(APIView):
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 查询当前日期
        now_date = date.today()

        # 获取当日注册用户数量 date_joined 记录创建账户时间
        count = User.objects.filter(is_staff=False, date_joined__gte=now_date).count()
        return Response({
            'date': now_date,
            'count': count
        })


# 3.日活跃统计
class UserActiveCountView(APIView):
    # 设置管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前时间
        now_date = date.today()

        # 获取当日登录用户数量  last_login记录最后登录时间
        count = User.objects.filter(is_staff=False, last_login__gte=now_date).count()
        return Response({
            "count": count,
            "date": now_date
        })


# 4.日下单用户统计
class UserOrderCountView(APIView):
    # 设置管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前时间
        now_date = date.today()

        # 获取当日下单用户数量  orders__create_time 订单创建时间
        count = User.objects.filter(orders__create_time__gte=now_date).distinct().count()
        return Response({
            "count": count,
            "date": now_date
        })


# 5.月增用户统计
class UserMonthCountView(APIView):
    # 设置管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取一个月前日期
        start_date = now_date - timedelta(29)
        # 创建空列表保存每天的用户量
        date_list = []

        for i in range(30):
            # 循环遍历获取当天日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天日期
            cur_date = start_date + timedelta(days=i + 1)
            # 查询条件是大于当前日期index_date，小于明天日期的用户cur_date，得到当天用户量
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date
            })

        return Response(date_list)


# 6.日分类商品统计
class GoodsDayView(ListAPIView):

    # def get(self, request):　继承自APIView
    #     # 获取当天日期
    #     now_date = date.today()
    #     # 获取当天访问的商品分类数量信息
    #     data = GoodsVisitCount.objects.filter(date=now_date)
    #     # 序列化返回分类数量
    #     ser = GoodsSerializer(data, many=True)
    #
    #     return Response(ser.data)
    # 模型类查询集
    queryset = GoodsVisitCount.objects.filter(date=date.today())
    # 指定序列化器
    serializer_class = GoodsSerializer
