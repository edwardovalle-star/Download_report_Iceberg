from __future__ import annotations

import os


ENTORNOS_LOCALES = {"local", "desarrollo", "dev", "windows"}
ENTORNOS_REMOTOS = {"streamlit", "streamlit_cloud", "cloud", "codespaces", "github_codespaces", "produccion", "production"}


def _normalizar_texto(valor: object, default: str = "") -> str:
    if valor is None:
        return default

    return str(valor).strip().lower()


def _normalizar_bool(valor: object, default: bool = False) -> bool:
    """
    Convierte valores de entorno tipo true/false, 1/0, si/no en booleano.
    """
    if valor is None:
        return default

    texto = _normalizar_texto(valor)

    if texto in {"1", "true", "yes", "y", "si", "s?", "on"}:
        return True

    if texto in {"0", "false", "no", "n", "off"}:
        return False

    return default


def _leer_streamlit_secret(nombre: str) -> str | None:
    """
    Intenta leer secrets de Streamlit sin obligar a que existan.
    Sirve para Streamlit Cloud.
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
    Lee primero variables de entorno y luego secrets de Streamlit.
    """
    valor = os.getenv(nombre)

    if valor is not None and str(valor).strip():
        return str(valor)

    valor_secret = _leer_streamlit_secret(nombre)

    if valor_secret is not None and str(valor_secret).strip():
        return str(valor_secret)

    return default


def detectar_entorno() -> str:
    """
    Detecta el entorno de ejecucion.

    Prioridad:
    1. ICEBERG_ENTORNO desde .env, entorno o secrets.
    2. Variable CODESPACES de GitHub Codespaces.
    3. Local por defecto.
    """
    entorno = _normalizar_texto(obtener_variable("ICEBERG_ENTORNO", ""))

    if entorno:
        return entorno

    if _normalizar_bool(os.getenv("CODESPACES"), False):
        return "codespaces"

    return "local"


def detectar_modo_local() -> bool:
    """
    Determina si la app debe comportarse como local.

    ICEBERG_MODO_LOCAL puede forzar true/false.
    Si no existe, se calcula desde ICEBERG_ENTORNO.
    """
    override = obtener_variable("ICEBERG_MODO_LOCAL", "")

    if str(override).strip():
        return _normalizar_bool(override, default=False)

    entorno = detectar_entorno()

    if entorno in ENTORNOS_REMOTOS:
        return False

    if entorno in ENTORNOS_LOCALES:
        return True

    return False


ICEBERG_ENTORNO = detectar_entorno()
MODO_LOCAL = detectar_modo_local()


def etiqueta_modo_ejecucion() -> str:
    """
    Etiqueta amigable para mostrar en la app.
    """
    if ICEBERG_ENTORNO in {"streamlit", "streamlit_cloud", "cloud", "produccion", "production"}:
        return "Produccion / Streamlit Cloud"

    if ICEBERG_ENTORNO in {"codespaces", "github_codespaces"}:
        return "Pruebas / Codespaces"

    if MODO_LOCAL:
        return "Desarrollo local"

    return f"Entorno remoto ({ICEBERG_ENTORNO})"


def es_entorno_cloud() -> bool:
    """
    Retorna True cuando la app corre en un entorno remoto donde no conviene
    usar funciones locales como abrir carpetas del sistema operativo.
    """
    entorno = detectar_entorno()

    if entorno in ENTORNOS_REMOTOS:
        return True

    if _normalizar_bool(os.getenv("CODESPACES"), False):
        return True

    return False


def preparar_playwright_cloud() -> tuple[bool, str]:
    """
    Prepara Playwright en entornos cloud/remotos.

    Esta funcion se mantiene por compatibilidad con app.py.
    En local no instala nada.
    En Streamlit Cloud / Codespaces intenta instalar Chromium si es necesario.

    Retorna:
    (True, mensaje) si todo esta bien o no aplica.
    (False, mensaje) si falla la preparacion.
    """
    import subprocess
    import sys

    if MODO_LOCAL:
        return True, "Entorno local: no se requiere preparacion automatica de Playwright."

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
                timeout=180,
            )

            if proceso.returncode != 0:
                mensaje_error = proceso.stderr.strip() or proceso.stdout.strip()
                return False, f"No fue posible instalar Chromium para Playwright: {mensaje_error}"

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

