from django.contrib import admin
from .models import User, Stock, StockStatus, Transaction, Watchlist, Alert, StockHolding

# Register your models here.
admin.site.register(User)
admin.site.register(Stock)
admin.site.register(StockStatus)
admin.site.register(Transaction)
admin.site.register(Watchlist)
admin.site.register(Alert)
admin.site.register(StockHolding)