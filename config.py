"""
Archivo: config.py
Descripción:
    Archivo central de configuración del proyecto.

    Aquí se definen:
    - Credenciales cargadas desde .env.
    - URLs de ICEBERG.
    - Reportes disponibles.
    - Periodos a descargar.
    - Carpeta de salida.
    - Timeouts.
    - Reintentos.
    - Configuración visual del navegador.

Importante:
    No escribir usuario ni contraseña directamente en este archivo.
    Las credenciales deben ir en el archivo .env.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Carga las variables del archivo .env.
# Ejemplo esperado:
# ICEBERG_USER=usuario
# ICEBERG_PASS=contraseña
load_dotenv()

ICEBERG_USER = os.getenv("ICEBERG_USER")
ICEBERG_PASS = os.getenv("ICEBERG_PASS")

# URLs principales de ICEBERG.
URL_LOGIN = "https://sig.cun.edu.co/icebergrs/"
URL_BASE = "https://sig.cun.edu.co/icebergrs/"
URL_REPORT_LIST = "https://sig.cun.edu.co/icebergrs/reportList.action?groupId=744427"

# Diccionario maestro de reportes disponibles.
# Cada clave representa un reporte que puede ser usado en REPORTES_A_DESCARGAR.
REPORTES_DISPONIBLES = {
    "matriculados_grupo_periodo": {
        "nombre": "Estudiantes_Matriculados",
        "report_id": "1947224",
        "url_reporte": "https://sig.cun.edu.co/icebergrs/reportDetail.action?reportId=1947224",
        "usar_boton_ok": True,
        "timeout_excel_ms": 120000,
        "timeout_descarga_ms": 120000,
        "reintentos": 3,
    },
    "ocupacion_docente": {
        "nombre": "Ocupacion_Docentes",
        "report_id": "27815",
        "url_reporte": "https://sig.cun.edu.co/icebergrs/reportDetail.action?reportId=27815",
        "usar_boton_ok": True,
        "timeout_excel_ms": 120000,
        "timeout_descarga_ms": 120000,
        "reintentos": 3,
    },
    "Estudiantes_con_pago_matricula_y_datos_de_contacto": {
        "nombre": "Estudiantes con pago, matricula y datos de contacto",
        "report_id": "2603827",
        "url_reporte": "https://sig.cun.edu.co/icebergrs/reportDetail.action?reportId=2603827",
        "usar_boton_ok": True,
        "timeout_excel_ms": 120000,
        "timeout_descarga_ms": 120000,
        "reintentos": 3,
    },
    "Estudiantes_con_pago_matricula_sin_Inscribir_Matricula": {
        "nombre": "Estudiantes con Pago sin Inscribir Matricula",
        "report_id": "50210",
        "url_reporte": "https://sig.cun.edu.co/icebergrs/reportDetail.action?reportId=50210",
        "usar_boton_ok": True,
        "timeout_excel_ms": 120000,
        "timeout_descarga_ms": 120000,
        "reintentos": 3,
    }
}

# Lista base de periodos a consultar.
# Para cambiar el alcance de la ejecución, agregar o quitar periodos aquí.

# Periodos por defecto si el proyecto se ejecuta desde consola
PERIODOS_BASE_DEFAULT = [
    "26T03", "26P03", "26V03", "26V02", "26T02", "26P02",
    "2026B", "26ET2", "26ES2", "26ES3", "2026Q",
    "26I02", "26I03", "26PI2", "26PI3"
]

# Periodos enviados desde Streamlit.
# Ejemplo:
# ICEBERG_PERIODOS=2026C,26V03,26P03
PERIODOS_ENV = os.getenv("ICEBERG_PERIODOS")

if PERIODOS_ENV:
    PERIODOS_BASE = [
        periodo.strip()
        for periodo in PERIODOS_ENV.split(",")
        if periodo.strip()
    ]
else:
    PERIODOS_BASE = PERIODOS_BASE_DEFAULT




# Reportes que realmente se ejecutarán.
# El operador ** desempaqueta toda la configuración del reporte seleccionado
# y luego se agrega la lista de periodos.
#
# Ejemplo:
# **REPORTES_DISPONIBLES["ocupacion_docente"]
# equivale a copiar todas las claves del reporte ocupacion_docente.
REPORTES_A_DESCARGAR = [
    {
        **REPORTES_DISPONIBLES["ocupacion_docente"],
        "periodos": PERIODOS_BASE
    }
]

# Timestamp único por ejecución.
# Sirve para crear carpetas y logs separados por cada corrida.
TIMESTAMP_EJECUCION = datetime.now().strftime("%Y_%m_%d_%H_%M")

# Carpetas de salida.
CARPETA_BASE = "./descargas_iceberg"
CARPETA_ICEBERG = "iceberg"
CARPETA_DESCARGAS = os.path.join(CARPETA_BASE, f"{CARPETA_ICEBERG}_{TIMESTAMP_EJECUCION}")
TXT_LOG_PATH = os.path.join(CARPETA_DESCARGAS, f"Log_Iceberg_{TIMESTAMP_EJECUCION}.log")

# False: ejecuta Chromium oculto.
# True: muestra el navegador. Útil para depurar login, botones o carga de reportes.
MOSTRAR_NAVEGADOR = False

# Tamaño de la ventana del navegador controlado por Playwright.
VIEWPORT_CONFIG = {"width": 1366, "height": 768}

# Activa o desactiva escritura de logs en archivo.
LOG_ACTIVO = True

# Timeouts globales.
# Se expresan en milisegundos.
UI_TIMEOUT_MS = 60000
OK_CLICK_TIMEOUT_MS = 90000
REPORTE_GENERACION_TIMEOUT_MS = 100000
EXCEL_LINK_TIMEOUT_MS = 100000
DOWNLOAD_TIMEOUT_MS = 100000

# Reintentos globales por periodo.
REINTENTOS_PERIODO = 3

# Pausa entre reintentos.
RETRY_DELAY_SECONDS = 8
