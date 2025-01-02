from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Dashboard


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