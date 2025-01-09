from django.urls import path
from . import views
from .dashboard.views import DashboardView
from .portfolio.views import PortfolioView
from .pdf_extract.views import PdfExtractView

urlpatterns = [
    path("user/", views.UserListCreate.as_view(), name="user_list_create"),  
    path("user/<int:pk>/", views.UserDetail.as_view(), name="user_detail"),  
    path("user/login/", views.LoginUser.as_view(), name="login_user"),

    path("user/<int:user_id>/dashboard/", DashboardView.as_view(), name="user_dashboard"),

    path('portfolio/<int:user_id>/', PortfolioView.as_view(), name='portfolio-detail'),

    path('stocks/', views.get_all_stocks, name='get_all_stocks'),
    path('stocks/<str:stock_symbol>/', views.get_stock_by_symbol, name='get_stock_by_symbol'),
    path('sectors/', views.get_all_sectors, name='get_all_sectors'),

    path('stock-statuses/', views.get_all_stock_statuses, name='get_all_stock_statuses'),
    path('stock-statuses/<str:stock_symbol>/', views.get_stock_status_for_symbol, name='get_stock_detail_by_symbol'),

    path('transaction/add/<int:user_id>/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:user_id>/', views.transaction_history, name='transaction_history'),

    path('latest-stock-status/<str:stock_symbol>/', views.LatestStockStatus.as_view(), name='latest-stock-status'),

    path('watchlist/', views.WatchlistListAPIView.as_view(), name='watchlist-list'),
    path('watchlist/create/', views.WatchlistCreateAPIView.as_view(), name='watchlist-create'),
    path('watchlist/delete/', views.WatchlistDeleteAPIView.as_view(), name='watchlist-delete'),

    path('alerts/create/', views.AlertCreateAPIView.as_view(), name='alert-create'),
    path('alerts/', views.AlertListAPIView.as_view(), name='alert-list'),
    path('alerts/delete/', views.AlertDeleteAPIView.as_view(), name='alert-delete'),

     path('pdf-extract/', PdfExtractView.as_view()),

]
