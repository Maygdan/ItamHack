from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from mini.models import LoginCode


class Command(BaseCommand):
    help = 'Удаляет коды входа старше 2 месяцев'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=60)
        deleted, _ = LoginCode.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(f'Удалено {deleted} старых кодов входа (старше 2 месяцев)')
        )
