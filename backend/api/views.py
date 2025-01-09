from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.generics import RetrieveAPIView
from .models import User,Dashboard, Stock, StockStatus, Portfolio
from .serializers import UserSerializer,DashboardSerializer, PortfolioSerializer
from django.http import JsonResponse

class UserListCreate(generics.ListCreateAPIView):
    """
    Handles listing all users and creating a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    """
    Handles retrieving a single user by ID.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginUser(APIView):
    """
    Handles user login by validating username and password.
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(RetrieveAPIView):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        try:
            dashboard = Dashboard.objects.get(user_id=user_id)
            serializer = self.get_serializer(dashboard)
            return Response(serializer.data)
        except Dashboard.DoesNotExist:
            # Return empty values if the dashboard does not exist
            empty_data = {
                "user": user_id,
                "invested_amount": 0.0,
                "current_stock_holding": 0.0,
                "profit_loss": "",
                "day_change": "",
                "portfolio_values": [],
                "stock_distribution_by_sector": {},
                "stock_distribution_by_company": {},
                "stock_holdings": [],
                "stock_suggestions": [],
            }
            return Response(empty_data, status=status.HTTP_200_OK)

class PortfolioView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        try:
            portfolio = Portfolio.objects.get(user_id=user_id)
            serializer = PortfolioSerializer(portfolio)
            return Response(serializer.data)
        except Portfolio.DoesNotExist:
            # Return empty values if the portfolio does not exist
            empty_data = {
                "user": user_id,
                "invested_amount": 0.0,
                "current_stock_holding": 0.0,
                "profit_loss": "",
                "profit_loss_value": "",
                "day_change": "",
                "stock_holding_details": [],
                "cumulative_return_ytd": "",
                "cumulative_return_1yr": "",
                "cumulative_return_5yr": "",
                "risk_level_indicator": 0.0,
                "std": 0.0,
                "beta_coeffecient": 0.0,
                "var": 0.0,
                "market_sensitivity": "",
                "impact": "",
                "top_stocks": [],
                "worst_stocks": [],
                "transaction_history": [],
            }
            return Response(empty_data, status=status.HTTP_200_OK)

def get_all_stocks(request):
    stocks = list(Stock.objects.values())
    return JsonResponse(stocks, safe=False)

def get_stock_by_symbol(request, stock_symbol):
    try:
        stock_symbol = stock_symbol.upper()
        stock = Stock.objects.get(stock_symbol=stock_symbol)
        return JsonResponse({
            "id": stock.id,
            "stock_symbol": stock.stock_symbol,
            "stock_name": stock.stock_name,
            "sector": stock.sector
        })
    except Stock.DoesNotExist:
        return JsonResponse({"error": "Stock not found"}, status=404)

def get_all_sectors(request):
    sectors = Stock.objects.values_list('sector', flat=True).distinct()
    return JsonResponse(list(sectors), safe=False)

def get_all_stock_statuses(request):
    stocks_statuses = list(StockStatus.objects.values())
    return JsonResponse(stocks_statuses, safe=False)

from django.shortcuts import render
from django.http import JsonResponse
from api.models import Stock, StockStatus

def get_stock_status_for_symbol(request, stock_symbol):
    try:
        stock_symbol = stock_symbol.upper()
        # Find the stock with the given stock_symbol
        stock = Stock.objects.get(stock_symbol=stock_symbol)

        # Fetch all related StockStatus objects for the found stock
        stock_statuses = StockStatus.objects.filter(stock=stock)

        # Prepare the response data (you can modify the structure as needed)
        stock_status_data = []
        for status in stock_statuses:
            stock_status_data.append({
                'date': status.date,
                'close_price': status.close_price,
                'change_value': status.change_value,
                'change_percent': status.change_percent,
                'open_price': status.open_price,
                'high': status.high,
                'low': status.low,
                'volume': status.volume,
                'circuit_breaker': status.circuit_breaker,
                'day_range': status.day_range,
                'fifty_two_week_range': status.fifty_two_week_range,
                'ask_price': status.ask_price,
                'ask_volume': status.ask_volume,
                'bid_price': status.bid_price,
                'bid_volume': status.bid_volume,
                'ldcp': status.ldcp,
                'var': status.var,
                'haircut': status.haircut,
                'pe_ratio': status.pe_ratio,
                'one_year_change': status.one_year_change,
                'ytd_change': status.ytd_change
            })

        # Return the data as a JSON response
        return JsonResponse({'stock_statuses': stock_status_data}, safe=False)

    except Stock.DoesNotExist:
        # If stock with the given symbol does not exist
        return JsonResponse({'error': f'Stock with symbol {stock_symbol} not found'}, status=404)
