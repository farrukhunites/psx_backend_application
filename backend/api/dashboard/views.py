from decimal import Decimal
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User, StockStatus, StockHolding
from django.db.models import Max
from ..views import calculate_risk_level


class DashboardView(APIView):
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
                "day_change": "",
                "portfolio_values": [],
                "stock_distribution_by_sector": [],
                "stock_distribution_by_company": {},
                "stock_holdings": [],
                "stock_suggestions": [],
        }

        holding = StockHolding.objects.filter(user=user_id)

        if not(holding.exists()):
            return Response(res)

        invested = 0
        current_stock_holding = 0
        sector = {}
        company = {}

        stock_holdings = []

        day_change = 0
        
        for h in holding:
            status = StockStatus.objects.filter(
                stock=h.stock
            ).order_by('-date').first()
            status_close_price = Decimal(str(status.close_price).replace('Rs.', '').replace(',', '').strip())
            try:
                sector[h.stock.sector] += status_close_price*h.shares
            except KeyError:
                sector[h.stock.sector] = status_close_price*h.shares

            try:
                company[h.stock.stock_name] += status_close_price*h.shares
            except KeyError:
                company[h.stock.stock_name] = status_close_price*h.shares
            
            current_stock_holding += status_close_price*h.shares
            invested += h.shares * h.price_buy

            stock_holdings.append({"stock_name": h.stock.stock_name, "price_bought": h.price_buy, "current_price": status_close_price, "expected": status.circuit_breaker, "day_change": status.change_percent, "profit_loss": Decimal(status.change_value)*h.shares})
            day_change +=  Decimal(status.change_percent.replace("(", '').replace("%)", '').strip())
        
        day_change = day_change / holding.count()

        stock_distribution_by_sector = []
        for s in sector.keys():
            stock_distribution_by_sector.append({'x':s, 'y':round((sector[s]/current_stock_holding)*100, 2)})

        stock_distribution_by_company = []
        for c in company.keys():
            stock_distribution_by_company.append({'x':c, 'y':round((company[c]/current_stock_holding)*100, 2)})

        res['invested_amount'] = invested
        res['current_stock_holding'] = current_stock_holding
        res['day_change'] = day_change
        res['stock_distribution_by_sector'] = stock_distribution_by_sector
        res['stock_distribution_by_company'] = stock_distribution_by_company
        res['stock_holdings'] = stock_holdings

        res['profit_loss'] = round(((current_stock_holding-invested) / invested) * 100, 2)

        latest_date = StockStatus.objects.aggregate(latest_date=Max('date'))['latest_date']
        latest_stock_statuses = StockStatus.objects.filter(date=latest_date)
        suggestions = []
        for s in latest_stock_statuses:
            if s.one_year_change != 'N/A':
                risk_level, risk_score = calculate_risk_level(s.ldcp, s.var, s.haircut, s.pe_ratio, s.one_year_change, s.ytd_change)
                if risk_level == user.risk_preference and risk_score != 0:
                    holding = StockHolding.objects.filter(stock=s.stock).exists()
                    if not(holding):
                        suggestions.append({"stock_name": s.stock.stock_name, "current_price": s.close_price, "volume": s.volume, "suggestion": 'Buy', 'risk_preference': risk_level, "risk_score": risk_score})
                
        sorted_suggestions = sorted(suggestions, key=lambda x: x['risk_score'])[:5]
        res['stock_suggestions'] = sorted_suggestions

        holdings = StockHolding.objects.filter(user=user_id).values_list('stock', flat=True)
        stock_statuses = StockStatus.objects.filter(stock__in=holdings)
        
        portfolio = {}
        for s in stock_statuses:
            stock_holding = StockHolding.objects.get(stock=s.stock)
            status_close_price = Decimal(s.close_price.replace('Rs.', '').replace(',', '').strip())

            try:
                portfolio[s.date] += stock_holding.shares*status_close_price
            except KeyError:
                portfolio[s.date] = stock_holding.shares*status_close_price

        portfolio_value = []
        for d in portfolio.keys():
            portfolio_value.append({'x': d, 'y': portfolio[d]})
        
        res['portfolio_values'] = portfolio_value

        return Response(res)
