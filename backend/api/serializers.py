from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, StockStatus, Watchlist, Alert


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'password', 'email', 'cdc_id', 'date_created', 'risk_preference']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

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
