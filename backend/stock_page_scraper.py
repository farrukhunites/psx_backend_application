from api.models import Stock, StockStatus

import requests
from bs4 import BeautifulSoup

stocks = Stock.objects.all()

for stock in stocks:

    # Define the URL
    url = f"https://dps.psx.com.pk/company/{stock.stock_symbol}"

    # Send a GET request to fetch the HTML content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Extract close price, change in value, and percentage change
        quote_price_div = soup.find('div', class_='quote__price')

        if quote_price_div:
            # Extract close price
            close_price = quote_price_div.find('div', class_='quote__close')
            close_price_value = close_price.text.strip() if close_price else "N/A"

            # Extract change in value and percent
            change_div = quote_price_div.find('div', class_='quote__change')
            if change_div:
                change_value = change_div.find('div', class_='change__value')
                change_percent = change_div.find('div', class_='change__percent')
                change_value_text = change_value.text.strip() if change_value else "N/A"
                change_percent_text = change_percent.text.strip() if change_percent else "N/A"
            else:
                change_value_text = "N/A"
                change_percent_text = "N/A"

            # Print the extracted data for close price and change info
            print(f"Close Price: {close_price_value}")
            print(f"Change Value: {change_value_text}")
            print(f"Change Percent: {change_percent_text}")
        else:
            print("Could not find the quote__price section.")

        # 2. Extract stats data from the REG panel
        data_div = soup.find('div', class_='tabs__panel', attrs={'data-name': 'REG'})

        if data_div:
            # Extract stats values
            stats_items = data_div.find_all('div', class_='stats_item')

            # Create a dictionary to store the extracted data
            stats_data = {}

            for item in stats_items:
                # Safely find label and value
                label_div = item.find('div', class_='stats_label')
                value_div = item.find('div', class_='stats_value')

                # Only add to the dictionary if both are present
                if label_div and value_div:
                    label = label_div.text.strip()
                    value = value_div.text.strip()
                    stats_data[label] = value
                else:
                    print(f"Skipping item due to missing data: {item}")

            # Print the extracted stats data
            for key, value in stats_data.items():
                print(f"{key}: {value}")
        else:
            print("Could not find the data div with the specified attributes.")

    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

    print(f"Fetched {stock.id} Successfully: {stock}")

    # Create or update StockStatus
    StockStatus.objects.get_or_create(
            stock=stock,  # Pass the Stock object directly
            defaults={  # Use defaults for the data fields
                'close_price': stats_data['close_price'],
                'change_value': stats_data['change_value'],
                'change_percent': stats_data['change_percent'],
                'open_price': stats_data['open_price'],
                'high': stats_data['high'],
                'low': stats_data['low'],
                'volume': stats_data['volume'],
                'circuit_breaker': stats_data['circuit_breaker'],
                'day_range': stats_data['day_range'],
                'fifty_two_week_range': stats_data['fifty_two_week_range'],
                'ask_price': stats_data['ask_price'],
                'ask_volume': stats_data['ask_volume'],
                'bid_price': stats_data['bid_price'],
                'bid_volume': stats_data['bid_volume'],
                'ldcp': stats_data['ldcp'],
                'var': stats_data['var'],
                'haircut': stats_data['haircut'],
                'pe_ratio': stats_data['pe_ratio'],
                'one_year_change': stats_data['one_year_change'],
                'ytd_change': stats_data['ytd_change'],
            }
        )

    print(f"Added {stock.id} Successfully: {stock}")