from django.core.management.base import BaseCommand
from core.email_notifications import send_payment_reminders


class Command(BaseCommand):
    help = 'Envía recordatorios de pago por email (ejecutar diariamente)'

    def handle(self, *args, **options):
        sent, errors = send_payment_reminders()
        self.stdout.write(self.style.SUCCESS(f'✅ {sent} correo(s) enviado(s)'))
        for e in errors:
            self.stdout.write(self.style.ERROR(f'❌ {e}'))
