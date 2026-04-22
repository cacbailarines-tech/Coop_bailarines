from django.core.management.base import BaseCommand, CommandError

from core.push_notifications import notify_socio_push, push_configured
from socios.models import Socio


class Command(BaseCommand):
    help = 'Envía una notificación push de prueba a un socio por cédula.'

    def add_arguments(self, parser):
        parser.add_argument('cedula', type=str, help='Cédula del socio')

    def handle(self, *args, **options):
        if not push_configured():
            raise CommandError('Push no está configurado todavía.')

        cedula = options['cedula'].strip()
        try:
            socio = Socio.objects.get(cedula=cedula)
        except Socio.DoesNotExist as exc:
            raise CommandError('No existe un socio con esa cédula.') from exc

        sent = notify_socio_push(
            socio,
            'Prueba de notificación push',
            'Si recibió este aviso, las alertas push del portal ya están funcionando.',
            url='/portal/inicio/',
            tag=f'test-push-{socio.pk}',
        )
        if sent:
            self.stdout.write(self.style.SUCCESS(f'Push enviada a {sent} dispositivo(s).'))
        else:
            self.stdout.write(self.style.WARNING('No hay dispositivos suscritos activos para ese socio.'))
