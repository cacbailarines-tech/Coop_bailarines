import logging
import os
import re

logger = logging.getLogger(__name__)


def extraer_comprobante_de_imagen(file_path_or_url):
    try:
        from google import genai
        from google.genai import types
        from django.conf import settings

        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY', '')
        if not api_key:
            logger.warning('GOOGLE_API_KEY no configurada, se omite OCR de imagen')
            return None

        client = genai.Client(api_key=api_key)

        prompt = (
            "Extrae el numero de comprobante, referencia de transferencia o numero de operacion "
            "de esta imagen de captura de pantalla bancaria. "
            "Devuelve SOLO el numero de referencia/comprobante encontrado. "
            "Si no encuentras un numero claro, devuelve 'NO_ENCONTRADO'."
        )

        if file_path_or_url.startswith(('http://', 'https://')):
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    types.Part.from_uri(file_uri=file_path_or_url, mime_type='image/jpeg'),
                    prompt,
                ],
            )
        else:
            with open(file_path_or_url, 'rb') as f:
                file_bytes = f.read()

            mime_type = 'image/jpeg'
            lower_path = file_path_or_url.lower()
            if '.png' in lower_path:
                mime_type = 'image/png'
            elif '.webp' in lower_path:
                mime_type = 'image/webp'

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                ],
            )

        text = (response.text or '').strip()

        if text == 'NO_ENCONTRADO' or not text:
            return None

        cleaned = re.sub(r'[^\d\w\-]', '', text)
        return cleaned if len(cleaned) >= 3 else None

    except Exception as e:
        logger.warning('Error extrayendo comprobante de imagen con Gemini: %s', e)
        return None
