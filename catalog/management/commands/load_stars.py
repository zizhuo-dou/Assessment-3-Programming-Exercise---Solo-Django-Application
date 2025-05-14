import csv
from django.core.management.base import BaseCommand
from catalog.models import Star

class Command(BaseCommand):
    help = 'Load up to 3000 stars from hipparcos_sample.csv'

    def handle(self, *args, **kwargs):
        with open('hipparcos_sample.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                if count >= 3000:
                    break
                Star.objects.create(
                    name=row['name'],
                    constellation=row['constellation'],
                    magnitude=float(row['magnitude']),
                    ra=float(row['ra']),
                    dec=float(row['dec'])
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} stars.'))



