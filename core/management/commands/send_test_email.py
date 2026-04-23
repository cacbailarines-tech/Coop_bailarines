from django.core.management.base import BaseCommand, CommandError

from core.email_notifications import send_test_email


class Command(BaseCommand):
    help = 'Envia un correo de prueba para validar la configuracion de correo.'

    def add_arguments(self, parser):
        parser.add_argument('destino', type=str, help='Correo destino para la prueba')

    def handle(self, *args, **options):
        destino = options['destino'].strip()
        if not destino:
            raise CommandError('Debe indicar un correo destino.')
        if send_test_email(destino):
            self.stdout.write(self.style.SUCCESS(f'Correo de prueba enviado a {destino}'))
            return
        raise CommandError('No se pudo enviar el correo de prueba. Revise las variables GMAIL_*, EMAIL_* y APP_BASE_URL.')
