import json
from django.core.management.base import BaseCommand
from api.models import Stock

class Command(BaseCommand):
    help = "Load stocks data from JSON file"

    def handle(self, *args, **kwargs):
        with open('stock_data_fixture.json', 'r') as file:
            data = json.load(file)
            for item in data:
                # Access the 'fields' dictionary inside each item
                fields = item.get('fields', {})
                stock_symbol = fields.get('stock_symbol')
                stock_name = fields.get('stock_name', 'Unknown')
                sector = fields.get('sector', 'Unknown')

                # Skip if stock_symbol is missing
                if not stock_symbol:
                    self.stdout.write(self.style.WARNING(f"Skipping item due to missing stock_symbol: {item}"))
                    continue

                # Use get_or_create to ensure no duplicates based on stock_symbol
                Stock.objects.get_or_create(
                    stock_symbol=stock_symbol,
                    stock_name=stock_name,
                    sector=sector
                )

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
