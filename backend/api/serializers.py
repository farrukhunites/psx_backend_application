from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Dashboard, Portfolio, StockStatus, Watchlist, Alert


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'date_created', 'risk_preference']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = [
            'user',
            'invested_amount',
            'current_stock_holding',
            'profit_loss',
            'day_change',
            'portfolio_values',
            'stock_distribution_by_sector',
            'stock_distribution_by_company',
            'stock_holdings',
            'stock_suggestions',
        ]

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            'user',
            'invested_amount',
            'current_stock_holding',
            'profit_loss',
            'profit_loss_value',
            'day_change',
            'stock_holding_details',
            'cumulative_return_ytd',
            'cumulative_return_1yr',
            'cumulative_return_5yr',
            'risk_level_indicator',
            'std',
            'beta_coeffecient',
            'var',
            'market_sensitivity',
            'impact',
            'top_stocks',
            'worst_stocks',
            'transaction_history',
        ]

class StockStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockStatus
        fields = '__all__'       

class WatchlistSerializer(serializers.ModelSerializer):
    # Adding stock symbol and stock name from the Stock model
    stock_symbol = serializers.CharField(source='stock.stock_symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'current_price', 'volume', 'risk_level', 'user', 'stock', 'stock_symbol', 'stock_name']

class AlertSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='watchlist.stock.stock_name', read_only=True)
    stock_symbol = serializers.CharField(source='watchlist.stock.stock_symbol', read_only=True)

    class Meta:
        model = Alert
        fields = ('id', 'watchlist', 'condition', 'price', 'fulfilled', 'stock_name', 'stock_symbol')
