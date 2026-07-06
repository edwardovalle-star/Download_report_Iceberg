from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ENTORNOS_LOCALES = {"local", "desarrollo", "dev", "windows"}
ENTORNOS_REMOTOS = {
    "streamlit",
    "streamlit_cloud",
    "cloud",
    "codespaces",
    "github_codespaces",
    "produccion",
    "production",
}


def _normalizar_texto(valor: object, default: str = "") -> str:
    if valor is None:
        return default

    return str(valor).strip().lower()


def _normalizar_bool(valor: object, default: bool = False) -> bool:
    if valor is None:
        return default

    texto = _normalizar_texto(valor)

    if texto in {"1", "true", "yes", "y", "si", "on"}:
        return True

    if texto in {"0", "false", "no", "n", "off"}:
        return False

    return default


def _leer_streamlit_secret(nombre: str) -> str | None:
    """
    Lee secrets de Streamlit si estan disponibles.
    No falla si la app esta corriendo local sin secrets.
    """
    try:
        import streamlit as st

        valor = st.secrets.get(nombre)

        if valor is None:
            return None

        return str(valor)

    except Exception:
        return None


def obtener_variable(nombre: str, default: str = "") -> str:
    """
    Lee primero variables de entorno y luego Streamlit secrets.
    """
    valor = os.getenv(nombre)

    if valor is not None and str(valor).strip():
        return str(valor)

    valor_secret = _leer_streamlit_secret(nombre)

    if valor_secret is not None and str(valor_secret).strip():
        return str(valor_secret)

    return default


def _esta_streamlit_cloud() -> bool:
    """
    Detecta Streamlit Cloud por senales del servidor.
    """
    if Path("/mount/src").exists():
        return True

    entorno = _normalizar_texto(obtener_variable("ICEBERG_ENTORNO", ""))

    if entorno in {"streamlit", "streamlit_cloud", "cloud", "produccion", "production"}:
        return True

    return False


def _esta_codespaces() -> bool:
    """
    Detecta GitHub Codespaces.
    """
    return (
        _normalizar_bool(os.getenv("CODESPACES"), False)
        or bool(os.getenv("CODESPACE_NAME"))
        or bool(os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"))
    )


def detectar_entorno() -> str:
    """
    Detecta el entorno de ejecucion.

    Prioridad:
    1. Streamlit Cloud.
    2. Codespaces.
    3. ICEBERG_ENTORNO.
    4. local por defecto.
    """
    if _esta_streamlit_cloud():
        return "streamlit_cloud"

    if _esta_codespaces():
        return "codespaces"

    entorno = _normalizar_texto(obtener_variable("ICEBERG_ENTORNO", ""))

    if entorno:
        return entorno

    return "local"


def detectar_modo_local() -> bool:
    """
    Determina si la app debe comportarse como local.

    Regla de seguridad:
    Streamlit Cloud y Codespaces siempre son modo no local.
    """
    if _esta_streamlit_cloud() or _esta_codespaces():
        return False

    entorno = detectar_entorno()

    if entorno in ENTORNOS_REMOTOS:
        return False

    override = obtener_variable("ICEBERG_MODO_LOCAL", "")

    if str(override).strip():
        return _normalizar_bool(override, default=False)

    if entorno in ENTORNOS_LOCALES:
        return True

    return False


ICEBERG_ENTORNO = detectar_entorno()
MODO_LOCAL = detectar_modo_local()


def etiqueta_modo_ejecucion() -> str:
    """
    Etiqueta visible en la app.
    """
    entorno = detectar_entorno()
    modo_local = detectar_modo_local()

    if entorno in {"streamlit", "streamlit_cloud", "cloud", "produccion", "production"}:
        return "Produccion / Streamlit Cloud"

    if entorno in {"codespaces", "github_codespaces"}:
        return "Pruebas / Codespaces"

    if modo_local:
        return "Desarrollo local"

    return f"Entorno remoto ({entorno})"


def es_entorno_cloud() -> bool:
    """
    Retorna True si la app esta en entorno remoto.
    """
    return not detectar_modo_local()


def preparar_playwright_cloud() -> tuple[bool, str]:
    """
    Prepara Playwright en entornos cloud/remotos.

    En local no instala nada.
    En Streamlit Cloud o Codespaces intenta validar o instalar Chromium.
    """
    if detectar_modo_local():
        return True, "Entorno local: no se requiere preparar Playwright automaticamente."

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return False, f"Playwright no esta instalado o no se pudo importar: {exc}"

    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            navegador.close()

        return True, "Playwright esta disponible."

    except Exception as exc_inicial:
        try:
            proceso = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "playwright",
                    "install",
                    "chromium",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if proceso.returncode != 0:
                detalle = proceso.stderr.strip() or proceso.stdout.strip()
                return False, f"No fue posible instalar Chromium para Playwright: {detalle[-2000:]}"

            with sync_playwright() as p:
                navegador = p.chromium.launch(headless=True)
                navegador.close()

            return True, "Chromium de Playwright fue instalado correctamente."

        except Exception as exc_instalacion:
            return (
                False,
                "No fue posible preparar Playwright automaticamente: "
                f"{exc_instalacion}. Error inicial: {exc_inicial}"
            )
