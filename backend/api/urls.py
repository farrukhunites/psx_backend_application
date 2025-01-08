from django.urls import path
from . import views

urlpatterns = [
    path("user/", views.UserListCreate.as_view(), name="user_list_create"),  
    path("user/<int:pk>/", views.UserDetail.as_view(), name="user_detail"),  
    path("user/login/", views.LoginUser.as_view(), name="login_user"),
    path("user/<int:pk>/dashboard/", views.DashboardView.as_view(), name="user_dashboard"),

    path('stocks/', views.get_all_stocks, name='get_all_stocks'),
    path('stocks/<str:stock_symbol>/', views.get_stock_by_symbol, name='get_stock_by_symbol'),
    path('sectors/', views.get_all_sectors, name='get_all_sectors'),

]
