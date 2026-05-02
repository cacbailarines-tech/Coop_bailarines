from django.urls import path
from . import portal_views
from creditos.pdf_views import credito_pdf_portal as portal_credito_pdf
from .pdf_views import portal_estado_cuenta_pdf

urlpatterns = [
    path('', portal_views.portal_login, name='portal_login'),
    path('recuperar-pin/', portal_views.portal_recuperar_pin, name='portal_recuperar_pin'),
    path('inicio/', portal_views.portal_inicio, name='portal_inicio'),
    path('mis-datos/', portal_views.portal_mis_datos, name='portal_mis_datos'),
    path('libretas/', portal_views.portal_libretas, name='portal_libretas'),
    path('libretas/<int:lib_pk>/proposito/', portal_views.portal_establecer_proposito, name='portal_establecer_proposito'),
    path('libretas/<int:lib_pk>/reportar-aporte/<int:mes>/', portal_views.portal_reportar_aporte, name='portal_reportar_aporte'),
    path('libretas/<int:pk>/estado-cuenta/pdf/', portal_estado_cuenta_pdf, name='portal_estado_cuenta_pdf'),
    path('creditos/', portal_views.portal_creditos, name='portal_creditos'),
    path('creditos/solicitar/', portal_views.portal_solicitar_credito, name='portal_solicitar_credito'),
    path('creditos/<int:cred_pk>/pago/', portal_views.portal_reportar_pago, name='portal_reportar_pago'),
    path('pagos/combinado/', portal_views.portal_pago_combinado, name='portal_pago_combinado'),
    path('multas/', portal_views.portal_multas, name='portal_multas'),
    path('multas/<int:multa_pk>/pagar/', portal_views.portal_reportar_multa, name='portal_reportar_multa'),
    path('push/subscribe/', portal_views.portal_push_subscribe, name='portal_push_subscribe'),
    path('push/unsubscribe/', portal_views.portal_push_unsubscribe, name='portal_push_unsubscribe'),
    path('salir/', portal_views.portal_logout, name='portal_logout'),
    path('solicitudes/', portal_views.portal_mis_solicitudes, name='portal_mis_solicitudes'),
    path('creditos/<int:pk>/pdf/', portal_credito_pdf, name='portal_credito_pdf'),
    path('chat/', portal_views.portal_chat_api, name='portal_chat_api'),
]
