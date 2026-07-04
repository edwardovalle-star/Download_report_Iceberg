"""
Parche opcional para Streamlit Cloud.

Uso sugerido:
1. Copiar este archivo como cloud_runtime.py en la raíz del proyecto.
2. En app.py, antes de validar credenciales o lanzar Playwright, importar y ejecutar:

   from cloud_runtime import preparar_playwright_cloud
   preparar_playwright_cloud()

Este parche intenta descargar Chromium si el navegador de Playwright no existe.
No instala dependencias Linux; esas van en packages.txt.
"""

import os
import subprocess
import sys
from pathlib import Path


def preparar_playwright_cloud() -> None:
    entorno = os.getenv("ICEBERG_ENTORNO", "").strip().lower()

    if entorno not in {"streamlit_cloud", "streamlit", "cloud"}:
        return

    marcador = Path.home() / ".cache" / "iceberg_playwright_chromium_ok.txt"

    if marcador.exists():
        return

    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            text=True,
        )
        marcador.parent.mkdir(parents=True, exist_ok=True)
        marcador.write_text("ok", encoding="utf-8")
    except Exception as e:
        raise RuntimeError(
            "No fue posible preparar Chromium de Playwright en Streamlit Cloud. "
            "Revisa packages.txt y los logs de despliegue."
        ) from e
