from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.contrib.auth.hashers import check_password
from .models import User, Stock, StockStatus, Transaction, Watchlist, Alert, StockHolding
from .serializers import UserSerializer, StockStatusSerializer, WatchlistSerializer, AlertSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers import serialize
import numpy as np
from django.db import IntegrityError
from django.db.models import Max


class UserUpdateView(APIView):
    def put(self, request, *args, **kwargs):
        # Extract user ID from request data
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Map frontend fields to model fields
        update_data = {
            'name': request.data.get('name'),
            'cdc_id': request.data.get('cdc_id'),  # Map 'cdcid' to 'cdc_id'
            'email': request.data.get('email')
        }

        # Update user with direct assignment
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        
        user.save()
        return Response({'status': 'User updated'}, status=status.HTTP_200_OK)

def calculate_risk_level(ldcp, var, haircut, pe_ratio, one_year_change, ytd_change):
    # Convert the string inputs into float values, handle "N/A" for pe_ratio
    try:
        ldcp = float(ldcp)
    except ValueError:
        ldcp = 0.0  # Default to 0 if conversion fails

    try:
        var = float(var)
    except ValueError:
        var = 0.0  # Default to 0 if conversion fails

    try:
        haircut = float(haircut)
    except ValueError:
        haircut = 0.0  # Default to 0 if conversion fails

    # Handle "N/A" or non-numeric values for pe_ratio
    if pe_ratio == "N/A" or not pe_ratio:
        pe_ratio = 0.0  # Default to 0 for P/E Ratio if it's "N/A"
    else:
        try:
            pe_ratio = float(pe_ratio)
        except ValueError:
            pe_ratio = 0.0  # Default to 0 if conversion fails

    # Convert percentage values for "one_year_change" and "ytd_change"
    one_year_change = float(one_year_change.replace('%', '').strip()) / 100
    ytd_change = float(ytd_change.replace('%', '').strip()) / 100

    # Formula for risk score, with adjusted weightings
    risk_score = (var * -0.001) + (haircut * -0.002) + (pe_ratio / 25) + (abs(one_year_change) / 2) + (ytd_change / 2)

    # Apply a logistic transformation (Sigmoid function)
    risk_score = 1 / (1 + np.exp(-risk_score))

    # Normalize the risk score between 0 and 1
    if risk_score <= 0.5:
        return ("low", risk_score)
    elif risk_score <= 0.7:
        return ("moderate", risk_score)
    else:
        return ("high", risk_score)

class UserListCreate(generics.ListCreateAPIView):
    """
    Handles listing all users and creating a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    """
    Handles retrieving a single user by ID.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginUser(APIView):
    """
    Handles user login by validating username and password.
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            serializer = UserSerializer(user)
            return Response({"message": "Login successful!", "user": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)

def get_all_stocks(request):
    stocks = list(Stock.objects.values())
    return JsonResponse(stocks, safe=False)

def get_stock_by_symbol(request, stock_symbol):
    try:
        stock_symbol = stock_symbol.upper()
        stock = Stock.objects.get(stock_symbol=stock_symbol)
        return JsonResponse({
            "id": stock.id,
            "stock_symbol": stock.stock_symbol,
            "stock_name": stock.stock_name,
            "sector": stock.sector
        })
    except Stock.DoesNotExist:
        return JsonResponse({"error": "Stock not found"}, status=404)

def get_all_sectors(request):
    sectors = Stock.objects.values_list('sector', flat=True).distinct()
    return JsonResponse(list(sectors), safe=False)

def get_all_stock_statuses(request):
    stocks_statuses = list(StockStatus.objects.values())
    return JsonResponse(stocks_statuses, safe=False)

def get_stock_status_for_symbol(request, stock_symbol):
    try:
        stock_symbol = stock_symbol.upper()
        # Find the stock with the given stock_symbol
        stock = Stock.objects.get(stock_symbol=stock_symbol)

        # Fetch all related StockStatus objects for the found stock
        stock_statuses = StockStatus.objects.filter(stock=stock)

        # Prepare the response data (you can modify the structure as needed)
        stock_status_data = []
        for status in stock_statuses:
            stock_status_data.append({
                'date': status.date,
                'close_price': status.close_price,
                'change_value': status.change_value,
                'change_percent': status.change_percent,
                'open_price': status.open_price,
                'high': status.high,
                'low': status.low,
                'volume': status.volume,
                'circuit_breaker': status.circuit_breaker,
                'day_range': status.day_range,
                'fifty_two_week_range': status.fifty_two_week_range,
                'ask_price': status.ask_price,
                'ask_volume': status.ask_volume,
                'bid_price': status.bid_price,
                'bid_volume': status.bid_volume,
                'ldcp': status.ldcp,
                'var': status.var,
                'haircut': status.haircut,
                'pe_ratio': status.pe_ratio,
                'one_year_change': status.one_year_change,
                'ytd_change': status.ytd_change
            })

        # Return the data as a JSON response
        return JsonResponse({'stock_statuses': stock_status_data}, safe=False)

    except Stock.DoesNotExist:
        # If stock with the given symbol does not exist
        return JsonResponse({'error': f'Stock with symbol {stock_symbol} not found'}, status=404)

class LatestStockStatus(APIView):
    def get(self, request, stock_symbol):
        # Get the latest StockStatus for the given stock_symbol
        try:
            stock_status = StockStatus.objects.filter(
                stock__stock_symbol=stock_symbol
            ).order_by('-date').first()  # Get the latest one based on date
            if stock_status:
                # Serialize the stock status and return it
                serializer = StockStatusSerializer(stock_status)
                return Response(serializer.data)
            else:
                return JsonResponse({"message": "Stock status not found."}, status=status.HTTP_404_NOT_FOUND)
        except StockStatus.DoesNotExist:
            return JsonResponse({"message": "Stock status not found."}, status=status.HTTP_404_NOT_FOUND)
   
def update_dashboard_and_portfolio(transaction: Transaction, user_id):

    user = get_object_or_404(User, id=user_id)

    holdings, created = StockHolding.objects.get_or_create(user=user, stock=transaction.stock)

    if transaction.transaction_type == "buy":
        holdings.price_buy = (Decimal(holdings.price_buy*holdings.shares) + Decimal(transaction.price_per_share*transaction.shares))/(holdings.shares+transaction.shares)
        holdings.shares += transaction.shares
    elif transaction.transaction_type == "sell":
        holdings.shares -= transaction.shares

    if holdings.shares <= 0:
        holdings.delete()
    else:
        holdings.save()

@csrf_exempt
def add_transaction(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        transaction_data = json.loads(request.body)

        print(transaction_data)

        stock_symbol = transaction_data.get("stock_symbol")
        transaction_type = transaction_data.get("type")
        shares = int(transaction_data.get("shares", 0))
        price_per_share = Decimal(transaction_data.get("price_per_share", "0.0"))

        # Fetch or create the stock
        stock, _ = Stock.objects.get_or_create(stock_symbol=stock_symbol)

        # Create the transaction
        transaction = Transaction.objects.create(
            user=user,
            stock=stock,
            transaction_type=transaction_type,
            shares=shares,
            price_per_share=price_per_share,
        )

        # Update dashboard and portfolio (reuse logic from `update_dashboard_and_portfolio`)
        update_dashboard_and_portfolio(transaction, user_id)

        return JsonResponse({"status": "success", "message": "Transaction added successfully!"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})

def transaction_history(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Fetch transactions and related stock details
    transactions = Transaction.objects.filter(user=user).select_related('stock').order_by('-transaction_date')

    # Format data to include stock_name and stock_symbol
    formatted_transactions = [
        {
            "user": transaction.user.id,
            "stock_name": transaction.stock.stock_name,  # Assuming 'name' is the field for stock name
            "stock_symbol": transaction.stock.stock_symbol,  # Assuming 'symbol' is the field for stock symbol
            "transaction_type": transaction.transaction_type,
            "shares": transaction.shares,
            "price_per_share": float(transaction.price_per_share),
            "total_value": float(transaction.total_value),
            "transaction_date": transaction.transaction_date,
        }
        for transaction in transactions
    ]

    return JsonResponse({"transactions": formatted_transactions})

class WatchlistCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        stock_symbol = request.data.get('stock_symbol')

        # Check if user_id and stock_symbol are provided
        if not user_id or not stock_symbol:
            return Response({"error": "user_id and stock_symbol are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the latest stock status for the given stock_symbol
        stock_status = StockStatus.objects.filter(
            stock__stock_symbol=stock_symbol
        ).order_by('-date').first()

        print(stock_status)

        if not stock_status:
            raise NotFound(detail="Stock status not found for this symbol", code=404)

        # Calculate risk level
        risk_level, score = calculate_risk_level(
            stock_status.ldcp, stock_status.var, stock_status.haircut,
            stock_status.pe_ratio, stock_status.one_year_change, stock_status.ytd_change
        )

        try:
            # Create Watchlist entry for the specified user_id
            watchlist = Watchlist.objects.create(
                user_id=user_id,  # Use the user_id provided in the request
                stock=stock_status.stock,
                current_price=stock_status.close_price,
                volume=stock_status.volume,
                risk_level=risk_level
            )

            # Serialize and return the response
            serializer = WatchlistSerializer(watchlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        except IntegrityError:
        # Handle any other integrity errors
            return Response({"error": "A unique constraint violation occurred."}, status=status.HTTP_400_BAD_REQUEST)

class WatchlistListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')

        # Check if user_id is provided
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the watchlist entries for the specified user_id
        watchlist_entries = Watchlist.objects.filter(user_id=user_id)
        
        if not watchlist_entries:
            return Response(watchlist_entries, status=status.HTTP_200_OK)

        # For each stock in the watchlist, check and update the stock status
        for watchlist_entry in watchlist_entries:
            stock_symbol = watchlist_entry.stock.stock_symbol

            # Retrieve the latest stock status for the given stock_symbol
            latest_stock_status = StockStatus.objects.filter(
                stock__stock_symbol=stock_symbol
            ).order_by('-date').first()

            if latest_stock_status:
                # Compare if the latest stock status is different from the current stock status in the watchlist
                if latest_stock_status.close_price != watchlist_entry.current_price or latest_stock_status.volume != watchlist_entry.volume:
                    # Update the watchlist entry with the new stock status
                    watchlist_entry.current_price = latest_stock_status.close_price
                    watchlist_entry.volume = latest_stock_status.volume
                    
                    # Recalculate the risk level with the updated stock status
                    risk_level, score = calculate_risk_level(
                        latest_stock_status.ldcp, latest_stock_status.var, latest_stock_status.haircut,
                        latest_stock_status.pe_ratio, latest_stock_status.one_year_change, latest_stock_status.ytd_change
                    )
                    watchlist_entry.risk_level = risk_level
                    watchlist_entry.save()  # Save the updated entry

        # Serialize and return the updated watchlist
        serializer = WatchlistSerializer(watchlist_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WatchlistDeleteAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        stock_symbol = request.data.get('stock_symbol')

        # Check if user_id and stock_symbol are provided
        if not user_id or not stock_symbol:
            return Response({"error": "user_id and stock_symbol are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the watchlist entry for the specified user_id and stock_symbol
        watchlist_entry = Watchlist.objects.filter(user_id=user_id, stock__stock_symbol=stock_symbol).first()

        if not watchlist_entry:
            return Response({"error": "Watchlist entry not found for this user and stock symbol"}, status=status.HTTP_404_NOT_FOUND)

        # Delete the watchlist entry
        watchlist_entry.delete()

        return Response({"message": "Watchlist entry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class AlertCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        watchlist_id = request.data.get('watchlist_id')
        condition = request.data.get('condition')
        price = request.data.get('price')

        # Check if required fields are provided
        if not user_id or not watchlist_id or not condition or not price:
            return Response({"error": "user_id, watchlist_id, condition, and price are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the corresponding Watchlist
        try:
            watchlist = Watchlist.objects.get(id=watchlist_id, user_id=user_id)
        except Watchlist.DoesNotExist:
            return Response({"error": "Watchlist not found for the user"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve and preprocess the current price from the Watchlist
        current_price_str = watchlist.current_price
        current_price = float(current_price_str.replace('Rs.', '').replace(',', '').strip())

        # Determine if the alert condition is fulfilled
        if (condition == 'above' and current_price > price) or (condition == 'below' and current_price < price):
            fulfilled = True
        else:
            fulfilled = False

        # Create the alert
        alert = Alert.objects.create(
            watchlist=watchlist,
            condition=condition,
            price=price,
            fulfilled=fulfilled
        )

        # Serialize and return the response
        serializer = AlertSerializer(alert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AlertListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')

        # Check if user_id is provided
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get all alerts for the specified user_id
        alerts = Alert.objects.filter(watchlist__user_id=user_id)

        # Check each alert's condition and update the fulfilled status
        for alert in alerts:
            # Retrieve and preprocess the current price from the related Watchlist
            current_price_str = alert.watchlist.current_price
            current_price = float(current_price_str.replace('Rs.', '').replace(',', '').strip())

            # Update the fulfilled field based on the condition
            if (alert.condition == 'above' and current_price > alert.price) or \
               (alert.condition == 'below' and current_price < alert.price):
                alert.fulfilled = True
            else:
                alert.fulfilled = False

            # Save the updated alert
            alert.save()

        # Serialize and return the response
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AlertDeleteAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        alert_id = request.data.get('alert_id')

        if not alert_id:
            return Response({"error": "alert_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to find and delete the alert
        try:
            alert = Alert.objects.get(id=alert_id)
            alert.delete()
            return Response({"message": "Alert deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Alert.DoesNotExist:
            return Response({"error": "Alert not found."}, status=status.HTTP_404_NOT_FOUND)
