from django.core.management.base import BaseCommand
from myapp.models import Food
from django.db.models import Count

class Command(BaseCommand):
    help = "Remove duplicate Food entries, keeping only one per name."

    def handle(self, *args, **options):
        duplicates = Food.objects.values('name').annotate(count=Count('id')).filter(count__gt=1)

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("No duplicates found."))
            return

        for dup in duplicates:
            foods = Food.objects.filter(name=dup['name'])
            for f in foods[1:]:
                f.delete()
            self.stdout.write(self.style.WARNING(f"Cleaned duplicates for: {dup['name']}"))

        self.stdout.write(self.style.SUCCESS("Duplicate cleanup complete."))