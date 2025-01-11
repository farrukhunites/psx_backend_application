from decimal import Decimal
import math
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User, StockStatus, StockHolding
from django.db.models import Max
from ..views import calculate_risk_level


class PortfolioView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        
        res = {
            "user": user_id,
            "invested_amount": 0.0,
            "current_stock_holding": 0.0,
            "profit_loss": "",
            "profit_loss_value": "",
            "day_change": "",
            "stock_holding_details": [],
            "cumulative_return_ytd": "Insufficient Data",
            "cumulative_return_1yr": "Insufficient Data",
            "cumulative_return_5yr": "Insufficient Data",
            "risk_level_indicator": 0.0,
            "std": 0.0,
            "var": 0.0,
            "market_sensitivity": "Sentiment Analysis Awaiting...",
            "impact": "Sentiment Analysis Awaiting...",
            "top_stocks": [],
            "worst_stocks": [],
        }

        holding = StockHolding.objects.filter(user=user_id)

        if not(holding.exists()):
            return Response(res)

        invested = 0
        current_stock_holding = 0
    
        stock_holdings = []

        day_change = 0
        
        total_risk_score = 0
        total_var = 0
        total_count = holding.count()

        profit_loss_percentages = []
        for h in holding:
            status = StockStatus.objects.filter(
                stock=h.stock
            ).order_by('-date').first()
            status_close_price = Decimal(str(status.close_price).replace('Rs.', '').replace(',', '').strip())
            
            current_stock_holding += status_close_price*h.shares
            invested += h.shares * h.price_buy

            profit_loss_percentage = (
                (Decimal(status.change_value) * h.shares) /
                (h.shares * h.price_buy)
            ) * 100
            profit_loss_percentages.append(profit_loss_percentage)
                                    
            day_change +=  Decimal(status.change_percent.replace("(", '').replace("%)", '').strip())

            latest_date = StockStatus.objects.aggregate(latest_date=Max('date'))['latest_date']
            s = StockStatus.objects.filter(date=latest_date, stock=h.stock).first()
            one_year_change = s.one_year_change
            if one_year_change == 'N/A':
                one_year_change = 0
                
            risk_level, risk_score = calculate_risk_level(s.ldcp, s.var, s.haircut, s.pe_ratio, one_year_change, s.ytd_change)
        
            total_risk_score += risk_score
            total_var += float(s.var)*h.shares

            stock_holdings.append({"stock_name": h.stock.stock_name, 
                                   "stock_symbol": h.stock.stock_symbol, 
                                   "price_bought": h.price_buy, 
                                   "current_price": status_close_price, 
                                   "expected": status.circuit_breaker, 
                                   "day_change": status.change_percent, 
                                   "profit_loss_value": round(Decimal(status_close_price*h.shares)-h.shares*h.price_buy, 2), 
                                   "quantity": h.shares, 
                                   'profit_loss': round(((Decimal(status_close_price*h.shares)-h.shares*h.price_buy)/(h.shares*h.price_buy))*100, 2),
                                   "risk_preference": risk_level
                                   })

        res['risk_level_indicator'] = round((total_risk_score/total_count) * 100)
        res['var'] = round((total_var/total_count) * 100, 2)

        if profit_loss_percentages:
            mean_profit_loss = sum(profit_loss_percentages) / len(profit_loss_percentages)
            variance = sum(
                (x - mean_profit_loss) ** 2 for x in profit_loss_percentages
            ) / len(profit_loss_percentages)
            std_deviation = math.sqrt(variance)
        else:
            std_deviation = 0

        res['std'] = round(std_deviation, 2)

        res['invested_amount'] = invested
        res['current_stock_holding'] = current_stock_holding
        res['profit_loss'] = round(((current_stock_holding-invested) / invested) * 100, 2)
        res['profit_loss_value'] = (current_stock_holding-invested)
        day_change = round(day_change/holding.count(), 2)
        res['day_change'] = day_change

        res['stock_holding_details'] = stock_holdings
        sorted_holdings = sorted(stock_holdings, key=lambda x: x['profit_loss_value'])
        top_performing = sorted_holdings[-5:]
        worst_performing = sorted_holdings[:5]

        res['top_stocks'] = top_performing
        res['worst_stocks'] = worst_performing

        return Response(res)
