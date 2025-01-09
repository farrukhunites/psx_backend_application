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
    email = models.CharField(max_length=50, unique=True, null=True, blank=True)
    cdc_id = models.CharField(max_length=100, default="Unknown")
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
    
class Portfolio(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="portfolio")

    invested_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_stock_holding = models.DecimalField(max_digits=15, decimal_places=2)
    profit_loss = models.CharField(max_length=50)  # e.g., "3.8% Gain"
    profit_loss_value = models.CharField(max_length=50)
    day_change = models.CharField(max_length=50)

    stock_holding_details = models.JSONField()

    cumulative_return_ytd = models.CharField(max_length=50)
    cumulative_return_1yr = models.CharField(max_length=50)
    cumulative_return_5yr = models.CharField(max_length=50)

    risk_level_indicator = models.DecimalField(max_digits=15, decimal_places=2)
    std = models.DecimalField(max_digits=15, decimal_places=2)
    beta_coeffecient = models.DecimalField(max_digits=15, decimal_places=2)
    var = models.DecimalField(max_digits=15, decimal_places=2)

    market_sensitivity = models.CharField(max_length=50)
    impact = models.CharField(max_length=50)

    top_stocks = models.JSONField()
    worst_stocks = models.JSONField()

    transaction_history = models.JSONField()

    def __str__(self):
        return f"Portfolio of {self.user.username}"

class Stock(models.Model):
    stock_symbol = models.CharField(max_length=10, unique=True)
    stock_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)

    def __str__(self):
        return self.stock_symbol
    
class StockStatus(models.Model):
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name="stock_statuses")
    date = models.DateField(auto_now_add=True)

    # Stock-related attributes
    close_price = models.CharField(max_length=20)  # As a string representation of decimal values
    change_value = models.CharField(max_length=20)  # As a string representation of decimal values
    change_percent = models.CharField(max_length=20)  # As a string representation of decimal values
    open_price = models.CharField(max_length=20)  # As a string representation of decimal values
    high = models.CharField(max_length=20)  # As a string representation of decimal values
    low = models.CharField(max_length=20)  # As a string representation of decimal values
    volume = models.CharField(max_length=50)  # Volume as a string
    circuit_breaker = models.CharField(max_length=20)  # Format: "0.71 — 2.71"
    day_range = models.CharField(max_length=20)  # Format: "1.68 — 1.96"
    fifty_two_week_range = models.CharField(max_length=20)  # Format: "1.15 — 2.00"
    ask_price = models.CharField(max_length=20)  # As a string representation of decimal values
    ask_volume = models.CharField(max_length=50)  # Ask volume as a string
    bid_price = models.CharField(max_length=20)  # As a string representation of decimal values
    bid_volume = models.CharField(max_length=50)  # Bid volume as a string
    ldcp = models.CharField(max_length=20)  # Last Day Closing Price as a string
    var = models.CharField(max_length=20)  # Value at Risk as a string
    haircut = models.CharField(max_length=20)  # Haircut as a string
    pe_ratio = models.CharField(max_length=20, null=True, blank=True)  # P/E Ratio as a string (nullable for N/A)
    one_year_change = models.CharField(max_length=20)  # 1-Year Change as a string
    ytd_change = models.CharField(max_length=20) 

    class Meta:
        unique_together = ('stock', 'date')  # Ensure unique combination of stock and date

    def __str__(self):
        return f"Stock Status for {self.stock.stock_symbol} on {self.date}"