from django.urls import path, include
from .views import index, by_category, PpRegisterView, profile,PpLoginView,\
    PpLogoutView,RegisterUserDone,ChangeUserInfo,DeleteUser, detail,profile_pp_add,RegistrationAPIView,LoginAPIView,\
    profile_pp_change, profile_pp_delete,user_tips, user_tips_delete, ProductViewSet, ProductDetailApi, ProductListApi, \
    TipProductApi, TipProductViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('products',ProductViewSet)

router.register('tip_product',TipProductViewSet)
app_name = 'main'

urlpatterns = [
    path('api/',include(router.urls)),
    path('api/product_detail/',ProductListApi.as_view(),name='products_detail'),
    path('api/product_detail/<int:category_pk>/<int:pk>/',ProductDetailApi.as_view(),name='product_detail'),
    path('api/tip/product/<str:name>/',TipProductApi.as_view(),name='products_detail'),
    path('registration/', RegistrationAPIView.as_view(), name='user_registration'),
    path('login/', LoginAPIView.as_view(), name='user_login'),
    path('accounts/register/',PpRegisterView.as_view(),name='register'),
    path('accounts/register/done/',RegisterUserDone.as_view(),name='register_done'),
    path('', index, name='index'),
    path('<int:category_pk>/<int:pk>/',detail,name='detail'),
    path('<int:pk>/',by_category,name='by_category'),
    path('accounts/login/',PpLoginView.as_view(),name='login'),
    path('accounts/profile/add/product/',profile_pp_add,name='profile_pp_add'),
    path('accounts/profile/change/product/<int:pk>',profile_pp_change,name='profile_pp_change'),
    path('accounts/profile/delete/product/<int:pk>',profile_pp_delete,name='profile_pp_delete'),
    path('accounts/logout/',PpLogoutView.as_view(),name='logout'),
    path('accounts/profile/',profile,name='profile'),
    path('accounts/profile/tips/',user_tips,name='user_tips'),
    path('accounts/profile/tips/delete/<int:pk>',user_tips_delete,name='user_tips_delete'),
    path('accounts/profile/change/',ChangeUserInfo.as_view(),name='change_user'),
    path('accounts/profile/delete/',DeleteUser.as_view(),name='delete_user'),




]