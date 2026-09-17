from django.core.management.base import BaseCommand
from shop.models import Candle

# The class name MUST be 'Command'
class Command(BaseCommand):
    help = 'Seeds the database with initial candles'

    def handle(self, *args, **kwargs):
        candles_data = [
            {
                "name": "Lavender Dream",
                "description": "A soothing scent to help you relax after a long day.",
                "price": 499.00,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&q=80&w=400"
            },
            {
                "name": "Midnight Jasmine",
                "description": "Deep floral notes for a premium atmospheric experience.",
                "price": 599.00,
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1602873145311-4825d77561ed?auto=format&fit=crop&q=80&w=400"
            },
            {
                "name": "Vanilla Bean",
                "description": "Classic, warm, and comforting aroma for your living room.",
                "price": 399.00,
                "stock": 5,
                "image_url": "https://images.unsplash.com/photo-1596433809252-260c2745dfdd?auto=format&fit=crop&q=80&w=400"
            }
        ]

        self.stdout.write("Seeding candles...")

        for item in candles_data:
            candle, created = Candle.objects.get_or_create(
                name=item['name'],
                defaults=item
            )
            if created:
                self.stdout.write(f"Successfully created: {candle.name}")
            else:
                self.stdout.write(f"Skipped: {candle.name} (already exists)")

        self.stdout.write(self.style.SUCCESS('Successfully seeded LumiAnsh database!'))