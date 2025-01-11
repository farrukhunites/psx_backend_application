from django.db import models

# Create your models here.
class User(models.Model):
    RISK_CHOICES = [
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
    ]

    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, default="Person Name")
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
    
class Stock(models.Model):
    stock_symbol = models.CharField(max_length=10, unique=True)
    stock_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)

    def __str__(self):
        return self.stock_symbol
    
class StockHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price_buy = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    shares = models.IntegerField(default=0)
    
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
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey("Stock", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    shares = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically calculate the total transaction value."""
        self.total_value = self.shares * self.price_per_share
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} {self.shares} of {self.stock.stock_symbol} by {self.user.username}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='watchlists')
    current_price = models.CharField(max_length=20)  # As a string representation of decimal values
    volume = models.CharField(max_length=50)  # Volume as a string
    risk_level = models.CharField(max_length=20)  # Risk level: 'low', 'medium', 'high'

    class Meta:
        unique_together = ('user', 'stock')

    def __str__(self):
        return f"Watchlist for {self.user.username} - {self.stock.stock_symbol}"
    
class Alert(models.Model):
    watchlist = models.ForeignKey(Watchlist, related_name='alerts', on_delete=models.CASCADE)
    condition = models.CharField(choices=[('above', 'Above'), ('below', 'Below')], max_length=5)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.watchlist.stock.stock_symbol} - {self.condition} {self.price}"
