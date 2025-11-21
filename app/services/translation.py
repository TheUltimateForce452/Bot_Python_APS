import logging

import requests

from app.config import (
    HEADERS,
    LIBRETRANSLATE_ENDPOINT,
    MYMEMORY_ENDPOINT,
    TRANSLATE_TIMEOUT,
)


def translate_text(text: str, source: str = "en", target: str = "es") -> str:
    try:
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        resp = requests.post(
            LIBRETRANSLATE_ENDPOINT,
            json=payload,
            timeout=TRANSLATE_TIMEOUT,
            headers=HEADERS,
        )
        if resp.status_code == 200 and resp.content:
            try:
                data = resp.json()
                translated = data.get("translatedText") or data.get("result")
                if translated:
                    return translated
                logging.warning("LibreTranslate sin 'translatedText'.")
            except ValueError as exc:
                logging.warning("LibreTranslate devolvió contenido no-JSON: %s", exc)
        else:
            logging.warning("LibreTranslate status=%s", resp.status_code)
    except requests.RequestException as exc:
        logging.warning("Error conectando a LibreTranslate: %s", exc)

    try:
        params = {"q": text, "langpair": f"{source}|{target}"}
        resp = requests.get(
            MYMEMORY_ENDPOINT,
            params=params,
            timeout=TRANSLATE_TIMEOUT,
            headers=HEADERS,
        )
        if resp.status_code == 200 and resp.content:
            try:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText")
                if translated:
                    return translated
                logging.warning("MyMemory sin 'translatedText'.")
            except ValueError as exc:
                logging.warning("MyMemory devolvió contenido no-JSON: %s", exc)
        else:
            logging.warning("MyMemory status=%s", resp.status_code)
    except requests.RequestException as exc:
        logging.warning("Error conectando a MyMemory: %s", exc)

    logging.warning("No fue posible traducir — uso el texto original.")
    return text


def is_probably_spanish(text: str) -> bool:
    lowered = text.lower()
    for word in (" el ", " la ", " y ", " de ", " que ", "¡", "¿", "los ", "las ", "un ", "una "):
        if word in lowered:
            return True
    return False
