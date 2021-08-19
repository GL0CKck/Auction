from django.urls import path
from cart.views import *


app_name = 'cart'

urlpatterns = [
    path('',views.cart_detail,name='cart_detail'),
    path('add/<int:pk>/',views.cart_add,name='cart_add'),
    path('remove/<int:pk>/',views.cart_remove,name='cart_remove'),
]