from django.urls import path
from .views import LoginUser, RegisterUser, detail_user, logout_user, user_orders

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('sign_up/', RegisterUser.as_view(), name='register'),
    path('area/', detail_user, name='detail_user'),
    path('logout/', logout_user, name='logout'),
    path('orders/', user_orders, name='orders')
]