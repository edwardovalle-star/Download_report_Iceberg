"""
Archivo: 1_Descargar.py
Descripción:
    Automatiza la descarga de reportes desde ICEBERG usando Playwright.

Requisitos:
    - Tener configurado .env con ICEBERG_USER e ICEBERG_PASS.
    - Tener Playwright instalado.
    - Haber instalado Chromium con: python -m playwright install chromium.

Salida:
    - Archivos .xls descargados por periodo.
    - Archivo .log de ejecución.
    - Capturas .png si ocurre un error.
"""

import time
import os
import shutil
import sys
from datetime import datetime
import config
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Validación temprana de credenciales.
# Evita abrir navegador si el .env no está configurado.
if not getattr(config, 'ICEBERG_USER', None) or not getattr(config, 'ICEBERG_PASS', None):
    print("❌ ERROR CRÍTICO: No se encontraron las credenciales (USUARIO/PASSWORD) en config.py")
    print("   Asegúrate de tener un archivo .env con ICEBERG_USER e ICEBERG_PASS")
    exit()


def preparar_carpeta_descargas():
    """Crea la carpeta base de descargas y elimina ejecuciones antiguas."""
    if not os.path.exists(config.CARPETA_BASE):
        os.makedirs(config.CARPETA_BASE)
        print(f"📁 Carpeta base creada: {config.CARPETA_BASE}")

    carpetas_existentes = []
    if os.path.exists(config.CARPETA_BASE):
        for item in os.listdir(config.CARPETA_BASE):
            ruta_completa = os.path.join(config.CARPETA_BASE, item)
            if os.path.isdir(ruta_completa) and item.startswith(config.CARPETA_ICEBERG):
                carpetas_existentes.append((ruta_completa, os.path.getctime(ruta_completa)))

    # Ordena por fecha de creación para eliminar las más antiguas.
    carpetas_existentes.sort(key=lambda x: x[1])

    limite_carpetas = 9
    if len(carpetas_existentes) > limite_carpetas:
        carpetas_a_eliminar = carpetas_existentes[:-limite_carpetas]
        print(f"🗑️  Limpiando {len(carpetas_a_eliminar)} carpeta(s) antigua(s)...")
        for carpeta, _ in carpetas_a_eliminar:
            try:
                shutil.rmtree(carpeta)
                print(f"   ✓ Eliminada: {os.path.basename(carpeta)}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {carpeta}: {e}")

    if not os.path.exists(config.CARPETA_DESCARGAS):
        os.makedirs(config.CARPETA_DESCARGAS)
        print(f"[*] Carpeta de descarga creada: {config.CARPETA_DESCARGAS}")


def log_mensaje(mensaje: str):
    """Imprime mensajes en consola y opcionalmente los guarda en archivo .log."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    texto_completo = f"[{timestamp}] {mensaje}"
    print(texto_completo)

    if getattr(config, 'LOG_ACTIVO', True):
        try:
            with open(config.TXT_LOG_PATH, mode='a', encoding='utf-8') as log_file:
                log_file.write(texto_completo + "\n")
        except Exception as e:
            print(f"Error escribiendo log: {e}")


def iniciar_navegador(p) -> tuple[Browser, BrowserContext, Page]:
    """Inicializa Chromium con Playwright."""
    log_mensaje("🚀 Lanzando navegador...")

    # headless=True ejecuta el navegador oculto.
    # headless=False permite ver la navegación en pantalla.
    browser = p.chromium.launch(headless=not config.MOSTRAR_NAVEGADOR)

    context = browser.new_context(
        viewport=config.VIEWPORT_CONFIG,
        accept_downloads=True
    )

    page = context.new_page()
    page.set_default_timeout(config.UI_TIMEOUT_MS)
    return browser, context, page


def take_screenshot(page: Page, name: str):
    """Guarda una captura de pantalla para diagnóstico de errores."""
    try:
        safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip()
        filename = f"{safe_name}.png"
        path = os.path.join(config.CARPETA_DESCARGAS, filename)
        page.screenshot(path=path)
    except Exception:
        # No se detiene la ejecución si falla la captura.
        pass


def realizar_login(page: Page) -> bool:
    """Realiza login en ICEBERG."""
    try:
        log_mensaje("🔐 Iniciando sesión en Iceberg...")
        page.goto(config.URL_LOGIN, wait_until="domcontentloaded")

        page.locator("#userName").fill(config.ICEBERG_USER or "")
        page.locator('input[name="password"]').fill(config.ICEBERG_PASS or "")
        page.get_by_role("button", name="Login").click()

        page.wait_for_load_state("networkidle")
        log_mensaje("✅ Login completado.")
        return True
    except Exception as e:
        log_mensaje(f"❌ Error Login: {e}")
        take_screenshot(page, "error_login")
        sys.exit(1)


def navegar_a_reporte(page: Page, reporte_config: dict):
    """Abre la URL directa del reporte configurado."""
    url_reporte = reporte_config["url_reporte"]
    page.goto(url_reporte, wait_until="domcontentloaded")


def esperar_link_excel(page: Page, timeout_ms: int):
    """Espera hasta que el enlace Excel esté visible."""
    excel_link = page.get_by_role("link", name="Excel")
    excel_link.wait_for(state="visible", timeout=timeout_ms)
    return excel_link


def descargar_reporte_periodo(page: Page, nombre_tarea: str, periodo: str, reporte_config: dict):
    """Selecciona un periodo, genera el reporte y descarga el archivo Excel."""
    page.wait_for_load_state("domcontentloaded")

    combo = page.get_by_role("combobox")
    combo.wait_for(state="visible", timeout=config.UI_TIMEOUT_MS)
    combo.select_option(periodo)

    if reporte_config.get("usar_boton_ok", True):
        log_mensaje("     Generando reporte...")
        boton_ok = page.get_by_role("button", name="Ok")
        boton_ok.wait_for(state="visible", timeout=config.UI_TIMEOUT_MS)

        try:
            # no_wait_after=True evita esperar una navegación completa,
            # porque ICEBERG puede generar el reporte sin cambiar totalmente de página.
            boton_ok.click(timeout=config.OK_CLICK_TIMEOUT_MS, no_wait_after=True)
        except Exception as e:
            log_mensaje(f"     ⚠️ Click normal en Ok falló: {e}")
            log_mensaje("     ↪ Intentando click por JavaScript...")

            # Fallback: fuerza el click desde JavaScript.
            # Útil cuando el botón existe, pero Playwright no lo considera interactuable.
            boton_ok.evaluate("el => el.click()")

    try:
        page.wait_for_load_state("networkidle", timeout=config.REPORTE_GENERACION_TIMEOUT_MS)
    except Exception as e:
        # No siempre ICEBERG llega a estado networkidle, por eso no se detiene el flujo.
        log_mensaje(f"     ⚠️ networkidle no confirmado: {e}")

    log_mensaje("     Esperando enlace Excel...")
    excel_link = esperar_link_excel(
        page,
        reporte_config.get("timeout_excel_ms", config.EXCEL_LINK_TIMEOUT_MS)
    )

    log_mensaje("     Descargando Excel...")

    # Playwright debe empezar a escuchar la descarga antes de hacer clic.
    # Por eso el click al enlace Excel va dentro del bloque expect_download.
    with page.expect_download(
        timeout=reporte_config.get("timeout_descarga_ms", config.DOWNLOAD_TIMEOUT_MS)
    ) as download_info:
        excel_link.click()

    download = download_info.value
    timestamp = datetime.now().strftime("%H%M%S")
    periodo_safe = periodo.replace("/", "-").strip()
    nombre_archivo = f"{nombre_tarea}_{periodo_safe}_{timestamp}.xls"
    path_final = os.path.join(config.CARPETA_DESCARGAS, nombre_archivo)
    download.save_as(path_final)

    log_mensaje(f"     🎉 Archivo guardado: {nombre_archivo}")


def procesar_periodo(page: Page, reporte_config: dict, periodo: str) -> bool:
    """Procesa un periodo con reintentos."""
    nombre_tarea = reporte_config["nombre"]
    max_reintentos = reporte_config.get("reintentos", config.REINTENTOS_PERIODO)

    for intento in range(1, max_reintentos + 1):
        try:
            log_mensaje(f"   > PERIODO : {periodo} | intento {intento}/{max_reintentos}")
            navegar_a_reporte(page, reporte_config)
            descargar_reporte_periodo(page, nombre_tarea, periodo, reporte_config)
            return True
        except Exception as e:
            log_mensaje(f"     ❌ Error en periodo {periodo} (intento {intento}): {e}")
            take_screenshot(page, f"error_{nombre_tarea}_{periodo}_intento_{intento}")

            if intento < max_reintentos:
                time.sleep(config.RETRY_DELAY_SECONDS)
                try:
                    page.goto(reporte_config["url_reporte"], wait_until="domcontentloaded")
                except Exception:
                    pass

    return False


def procesar_reporte(page: Page, reporte_config: dict) -> bool:
    """Procesa todos los periodos de un reporte."""
    nombre_tarea = reporte_config["nombre"]
    log_mensaje(f"--- Procesando tarea: {nombre_tarea} ---")

    lista_periodos = reporte_config.get("periodos", [])
    if not lista_periodos:
        log_mensaje("   ⚠️ No hay periodos configurados.")
        return False

    ok_total = True

    for periodo in lista_periodos:
        if page.is_closed():
            log_mensaje("   🛑 El navegador se ha cerrado inesperadamente.")
            sys.exit(1)

        exito = procesar_periodo(page, reporte_config, periodo)
        if not exito:
            ok_total = False

    return ok_total


def ejecutar_bot():
    """Orquesta la ejecución completa del bot."""
    log_mensaje("🤖 Iniciando Bot de Descarga Iceberg")
    log_mensaje(f"📂 Carpeta de descarga: {config.CARPETA_DESCARGAS}")

    with sync_playwright() as p:
        browser, context, page = iniciar_navegador(p)

        if realizar_login(page):
            for reporte in config.REPORTES_A_DESCARGAR:
                procesar_reporte(page, reporte)
                time.sleep(1)
        else:
            log_mensaje("🛑 Fin por error de login.")
            sys.exit(1)

        try:
            browser.close()
        except Exception:
            pass

        log_mensaje("🏁 Proceso de descarga finalizado.")


if __name__ == "__main__":
    preparar_carpeta_descargas()
    ejecutar_bot()
