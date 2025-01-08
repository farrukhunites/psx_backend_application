import json
from django.core.management.base import BaseCommand
from ....api.models import Stock

class Command(BaseCommand):
    help = "Load stocks data from JSON file"

    def handle(self, *args, **kwargs):
        with open('stock_data_fixture.json', 'r') as file:
            data = json.load(file)
            print(data)
            for item in data:
                Stock.objects.get_or_create(
                    stock_symbol=item['stock_symbol'],
                    stock_name=item['stock_name'],
                    sector=item['sector']
                )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
