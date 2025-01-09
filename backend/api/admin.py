from django.contrib import admin
from .models import User, Stock, Dashboard, StockStatus, Portfolio

# Register your models here.
admin.site.register(User)
admin.site.register(Dashboard)
admin.site.register(Stock)
admin.site.register(StockStatus)
admin.site.register(Portfolio)