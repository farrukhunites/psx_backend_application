from django.db import models

# Create your models here.
class User(models.Model):
    RISK_CHOICES = [
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
    ]

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    date_created = models.DateField(auto_now_add=True)
    risk_preference = models.CharField(
        max_length=10,
        choices=RISK_CHOICES,
        default='moderate',  # Recommended default
    )

    def __str__(self):
        return f"{self.username} - {self.get_risk_preference_display()}"
    


class Dashboard(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="dashboard")
    
    # Top-Level Values
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_stock_holding = models.DecimalField(max_digits=15, decimal_places=2)
    profit_loss = models.CharField(max_length=50)  # e.g., "3.8% Gain"
    day_change = models.CharField(max_length=50)  # e.g., "-1.2%"
    
    # Portfolio Value over Last 10 Days
    portfolio_values = models.JSONField()  # Django's built-in JSONField

    # Stock Distribution
    stock_distribution_by_sector = models.JSONField()  # {"Energy": 20, "Banking": 40, "Cement": 40}
    stock_distribution_by_company = models.JSONField()  # {"OGDC": 20, "HBL": 40, "DGKC": 40}

    # Stock Holdings Table
    stock_holdings = models.JSONField()  # [{"stock_name": "OGDC", "price_bought": ..., ...}, ...]

    # Stock Suggestions Table
    stock_suggestions = models.JSONField()  # [{"stock_name": "OGDC", "current_price": ..., ...}, ...]

    def __str__(self):
        return f"Dashboard of {self.user.username}"