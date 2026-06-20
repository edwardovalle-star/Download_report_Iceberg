import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ICEBERG_USER = os.getenv("ICEBERG_USER")
ICEBERG_PASS = os.getenv("ICEBERG_PASS")

URL_LOGIN = "https://sig.cun.edu.co/icebergrs/"
URL_BASE = "https://sig.cun.edu.co/icebergrs/"
URL_REPORT_LIST = "https://sig.cun.edu.co/icebergrs/reportList.action?groupId=744427"

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

PERIODOS_BASE = [
     "26T03", "26P03", "26V03", "26V02", "26T02", "26P02", "2026B", "26ET2","26ES2","26ES3","2026Q","26I02","26I03","26PI2","26PI3"
]
#        "periodos": ["2026A", "2026B", "2026Q", "26ES2", "26I02", "26P01", "26P01", "26T01", "26T02", "26V01", "26V02", "26ET1" , "26ES1" "26PI2", "26I02"
#	     "periodos": ["26T01", "26P01", "26V01", "26V02", "26T02", "26P02", "2026A", "2026B"]
#        "periodos": ["25V06", "25T06", "25P06", "26V01", "26T01", "26P01", "2026A", "26V02", "26T02", "26P02", "2026B"],
#        "periodos": ["25V06", "25T06", "25P06", "26V01", "26T01", "26P01", "2026A"],
REPORTES_A_DESCARGAR = [
    {
        **REPORTES_DISPONIBLES["ocupacion_docente"],
        "periodos": PERIODOS_BASE
    }
]

TIMESTAMP_EJECUCION = datetime.now().strftime("%Y_%m_%d_%H_%M")
CARPETA_BASE = "./descargas_iceberg"
CARPETA_ICEBERG = "iceberg"
CARPETA_DESCARGAS = os.path.join(CARPETA_BASE, f"{CARPETA_ICEBERG}_{TIMESTAMP_EJECUCION}")
TXT_LOG_PATH = os.path.join(CARPETA_DESCARGAS, f"Log_Iceberg_{TIMESTAMP_EJECUCION}.log")

MOSTRAR_NAVEGADOR = False
VIEWPORT_CONFIG = {"width": 1366, "height": 768}
LOG_ACTIVO = True

UI_TIMEOUT_MS = 60000
OK_CLICK_TIMEOUT_MS = 90000
REPORTE_GENERACION_TIMEOUT_MS = 100000
EXCEL_LINK_TIMEOUT_MS = 100000
DOWNLOAD_TIMEOUT_MS = 100000
REINTENTOS_PERIODO = 3
RETRY_DELAY_SECONDS = 8