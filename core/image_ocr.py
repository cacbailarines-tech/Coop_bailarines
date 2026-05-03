import logging
import os
import re

logger = logging.getLogger(__name__)


def extraer_comprobante_de_imagen(file_data, file_name='image.jpg'):
    logger.info('=== OCR: Iniciando extraccion de imagen: %s (%d bytes)', file_name, len(file_data))
    try:
        import pytesseract
        from PIL import Image
        import io

        logger.info('OCR: version de tesseract disponible')

        img = Image.open(io.BytesIO(file_data))
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
        logger.info('OCR: texto extraido por tesseract: "%s"', text)

        patterns = [
            r'comprobante[\s#:.]*([\d\-]+)',
            r'referencia[\s#:.]*([\d\-]+)',
            r'operacion[\s#:.]*([\d\-]+)',
            r'numero[\s#:.]*([\d\-]+)',
            r'N[°o][\s#:.]*([\d\-]+)',
            r'\b(\d{5,})\b',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                logger.info('OCR: comprobante extraido (pattern "%s"): "%s"', pattern, result)
                return result

        cleaned = re.sub(r'[^\d]', '', text)
        numbers = re.findall(r'\d{4,}', cleaned)
        if numbers:
            logger.info('OCR: comprobante extraido (fallback numerico): "%s"', numbers[0])
            return numbers[0]

        logger.info('OCR: no se encontro numero en la imagen')
        return None

    except ImportError as e:
        logger.error('OCR: pytesseract no instalado: %s', e)
        return None
    except Exception as e:
        logger.exception('OCR: Error inesperado extrayendo comprobante: %s', e)
        return None
