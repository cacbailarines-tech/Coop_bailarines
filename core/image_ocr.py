import logging
import os
import re

logger = logging.getLogger(__name__)


def extraer_comprobante_de_imagen(file_path_or_url):
    logger.info('=== OCR: Iniciando extraccion de imagen: %s', file_path_or_url)
    try:
        from google import genai
        from google.genai import types
        from django.conf import settings

        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY', '')
        if not api_key:
            logger.warning('OCR: GOOGLE_API_KEY no configurada')
            return None
        logger.info('OCR: API key encontrada')

        client = genai.Client(api_key=api_key)

        prompt = (
            "Extrae el numero de comprobante, referencia de transferencia o numero de operacion "
            "de esta imagen de captura de pantalla bancaria. "
            "Devuelve SOLO el numero de referencia/comprobante encontrado. "
            "Si no encuentras un numero claro, devuelve 'NO_ENCONTRADO'."
        )

        if file_path_or_url.startswith(('http://', 'https://')):
            logger.info('OCR: usando URL')
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    types.Part.from_uri(file_uri=file_path_or_url, mime_type='image/jpeg'),
                    prompt,
                ],
            )
        else:
            logger.info('OCR: usando archivo local, ruta: %s', file_path_or_url)
            if not os.path.exists(file_path_or_url):
                logger.error('OCR: El archivo no existe en la ruta: %s', file_path_or_url)
                return None
            with open(file_path_or_url, 'rb') as f:
                file_bytes = f.read()
            logger.info('OCR: leidos %d bytes del archivo', len(file_bytes))

            mime_type = 'image/jpeg'
            lower_path = file_path_or_url.lower()
            if '.png' in lower_path:
                mime_type = 'image/png'
            elif '.webp' in lower_path:
                mime_type = 'image/webp'
            logger.info('OCR: mime type: %s', mime_type)

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                ],
            )

        text = (response.text or '').strip()
        logger.info('OCR: respuesta de Gemini: "%s"', text)

        if text == 'NO_ENCONTRADO' or not text:
            logger.info('OCR: no se encontro numero en la imagen')
            return None

        cleaned = re.sub(r'[^\d\w\-]', '', text)
        if len(cleaned) < 3:
            logger.info('OCR: texto muy corto tras limpiar: "%s"', cleaned)
            return None

        logger.info('OCR: comprobante extraido: "%s"', cleaned)
        return cleaned

    except ImportError as e:
        logger.error('OCR: Error importando google-genai: %s', e)
        return None
    except Exception as e:
        logger.exception('OCR: Error inesperado extrayendo comprobante: %s', e)
        return None
