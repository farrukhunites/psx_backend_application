from django.core.management.base import BaseCommand
from api.models import Stock, StockStatus
import requests
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Fetch stock data from the Pakistan Stock Exchange and update the database'

    def handle(self, *args, **kwargs):
        # Fetch all stocks
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

                close_price_value = "N/A"
                change_value_text = "N/A"
                change_percent_text = "N/A"

                if quote_price_div:
                    close_price = quote_price_div.find('div', class_='quote__close')
                    close_price_value = close_price.text.strip() if close_price else "N/A"

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
                    self.stdout.write(f"Close Price: {close_price_value}")
                    self.stdout.write(f"Change Value: {change_value_text}")
                    self.stdout.write(f"Change Percent: {change_percent_text}")
                else:
                    self.stdout.write("Could not find the quote__price section.")

                # 2. Extract stats data from the REG panel
                data_div = soup.find('div', class_='tabs__panel', attrs={'data-name': 'REG'})

                stats_data = {
                    'close_price': close_price_value,
                    'change_value': change_value_text,
                    'change_percent': change_percent_text,
                }

                if data_div:
                    stats_items = data_div.find_all('div', class_='stats_item')

                    for item in stats_items:
                        label_div = item.find('div', class_='stats_label')
                        value_div = item.find('div', class_='stats_value')

                        if label_div and value_div:
                            label = label_div.text.strip()
                            value = value_div.text.strip()
                            stats_data[label] = value
                        else:
                            self.stdout.write(f"Skipping item due to missing data: {item}")

                    # Print the extracted stats data
                    for key, value in stats_data.items():
                        self.stdout.write(f"{key}: {value}")
                else:
                    self.stdout.write("Could not find the data div with the specified attributes.")
            else:
                self.stdout.write(f"Failed to fetch the page. Status code: {response.status_code}")

            self.stdout.write(f"Fetched {stock.id} Successfully: {stock}")
            print(stats_data)

            # Create or update StockStatus
            StockStatus.objects.create(
                stock=stock,
                close_price=stats_data.get('close_price', "N/A"),
                change_value=stats_data.get('change_value', "N/A"),
                change_percent=stats_data.get('change_percent', "N/A"),
                open_price=stats_data.get('Open', "N/A"),
                high=stats_data.get('High', "N/A"),
                low=stats_data.get('Low', "N/A"),
                volume=stats_data.get('Volume', "N/A"),
                circuit_breaker=stats_data.get('CIRCUIT BREAKER', "N/A"),
                day_range=stats_data.get('DAY RANGE', "N/A"),
                fifty_two_week_range=stats_data.get('52-WEEK RANGE', "N/A"),
                ask_price=stats_data.get('Ask Price', "N/A"),
                ask_volume=stats_data.get('Ask Volume', "N/A"),
                bid_price=stats_data.get('Bid Price', "N/A"),
                bid_volume=stats_data.get('Bid Volume', "N/A"),
                ldcp=stats_data.get('LDCP', "N/A"),
                var=stats_data.get('VAR', "N/A"),
                haircut=stats_data.get('HAIRCUT', "N/A"),
                pe_ratio=stats_data.get('P/E Ratio (TTM) **', "N/A"),
                one_year_change=stats_data.get('1-Year Change *', "N/A"),
                ytd_change=stats_data.get('YTD Change *', "N/A"),
            )

            self.stdout.write(f"Added {stock.id} Successfully: {stock}")
