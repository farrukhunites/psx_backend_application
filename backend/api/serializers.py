from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Dashboard, Portfolio


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
       