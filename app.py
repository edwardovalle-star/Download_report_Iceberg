import os
import sys
import subprocess
import zipfile
from pathlib import Path
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st
import config
from cloud_runtime import (
    ICEBERG_ENTORNO,
    MODO_LOCAL as MODO_LOCAL_RUNTIME,
    etiqueta_modo_ejecucion as etiqueta_modo_ejecucion_runtime,
)
from resource_monitor import mostrar_diagnostico_tecnico_sidebar


from session_workspace import (
    inicializar_workspace_sesion,
    registrar_consolidado_sesion,
    mostrar_consolidados_sesion,
    mostrar_consolidado_activo_sesion,
)

from filter_workspace import (
    limpiar_resultado_filtro_si_cambia_consolidado,
    registrar_resultado_filtro_sesion,
    mostrar_resultado_filtro_sesion,
)

from advanced_filters import (
    aplicar_filtros_avanzados,
    construir_resumen_filtros_avanzados,
    mostrar_filtros_avanzados_opcionales,
)
def asegurar_chromium_playwright() -> tuple[bool, str]:
    """
    En Streamlit Cloud, pip instala la librería Playwright,
    pero no siempre descarga el navegador Chromium.

    Esta función descarga Chromium una sola vez por entorno.
    """
    if sync_playwright is None:
        return False, "Playwright no está instalado. Revisa requirements.txt."

    es_streamlit_cloud = (
        os.getenv("ICEBERG_ENTORNO", "").strip().lower() in {"streamlit_cloud", "streamlit", "cloud"}
        or Path("/mount/src").exists()
    )

    if not es_streamlit_cloud:
        return True, "No aplica instalación automática de Chromium fuera de Streamlit Cloud."

    marcador = Path.home() / ".cache" / "iceberg_playwright_chromium_ok.txt"

    if marcador.exists():
        return True, "Chromium de Playwright ya estaba preparado."

    try:
        resultado = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if resultado.returncode != 0:
            detalle = (resultado.stderr or resultado.stdout or "").strip()
            return False, (
                "No fue posible instalar Chromium de Playwright en Streamlit Cloud.\n\n"
                f"Detalle técnico:\n{detalle[-2000:]}"
            )

        marcador.parent.mkdir(parents=True, exist_ok=True)
        marcador.write_text("ok", encoding="utf-8")

        return True, "Chromium de Playwright fue instalado correctamente."

    except Exception as e:
        return False, f"No fue posible preparar Chromium de Playwright: {e}"



try:
    from cloud_runtime import preparar_playwright_cloud
    preparar_playwright_cloud()
except Exception as e:
    st.warning(f"No fue posible preparar Playwright automáticamente: {e}")

try:
    from playwright.sync_api import sync_playwright
except Exception:  # type: ignore
    sync_playwright = None

BASE_DIR = Path(__file__).resolve().parent
ICEBERG_LOGIN_URL = "https://sig.cun.edu.co/icebergrs/"

# Modo de ejecución:
# - true  : ejecución local en Windows. Habilita abrir carpeta/archivo.
# - false : ejecución web/servidor/Codespaces/Docker. Solo muestra descargas.
MODO_LOCAL = MODO_LOCAL_RUNTIME

# Etiqueta visual para que el usuario identifique dónde está corriendo.
ENTORNO_APP = os.getenv("ICEBERG_ENTORNO", "streamlit").strip().lower()

# Tiempo máximo de inactividad.
# En Streamlit no se cierra la pestaña del navegador, pero sí se invalida la sesión interna.
try:
    INACTIVIDAD_MINUTOS = int(os.getenv("ICEBERG_INACTIVIDAD_MINUTOS", "30"))
except ValueError:
    INACTIVIDAD_MINUTOS = 30

INACTIVIDAD_SEGUNDOS = max(INACTIVIDAD_MINUTOS, 0) * 60



PERIODOS_UI = [
    "27ES3", "27ES2", "27ES1",
    "26V06", "26V05", "26V04", "26V03", "26V02", "26V01",
    "26T06", "26T05", "26T04", "26T03", "26T02", "26T01",
    "26P06", "26P05", "26P04", "26P03", "26P02", "26P01",
    "26PI6", "26PI5", "26PI4", "26PI3", "26PI2", "26PI1",
    "26I06", "26I05", "26I04", "26I03", "26I02", "26I01",
    "26ET4", "26ET3", "26ET2", "26ET1",
    "26ES6", "26ES5", "26ES4", "26ES3", "26ES2", "26ES1",
    "2026D", "2026C", "2026B", "2026A", "2026Q",
]

# Mismas materias excluidas en el filtro histórico 3_Filtrar.py.
MATERIAS_EXCLUIDAS_HISTORICAS = [
    "TRABAJO DE INVESTIGACION EN INGENIERIA",
    "PLAN DE NEGOCIO APLICADO PARA ESCUELA DE INGENIERIA",
    "COMPRENSION Y PRODUCCION DE TEXTOS",
]


def etiqueta_modo_ejecucion() -> str:
    return etiqueta_modo_ejecucion_runtime()

def timestamp_actual() -> float:
    return datetime.now().timestamp()


def registrar_actividad() -> None:
    st.session_state["ultima_actividad_ts"] = timestamp_actual()


def minutos_desde_ultima_actividad() -> float:
    ultima = st.session_state.get("ultima_actividad_ts")

    if not ultima:
        return 0.0

    try:
        return max((timestamp_actual() - float(ultima)) / 60, 0.0)
    except Exception:
        return 0.0


def limpiar_claves_por_prefijo(prefijos: tuple[str, ...]) -> None:
    for clave in list(st.session_state.keys()):
        if any(str(clave).startswith(prefijo) for prefijo in prefijos):
            del st.session_state[clave]


def limpiar_busqueda(mensaje: str = "Búsqueda limpiada. Puedes iniciar una nueva consulta sin volver a validar credenciales.") -> None:
    """
    Limpia resultados, filtros y selección de archivos sin cerrar sesión.
    Mantiene usuario validado y credenciales en memoria para una nueva búsqueda.
    """
    limpiar_claves_por_prefijo(
        (
            "mensaje_archivos_",
            "tabla_archivos_",
            "periodos_academicos_",
            "dependencias_filtro_",
            "fechas_filtro_",
            "excluir_practica_",
            "excluir_historicas_",
            "capacidad_mayor_cero_",
            "inscritos_mayor_cero_",
        )
    )

    st.session_state["consolidado_path"] = None
    st.session_state["consolidado_origen"] = ""
    st.session_state["consolidado_activo_id"] = ""
    st.session_state["periodos_consolidado_activo"] = []
    st.session_state["fecha_consolidado_activo"] = ""
    st.session_state["archivo_consolidado_activo"] = ""
    st.session_state["carpeta_consolidado_activo"] = ""
    st.session_state["resumen_ejecucion_actual"] = None
    st.session_state["ultimo_error"] = ""
    st.session_state["ultima_ejecucion_ok"] = False
    st.session_state["busqueda_nonce"] = st.session_state.get("busqueda_nonce", 0) + 1
    st.session_state["filtro_nonce"] = st.session_state.get("filtro_nonce", 0) + 1
    st.session_state["mensaje_sesion"] = mensaje
    registrar_actividad()


def cerrar_sesion_completa(mensaje: str = "Sesión cerrada correctamente.") -> None:
    """
    Cierra la sesión interna de Streamlit y elimina credenciales guardadas en memoria.
    """
    for clave in list(st.session_state.keys()):
        del st.session_state[clave]

    st.session_state["mensaje_sesion"] = mensaje


def verificar_timeout_inactividad() -> None:
    """
    Si la sesión validada supera el tiempo de inactividad, se cierra automáticamente.
    La verificación ocurre cuando el usuario vuelve a interactuar con la app.
    """
    if INACTIVIDAD_SEGUNDOS <= 0:
        return

    if not st.session_state.get("login_validado"):
        return

    ultima = st.session_state.get("ultima_actividad_ts")

    if not ultima:
        registrar_actividad()
        return

    try:
        segundos_inactivos = timestamp_actual() - float(ultima)
    except Exception:
        registrar_actividad()
        return

    if segundos_inactivos >= INACTIVIDAD_SEGUNDOS:
        cerrar_sesion_completa(
            f"La sesión fue cerrada automáticamente por inactividad superior a {INACTIVIDAD_MINUTOS} minutos."
        )
        st.rerun()



def inicializar_estado():
    defaults = {
        "login_validado": False,
        "iceberg_user": "",
        "iceberg_pass": "",
        "consolidado_path": None,
        "consolidado_origen": "",
        "ultimo_error": "",
        "ultima_ejecucion_ok": False,
        "ultima_actividad_ts": timestamp_actual(),
        "busqueda_nonce": 0,
        "filtro_nonce": 0,
        "mensaje_sesion": "",
        "resumen_ejecucion_actual": None,
    }

    for clave, valor in defaults.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def aplicar_estilos():
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        .ice-card {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin: 0.8rem 0 1rem 0;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        }

        .ice-ok {border-left: 6px solid #16a34a;}
        .ice-warn {border-left: 6px solid #f59e0b;}
        .ice-error {border-left: 6px solid #dc2626;}

        .ice-muted {
            color: #6b7280;
            font-size: 0.92rem;
        }

        .ice-table-title {
            font-weight: 750;
            font-size: 1.02rem;
            color: #111827;
            margin: 0.55rem 0 0.15rem 0;
        }

        .ice-section-note {
            color: #64748b;
            font-size: 0.90rem;
            margin-bottom: 0.35rem;
        }

        /* Botones generales */
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px !important;
            border: 1px solid #cbd5e1 !important;
            background: #ffffff !important;
            color: #1f2937 !important;
            font-weight: 650 !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
            transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: #94a3b8 !important;
            box-shadow: 0 4px 10px rgba(15, 23, 42, 0.12);
            transform: translateY(-1px);
        }

        .stButton > button:active,
        .stDownloadButton > button:active {
            transform: translateY(0);
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.10);
        }

        /* Boton primario */
        button[kind="primary"] {
            background: #dc2626 !important;
            color: #ffffff !important;
            border-color: #dc2626 !important;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.22) !important;
        }

        button[kind="primary"]:hover {
            background: #b91c1c !important;
            border-color: #b91c1c !important;
            box-shadow: 0 4px 12px rgba(185, 28, 28, 0.24) !important;
        }

        /* Labels de widgets */
        label[data-testid="stWidgetLabel"] p {
            font-weight: 650 !important;
            color: #334155 !important;
        }

        /* Expanders */
        details {
            border-color: #d7dee8 !important;
            border-radius: 10px !important;
        }

        details summary {
            font-weight: 650 !important;
            color: #1f2937 !important;
        }

        /* DataFrames */
        div[data-testid="stDataFrame"] {
            border: 1px solid #d7dee8;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        div[data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
            --gdg-border-color: rgba(100, 116, 139, 0.28) !important;
            --gdg-horizontal-border-color: rgba(100, 116, 139, 0.22) !important;
            --gdg-bg-header: rgba(241, 245, 249, 1) !important;
            --gdg-bg-header-hovered: rgba(226, 232, 240, 1) !important;
            --gdg-text-header: #111827 !important;
            --gdg-header-font-style: 700 14px !important;
            --gdg-base-font-style: 400 14px !important;
            --gdg-cell-horizontal-padding: 8px !important;
            --gdg-cell-vertical-padding: 3px !important;
        }

        /* Inputs compactos */
        div[data-baseweb="select"] {
            border-radius: 10px !important;
        }

        /* --- INICIO TABLAS VISIBLES ICEBERG --- */

        /* Contenedor general de tablas Streamlit */
        div[data-testid="stDataFrame"] {
            border: 1px solid #94a3b8 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
        }

        div[data-testid="stDataFrameResizable"] {
            border: 1px solid #94a3b8 !important;
            border-radius: 10px !important;
        }

        /* Tabla interna tipo Glide Data Editor */
        div[data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
            /* Encabezado / primera fila */
            --gdg-bg-header: #e2e8f0 !important;
            --gdg-bg-header-hovered: #cbd5e1 !important;
            --gdg-bg-header-has-focus: #cbd5e1 !important;
            --gdg-text-header: #0f172a !important;
            --gdg-text-header-selected: #ffffff !important;
            --gdg-header-font-style: 700 14px "Source Sans", sans-serif !important;

            /* Celdas */
            --gdg-text-dark: #111827 !important;
            --gdg-text-medium: #334155 !important;
            --gdg-base-font-style: 400 14px "Source Sans", sans-serif !important;

            /* Separacion visual de columnas y filas */
            --gdg-border-color: rgba(71, 85, 105, 0.55) !important;
            --gdg-horizontal-border-color: rgba(71, 85, 105, 0.45) !important;
            --gdg-drilldown-border: rgba(71, 85, 105, 0.35) !important;

            /* Fondo */
            --gdg-bg-cell: #ffffff !important;
            --gdg-bg-cell-medium: #f8fafc !important;
            --gdg-bg-group-header: #e2e8f0 !important;
            --gdg-bg-group-header-hovered: #cbd5e1 !important;

            /* Mantener compacto */
            --gdg-cell-horizontal-padding: 8px !important;
            --gdg-cell-vertical-padding: 3px !important;
        }

        /* Tablas HTML generadas por st.table, si existen */
        div[data-testid="stTable"] table {
            border-collapse: collapse !important;
            border: 1px solid #94a3b8 !important;
            width: 100% !important;
        }

        div[data-testid="stTable"] thead tr th {
            background: #e2e8f0 !important;
            color: #0f172a !important;
            font-weight: 700 !important;
            border: 1px solid #94a3b8 !important;
            padding: 0.35rem 0.5rem !important;
        }

        div[data-testid="stTable"] tbody tr td {
            border: 1px solid #cbd5e1 !important;
            color: #1f2937 !important;
            padding: 0.32rem 0.5rem !important;
        }

        div[data-testid="stTable"] tbody tr:nth-child(even) td {
            background: #f8fafc !important;
        }

        /* Titulos auxiliares */
        .ice-table-title {
            font-weight: 750 !important;
            font-size: 1.04rem !important;
            color: #0f172a !important;
            margin: 0.6rem 0 0.25rem 0 !important;
        }

        .ice-section-note {
            color: #475569 !important;
            font-size: 0.91rem !important;
            margin-bottom: 0.4rem !important;
        }

        /* --- FIN TABLAS VISIBLES ICEBERG --- */


        /* --- INICIO GRID FILTROS AVANZADOS ICEBERG --- */

        .ice-filter-grid-header {
            display: grid;
            grid-template-columns: 1.55fr 1.25fr 2.60fr 0.70fr;
            gap: 0.75rem;
            margin: 0.55rem 0 0.35rem 0;
            align-items: center;
        }

        .ice-filter-grid-header div {
            background: #e2e8f0;
            color: #0f172a;
            font-weight: 750;
            font-size: 0.90rem;
            padding: 0.42rem 0.65rem;
            border: 1px solid #94a3b8;
            border-radius: 9px;
            line-height: 1.1rem;
        }

        .ice-filter-row-label {
            color: #475569;
            font-size: 0.78rem;
            font-weight: 700;
            margin: 0.25rem 0 0.15rem 0;
        }

        .ice-filter-row-separator {
            height: 1px;
            background: linear-gradient(
                90deg,
                rgba(148, 163, 184, 0.15),
                rgba(148, 163, 184, 0.75),
                rgba(148, 163, 184, 0.15)
            );
            margin: 0.28rem 0 0.35rem 0;
        }

        /* Celdas visuales de la grilla de filtros avanzados */
        div[class*="st-key-adv_campo_"],
        div[class*="st-key-adv_operador_"],
        div[class*="st-key-adv_valores_"],
        div[class*="st-key-adv_valor_texto_"],
        div[class*="st-key-adv_valor_numero_"],
        div[class*="st-key-btn_quitar_filtro_"] {
            background: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 11px !important;
            padding: 0.34rem 0.42rem !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        div[class*="st-key-adv_campo_"]:hover,
        div[class*="st-key-adv_operador_"]:hover,
        div[class*="st-key-adv_valores_"]:hover,
        div[class*="st-key-adv_valor_texto_"]:hover,
        div[class*="st-key-adv_valor_numero_"]:hover {
            border-color: #94a3b8 !important;
            background: #f1f5f9 !important;
        }

        /* Reduce el ruido visual de labels internos cuando usamos encabezado propio */
        div[class*="st-key-adv_campo_"] label,
        div[class*="st-key-adv_operador_"] label,
        div[class*="st-key-adv_valores_"] label,
        div[class*="st-key-adv_valor_texto_"] label,
        div[class*="st-key-adv_valor_numero_"] label {
            margin-bottom: 0.15rem !important;
        }

        /* Boton quitar dentro de celda */
        div[class*="st-key-btn_quitar_filtro_"] button {
            width: 100%;
            min-height: 2.45rem;
        }

        /* --- FIN GRID FILTROS AVANZADOS ICEBERG --- */


        /* --- INICIO ESTILO GLIDE DATAFRAME ICEBERG --- */

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(148, 163, 184, 0.52) !important;
            border-radius: 16px !important;
            overflow: hidden !important;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07) !important;
            background: rgba(255,255,255,0.82) !important;
        }

        div[data-testid="stDataFrameResizable"] {
            border: 1px solid rgba(148, 163, 184, 0.46) !important;
            border-radius: 14px !important;
        }

        div[data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
            --gdg-bg-header: rgba(15, 23, 42, 0.92) !important;
            --gdg-bg-header-hovered: rgba(30, 41, 59, 0.96) !important;
            --gdg-bg-header-has-focus: rgba(30, 41, 59, 0.96) !important;
            --gdg-text-header: #f8fafc !important;
            --gdg-text-header-selected: #ffffff !important;
            --gdg-header-font-style: 700 13px "Source Sans", sans-serif !important;

            --gdg-text-dark: #0f172a !important;
            --gdg-text-medium: #334155 !important;
            --gdg-base-font-style: 400 13px "Source Sans", sans-serif !important;

            --gdg-border-color: rgba(100, 116, 139, 0.42) !important;
            --gdg-horizontal-border-color: rgba(100, 116, 139, 0.34) !important;

            --gdg-bg-cell: #ffffff !important;
            --gdg-bg-cell-medium: #f8fafc !important;
            --gdg-bg-group-header: rgba(15, 23, 42, 0.92) !important;
            --gdg-bg-group-header-hovered: rgba(30, 41, 59, 0.96) !important;

            --gdg-cell-horizontal-padding: 9px !important;
            --gdg-cell-vertical-padding: 3px !important;
        }

        /* --- FIN ESTILO GLIDE DATAFRAME ICEBERG --- */


        /* --- INICIO TABLA HTML AGGRID ICEBERG --- */

        .ice-ag-panel {
            margin-top: 0.75rem;
            background: #ffffff;
            border: 1px solid #d7e0ea;
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
        }

        .ice-ag-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 13px 16px;
            background: #f8fbff;
            border-bottom: 1px solid #d7e0ea;
            color: #475569;
            font-size: 0.88rem;
        }

        .ice-ag-title {
            color: #102033;
            font-weight: 800;
            font-size: 0.94rem;
        }

        .ice-ag-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 5px 10px;
            background: #e0f2fe;
            color: #075985;
            border: 1px solid #bae6fd;
            font-weight: 750;
            font-size: 0.78rem;
            white-space: nowrap;
        }

        .ice-ag-grid-wrap {
            overflow-x: auto;
            background: #ffffff;
        }

        .ice-ag-table {
            width: 100%;
            min-width: 760px;
            border-collapse: separate;
            border-spacing: 0;
        }

        .ice-ag-table thead th {
            position: sticky;
            top: 0;
            z-index: 2;
            text-align: left;
            background: #e8f1fa;
            color: #075985;
            border-top: 1px solid #c7d2df;
            border-bottom: 1px solid #c7d2df;
            border-right: 1px solid #d7e0ea;
            padding: 12px 14px;
            font-size: 0.76rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-weight: 850;
            white-space: nowrap;
        }

        .ice-ag-table thead th:last-child {
            border-right: 0;
        }

        .ice-ag-table tbody td {
            padding: 11px 14px;
            font-size: 0.90rem;
            color: #1e293b;
            border-bottom: 1px solid #e7edf3;
            border-right: 1px solid #eef3f8;
            vertical-align: middle;
        }

        .ice-ag-table tbody td:last-child {
            border-right: 0;
        }

        .ice-ag-table tbody tr:nth-child(even) {
            background: #f8fbff;
        }

        .ice-ag-table tbody tr {
            transition: background 0.14s ease, box-shadow 0.14s ease;
        }

        .ice-ag-table tbody tr:hover {
            background: #eff8ff;
            box-shadow: inset 5px 0 0 #075985;
        }

        .ice-ag-index {
            color: #64748b;
            font-weight: 750;
            width: 58px;
            text-align: center;
        }

        .ice-ag-field {
            font-weight: 750;
            color: #0f172a;
        }

        .ice-ag-example {
            color: #334155;
            max-width: 620px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .ice-ag-count {
            font-weight: 800;
            color: #075985;
            text-align: right;
            white-space: nowrap;
        }

        @media (max-width: 860px) {
            .ice-ag-table {
                min-width: 0;
            }

            .ice-ag-table thead {
                display: none;
            }

            .ice-ag-table,
            .ice-ag-table tbody,
            .ice-ag-table tr,
            .ice-ag-table td {
                display: block;
                width: 100%;
            }

            .ice-ag-table tbody {
                display: grid;
                gap: 12px;
                padding: 12px;
                background: #f8fbff;
            }

            .ice-ag-table tbody tr {
                background: #ffffff !important;
                border: 1px solid #d7e0ea;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
            }

            .ice-ag-table tbody td {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 16px;
                border-right: 0;
                padding: 11px 13px;
                white-space: normal;
            }

            .ice-ag-table tbody td::before {
                content: attr(data-label);
                font-weight: 850;
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                color: #64748b;
            }

            .ice-ag-example {
                white-space: normal;
                text-align: right;
            }
        }

        /* --- FIN TABLA HTML AGGRID ICEBERG --- */

        </style>
        """,
        unsafe_allow_html=True,
    )

def limpiar_sesion_login():
    st.session_state["login_validado"] = False
    st.session_state["iceberg_user"] = ""
    st.session_state["iceberg_pass"] = ""
    st.session_state["consolidado_path"] = None
    st.session_state["ultimo_error"] = ""
    st.session_state["ultima_ejecucion_ok"] = False
    st.session_state["busqueda_nonce"] = st.session_state.get("busqueda_nonce", 0) + 1
    st.session_state["filtro_nonce"] = st.session_state.get("filtro_nonce", 0) + 1


def mostrar_sidebar():
    with st.sidebar:
        st.header("Estado")

        if st.session_state["login_validado"]:
            st.success("Login validado")
            st.write(f"Usuario: `{st.session_state['iceberg_user']}`")

            st.caption("Acciones de sesión")

            if st.button("Nueva búsqueda", key="btn_nueva_busqueda"):
                limpiar_busqueda()
                st.rerun()


            if st.button("Cerrar sesión", key="btn_cerrar_sesion"):
                cerrar_sesion_completa("Sesión cerrada manualmente.")
                st.rerun()
        else:
            st.warning("Login pendiente")

        if st.session_state.get("consolidado_path"):
            st.success("Consolidado disponible")
        else:
            st.info("Consolidado pendiente")

        st.divider()
        st.caption("Modo de ejecución")
        st.info(etiqueta_modo_ejecucion())

        if not MODO_LOCAL:
            st.caption("Las acciones de abrir carpeta/archivo se ocultan en modo web.")

        st.divider()
        st.caption("Seguridad de sesión")

        if INACTIVIDAD_SEGUNDOS > 0:
            st.write(f"Cierre automático: `{INACTIVIDAD_MINUTOS} min`")
            if st.session_state.get("login_validado"):
                st.caption(f"Última actividad hace {minutos_desde_ultima_actividad():.1f} min")
        else:
            st.write("Cierre automático: `desactivado`")

        st.divider()

        if st.session_state["ultima_ejecucion_ok"]:
            st.success("Última ejecución correcta")
        elif st.session_state["ultimo_error"]:
            st.error("Última ejecución con error")
        else:
            st.info("Sin ejecución reciente")


def validar_credenciales_iceberg(usuario: str, password: str) -> tuple[bool, str]:
    """
    Valida usuario y contrasena directamente contra ICEBERG.

    Regla:
    - Si el login sigue mostrando el formulario, se considera fallido.
    - Solo se considera exitoso si aparece una senal fuerte de sesion iniciada:
      logoff/logout/cerrar sesion o rutas internas de reportes.
    """
    if sync_playwright is None:
        return False, "Playwright no está instalado o no está disponible. Revisa requirements.txt."

    ok_chromium, mensaje_chromium = asegurar_chromium_playwright()

    if not ok_chromium:
        return False, mensaje_chromium

    usuario = usuario.strip()
    password = password.strip()

    if not usuario or not password:
        return False, "Debes ingresar usuario y contraseña de ICEBERG."

    browser = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                accept_downloads=False,
            )

            page = context.new_page()
            page.set_default_timeout(45000)

            page.goto(ICEBERG_LOGIN_URL, wait_until="domcontentloaded")

            if not page.locator("#userName").is_visible(timeout=10000):
                browser.close()
                return False, "No se encontró el campo de usuario en ICEBERG."

            page.locator("#userName").fill(usuario)
            page.locator('input[name="password"]').fill(password)

            try:
                page.get_by_role("button", name="Login").click(timeout=8000)
            except Exception:
                page.locator('input[type="submit"], button[type="submit"], button').first.click(timeout=8000)

            try:
                page.wait_for_load_state("domcontentloaded", timeout=20000)
            except Exception:
                pass

            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            try:
                page.wait_for_timeout(1500)
            except Exception:
                pass

            html = page.content().lower()
            url_actual = page.url.lower()

            sigue_en_login = False

            try:
                sigue_en_login = page.locator("#userName").is_visible(timeout=2000)
            except Exception:
                sigue_en_login = False

            indicadores_fallo = [
                "login fallido",
                "credenciales",
                "usuario o contraseña",
                "usuario o contrasena",
                "contraseña incorrecta",
                "contrasena incorrecta",
                "invalid",
                "incorrect",
                "authentication failed",
                "acceso denegado",
            ]

            tiene_mensaje_fallo = any(texto in html for texto in indicadores_fallo)

            indicadores_exito = [
                "logoff",
                "logout",
                "cerrar sesión",
                "cerrar sesion",
                "reportgroup.action",
                "reportdetail.action",
                "reportgroup",
                "groupid",
            ]

            tiene_senal_exito = (
                any(texto in html for texto in indicadores_exito)
                or any(texto in url_actual for texto in indicadores_exito)
            )

            browser.close()

            if sigue_en_login or tiene_mensaje_fallo:
                return False, "No fue posible iniciar sesión en ICEBERG. Revisa usuario y contraseña."

            if tiene_senal_exito:
                return True, "Credenciales validadas correctamente contra ICEBERG."

            return False, (
                "No se pudo confirmar el inicio de sesión en ICEBERG. "
                "Revisa usuario y contraseña e intenta nuevamente."
            )

    except Exception as e:
        if browser:
            try:
                browser.close()
            except Exception:
                pass

        return False, f"Error validando credenciales en ICEBERG: {e}"

def construir_env(periodos: list[str], reportes: list[str] | None = None) -> dict:
    env = os.environ.copy()

    # Evita errores de codificación con emojis o tildes en Windows.
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    # Variables que leen config.py y los scripts hijos.
    env["ICEBERG_USER"] = st.session_state["iceberg_user"]
    env["ICEBERG_PASS"] = st.session_state["iceberg_pass"]
    env["ICEBERG_PERIODOS"] = ",".join(periodos)
    env["ICEBERG_REPORTES"] = ",".join(reportes or ["ocupacion_docente"])

    return env

def resumir_error(logs: list[str]) -> str:
    texto = "\n".join(logs).lower()

    if "error login" in texto or "login fallido" in texto or "credenciales" in texto:
        return "No fue posible iniciar sesión en ICEBERG. Revisa usuario y contraseña."

    if "timeout" in texto:
        return "La operación tardó demasiado. Puede ser lentitud de ICEBERG, periodo sin datos o cambio en la página."

    if "no hay archivos para consolidar" in texto:
        return "No se encontraron archivos descargados para consolidar."

    if "no se encontraron carpetas" in texto:
        return "No se encontró carpeta de descarga."

    if "traceback" in texto:
        return "El script generó un error técnico. Revisa el detalle del log."

    return "El proceso terminó con error. Revisa el log mostrado."


def ejecutar_script(nombre_script: str, env: dict, titulo: str) -> tuple[bool, str]:
    """
    Ejecuta un script externo y muestra avance/logs en la interfaz.
    """
    st.subheader(titulo)

    ruta_script = BASE_DIR / nombre_script
    if not ruta_script.exists():
        mensaje = f"No se encontró el archivo requerido: {nombre_script}"
        st.error(mensaje)
        return False, mensaje

    progress = st.progress(0)
    status_box = st.empty()
    log_box = st.empty()
    logs = []

    try:
        proceso = subprocess.Popen(
            [sys.executable, nombre_script],
            cwd=BASE_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        for i, linea in enumerate(proceso.stdout, start=1):
            logs.append(linea)

            if i < 8:
                progress.progress(20)
            elif i < 25:
                progress.progress(45)
            elif i < 80:
                progress.progress(75)
            else:
                progress.progress(90)

            status_box.info("Proceso en ejecución. Recibiendo información del script...")
            log_box.code("".join(logs[-220:]))

        proceso.wait()
        progress.progress(100)

        if proceso.returncode == 0:
            status_box.success(f"{titulo} finalizado correctamente.")
            return True, ""

        mensaje = resumir_error(logs)
        status_box.error(mensaje)
        return False, mensaje

    except Exception as e:
        progress.progress(100)
        mensaje = f"Error ejecutando {nombre_script}: {e}"
        status_box.error(mensaje)
        return False, mensaje


def obtener_carpeta_mas_reciente() -> Path | None:
    base_descargas = BASE_DIR / "descargas_iceberg"

    if not base_descargas.exists():
        return None

    carpetas = [
        p for p in base_descargas.iterdir()
        if p.is_dir() and p.name.startswith("iceberg_")
    ]

    if not carpetas:
        return None

    return max(carpetas, key=lambda p: p.stat().st_ctime)


def buscar_consolidado_mas_reciente(carpeta: Path | None = None) -> Path | None:
    if carpeta is None:
        carpeta = obtener_carpeta_mas_reciente()

    if carpeta is None or not carpeta.exists():
        return None

    archivos = list(carpeta.glob("Consolidado_Final*.xlsx"))

    if not archivos:
        return None

    return max(archivos, key=lambda p: p.stat().st_ctime)


def detectar_columna(df: pd.DataFrame, candidatos: list[str], indice_respaldo: int | None = None) -> str:
    columnas_normalizadas = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for candidato in candidatos:
        llave = candidato.strip().lower()
        if llave in columnas_normalizadas:
            return columnas_normalizadas[llave]

    if indice_respaldo is not None and indice_respaldo < len(df.columns):
        return df.columns[indice_respaldo]

    raise ValueError(f"No se encontró columna. Candidatos: {candidatos}")


def serie_texto(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.strip()


def preparar_fechas_para_ui(serie: pd.Series) -> list[str]:
    fechas = []

    for valor in serie.dropna().unique():
        if str(valor).strip() == "":
            continue

        fecha = pd.to_datetime(valor, dayfirst=True, errors="coerce")

        if pd.notna(fecha):
            fechas.append(fecha.strftime("%d/%m/%Y"))
        else:
            fechas.append(str(valor).strip())

    return sorted(set(fechas))


def obtener_columnas_filtro(df: pd.DataFrame) -> dict:
    """
    Replica la lógica histórica de columnas:
    - Materia: columna G, índice 6.
    - Capacidad: columna M, índice 12.
    - Inscritos: columna N, índice 13.
    - Fecha: columna U, índice 20.
    - Dependencia: columna AO, índice 40.

    Se priorizan los nombres de columna correctos y se deja índice como respaldo.
    """
    return {
        "materia": detectar_columna(
            df,
            ["Nom_materia", "Materia", "Asignatura", "Nombre materia"],
            indice_respaldo=6,
        ),
        "capacidad": detectar_columna(
            df,
            ["Capacidad", "Num_capacidad"],
            indice_respaldo=12,
        ),
        "inscritos": detectar_columna(
            df,
            ["Inscritos", "Num_inscritos", "Matriculados"],
            indice_respaldo=13,
        ),
        "fecha": detectar_columna(
            df,
            ["Fec_inicio_grupo", "Fecha inicio grupo", "Fecha inicio", "Fec_inicio"],
            indice_respaldo=20,
        ),
        "dependencia": detectar_columna(
            df,
            ["Dependencia", "Nom_dependencia", "Nombre dependencia", "Escuela", "Programa", "Carrera"],
            indice_respaldo=40,
        ),
    }


def aplicar_filtro_con_diagnostico(
    df: pd.DataFrame,
    dependencias: list[str],
    fechas: list[str],
    excluir_practica: bool,
    excluir_materias_historicas: bool,
    capacidad_mayor_cero: bool,
    inscritos_mayor_cero: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    columnas = obtener_columnas_filtro(df)

    col_materia = columnas["materia"]
    col_capacidad = columnas["capacidad"]
    col_inscritos = columnas["inscritos"]
    col_fecha = columnas["fecha"]
    col_dependencia = columnas["dependencia"]

    condicion = pd.Series(True, index=df.index)
    pasos = []

    def agregar_paso(nombre: str, filas: int | None, detalle: str):
        pasos.append({"Paso": nombre, "Filas": filas, "Detalle": detalle})

    agregar_paso("Total consolidado", int(condicion.sum()), "Sin filtros")

    if dependencias:
        c = serie_texto(df[col_dependencia]).isin(dependencias)
        agregar_paso("Solo dependencia/carrera", int(c.sum()), ", ".join(dependencias))
        condicion &= c
        agregar_paso("Acumulado dependencia/carrera", int(condicion.sum()), "AND acumulado")

    if fechas:
        fechas_set = set(fechas)

        fechas_convertidas = pd.to_datetime(
            df[col_fecha],
            dayfirst=True,
            errors="coerce",
        ).dt.strftime("%d/%m/%Y")

        fechas_texto = serie_texto(df[col_fecha])

        c = fechas_convertidas.isin(fechas_set) | fechas_texto.isin(fechas_set)
        agregar_paso("Solo fecha", int(c.sum()), ", ".join(fechas))
        condicion &= c
        agregar_paso("Acumulado fecha", int(condicion.sum()), "AND acumulado")

    if excluir_practica:
        c = ~serie_texto(df[col_materia]).str.contains(
            "PRACTICA",
            case=False,
            regex=True,
            na=False,
        )
        agregar_paso("Solo no PRACTICA", int(c.sum()), "Materia no contiene PRACTICA")
        condicion &= c
        agregar_paso("Acumulado no PRACTICA", int(condicion.sum()), "AND acumulado")

    if excluir_materias_historicas:
        c = ~serie_texto(df[col_materia]).isin(MATERIAS_EXCLUIDAS_HISTORICAS)
        agregar_paso("Solo exclusiones históricas", int(c.sum()), "3 materias excluidas")
        condicion &= c
        agregar_paso("Acumulado exclusiones históricas", int(condicion.sum()), "AND acumulado")

    if capacidad_mayor_cero:
        capacidad = pd.to_numeric(df[col_capacidad], errors="coerce").fillna(0)
        c = capacidad != 0
        agregar_paso("Solo capacidad != 0", int(c.sum()), f"Columna: {col_capacidad}")
        condicion &= c
        agregar_paso("Acumulado capacidad", int(condicion.sum()), "AND acumulado")

    if inscritos_mayor_cero:
        inscritos = pd.to_numeric(df[col_inscritos], errors="coerce").fillna(0)
        c = inscritos != 0
        agregar_paso("Solo inscritos != 0", int(c.sum()), f"Columna: {col_inscritos}")
        condicion &= c
        agregar_paso("Acumulado inscritos", int(condicion.sum()), "AND acumulado")

    agregar_paso(
        "Columnas usadas",
        None,
        (
            f"Materia={col_materia} | Capacidad={col_capacidad} | "
            f"Inscritos={col_inscritos} | Fecha={col_fecha} | Dependencia={col_dependencia}"
        ),
    )

    df_filtrado = df[condicion].copy()
    df_diagnostico = pd.DataFrame(pasos)

    return df_filtrado, df_diagnostico, columnas


def convertir_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtrado")
    return buffer.getvalue()

def abrir_ruta_local(ruta: Path) -> tuple[bool, str]:
    """
    Abre una carpeta o ubica un archivo en el Explorador de Windows.

    - Si la ruta es carpeta: abre esa carpeta.
    - Si la ruta es archivo: abre la carpeta y selecciona el archivo.

    Nota:
    Esta acción funciona cuando Streamlit corre localmente en Windows.
    Si la app se despliega en un servidor, abriría la ruta en el servidor.
    """
    try:
        ruta = Path(ruta).resolve()

        if not ruta.exists():
            return False, f"No existe la ruta: {ruta}"

        if os.name != "nt":
            return False, "La apertura directa está pensada para Windows. Usa el botón de descarga."

        if ruta.is_dir():
            subprocess.Popen(["explorer", str(ruta)])
            return True, f"Se solicitó abrir la carpeta: {ruta}"

        if ruta.is_file():
            subprocess.Popen(["explorer", "/select,", str(ruta)])
            return True, f"Se solicitó abrir la ubicación del archivo: {ruta}"

        return False, f"La ruta no es archivo ni carpeta: {ruta}"

    except Exception as e:
        return False, f"No fue posible abrir la ruta: {e}"



def abrir_archivo_directo(ruta: Path) -> tuple[bool, str]:
    """
    Abre directamente un archivo con la aplicación predeterminada de Windows.

    Ejemplo:
    - .xlsx / .xls: Excel
    - .csv: Excel o editor asociado
    - .log: Bloc de notas u otro editor asociado
    """
    try:
        ruta = Path(ruta).resolve()

        if not ruta.exists():
            return False, f"No existe el archivo: {ruta}"

        if not ruta.is_file():
            return False, f"La ruta no es un archivo: {ruta}"

        if os.name != "nt":
            return False, "La apertura directa está pensada para Windows."

        os.startfile(str(ruta))
        return True, f"Se solicitó abrir el archivo: {ruta}"

    except Exception as e:
        return False, f"No fue posible abrir el archivo: {e}"


def clasificar_archivo(ruta: Path) -> str:
    """
    Clasifica los archivos para que el usuario final entienda mejor qué está viendo.
    """
    nombre = ruta.name.lower()

    if nombre.startswith("filtrado_dinamico"):
        return "Resultado filtrado"

    if nombre.startswith("consolidado_final"):
        return "Consolidado"

    if nombre.startswith("log_iceberg"):
        return "Log"

    if nombre.startswith("ocupacion_docentes"):
        return "Descarga original"

    return "Otro"


def prioridad_archivo(ruta: Path) -> tuple[int, float]:
    """
    Orden recomendado para usuario final:
    1. Filtrado Excel
    2. Filtrado CSV
    3. Consolidado Excel
    4. Consolidado CSV
    5. Descargas originales
    6. Logs
    7. Otros
    """
    nombre = ruta.name.lower()
    extension = ruta.suffix.lower()

    if nombre.startswith("filtrado_dinamico") and extension == ".xlsx":
        prioridad = 1
    elif nombre.startswith("filtrado_dinamico") and extension == ".csv":
        prioridad = 2
    elif nombre.startswith("consolidado_final") and extension == ".xlsx":
        prioridad = 3
    elif nombre.startswith("consolidado_final") and extension == ".csv":
        prioridad = 4
    elif nombre.startswith("ocupacion_docentes"):
        prioridad = 5
    elif nombre.startswith("log_iceberg"):
        prioridad = 6
    else:
        prioridad = 7

    # Dentro de cada categoría, primero el más reciente.
    return prioridad, -ruta.stat().st_mtime


def crear_zip_archivos(archivos: list[Path]) -> bytes:
    """
    Crea un ZIP en memoria con todos los archivos generados.
    """
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos:
            if archivo.exists() and archivo.is_file():
                zipf.write(archivo, arcname=archivo.name)

    return buffer.getvalue()


def obtener_mime_archivo(ruta: Path) -> str:
    extension = ruta.suffix.lower()

    if extension == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if extension == ".csv":
        return "text/csv"
    if extension == ".xls":
        return "application/vnd.ms-excel"
    if extension == ".log":
        return "text/plain"

    return "application/octet-stream"


def obtener_archivos_generados(carpeta: Path) -> list[Path]:
    if not carpeta or not carpeta.exists():
        return []

    extensiones = {".xls", ".xlsx", ".csv", ".log"}

    archivos = [
        p for p in carpeta.iterdir()
        if p.is_file()
        and p.suffix.lower() in extensiones
        and not p.name.startswith("~$")
    ]

    return sorted(archivos, key=prioridad_archivo)


def mostrar_archivos_generados(carpeta: Path, contexto: str = "principal"):
    """
    Panel único y compacto de archivos generados.

    En modo local:
    - Permite abrir carpeta.
    - Permite abrir ubicación del archivo.
    - Permite abrir archivo directamente.
    - Permite descargar archivo y ZIP.

    En modo web/servidor:
    - Oculta abrir carpeta/archivo.
    - Mantiene descargar archivo y ZIP.
    """
    archivos = obtener_archivos_generados(carpeta)

    if not archivos:
        st.info("Aún no hay archivos generados para mostrar.")
        return

    mensaje_key = f"mensaje_archivos_{contexto}"

    with st.expander("Archivos generados de la ejecución", expanded=False):
        st.caption(f"Carpeta de resultados: `{carpeta}`")

        if not MODO_LOCAL:
            st.info(
                "Modo web/servidor activo: las opciones de abrir carpeta o archivo se ocultan. "
                "Usa Descargar o Descargar ZIP."
            )

        total_archivos = len(archivos)
        total_kb = sum(p.stat().st_size for p in archivos) / 1024
        filtrados = sum(1 for p in archivos if clasificar_archivo(p) == "Resultado filtrado")
        originales = sum(1 for p in archivos if clasificar_archivo(p) == "Descarga original")

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Archivos", total_archivos)

        with m2:
            st.metric("Tamaño total", f"{total_kb:,.1f} KB")

        with m3:
            st.metric("Filtrados", filtrados)

        with m4:
            st.metric("Originales", originales)

        tabla = pd.DataFrame([
            {
                "Archivo": p.name,
                "Categoría": clasificar_archivo(p),
                "Tipo": p.suffix.lower(),
                "Tamaño KB": round(p.stat().st_size / 1024, 2),
                "Modificado": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "Ruta": str(p),
            }
            for p in archivos
        ])

        evento = st.dataframe(
            tabla.drop(columns=["Ruta"]),
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"tabla_archivos_{contexto}_{carpeta.name}",
        )

        filas_seleccionadas = []

        try:
            filas_seleccionadas = list(evento.selection.rows)
        except Exception:
            try:
                filas_seleccionadas = list(evento.get("selection", {}).get("rows", []))
            except Exception:
                filas_seleccionadas = []

        if filas_seleccionadas:
            indice = filas_seleccionadas[0]
        else:
            indice = 0

        ruta_sel = Path(tabla.iloc[indice]["Ruta"])

        st.caption(f"Archivo seleccionado: `{ruta_sel.name}`")

        if MODO_LOCAL:
            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:
                if st.button("Abrir carpeta", key=f"abrir_carpeta_{contexto}_{carpeta.name}"):
                    ok, mensaje = abrir_ruta_local(carpeta)
                    st.session_state[mensaje_key] = mensaje

                    if ok:
                        st.toast("Carpeta solicitada al Explorador de Windows.")
                    else:
                        st.toast("No se pudo abrir la carpeta.")

            with c2:
                if st.button("Abrir ubicación", key=f"abrir_ubicacion_{contexto}_{ruta_sel.name}_{ruta_sel.stat().st_mtime}"):
                    ok, mensaje = abrir_ruta_local(ruta_sel)
                    st.session_state[mensaje_key] = mensaje

                    if ok:
                        st.toast("Ubicación solicitada al Explorador de Windows.")
                    else:
                        st.toast("No se pudo abrir la ubicación.")

            with c3:
                if st.button("Abrir archivo", key=f"abrir_directo_{contexto}_{ruta_sel.name}_{ruta_sel.stat().st_mtime}"):
                    ok, mensaje = abrir_archivo_directo(ruta_sel)
                    st.session_state[mensaje_key] = mensaje

                    if ok:
                        st.toast("Archivo solicitado a Windows.")
                    else:
                        st.toast("No se pudo abrir el archivo.")

            with c4:
                st.download_button(
                    "Descargar",
                    data=ruta_sel.read_bytes(),
                    file_name=ruta_sel.name,
                    mime=obtener_mime_archivo(ruta_sel),
                    key=f"descargar_{contexto}_{ruta_sel.name}_{ruta_sel.stat().st_mtime}",
                )

            with c5:
                nombre_zip = f"ICEBERG_Resultados_{carpeta.name}.zip"

                st.download_button(
                    "Descargar ZIP",
                    data=crear_zip_archivos(archivos),
                    file_name=nombre_zip,
                    mime="application/zip",
                    key=f"descargar_zip_{contexto}_{carpeta.name}_{len(archivos)}",
                )

        else:
            c1, c2 = st.columns(2)

            with c1:
                st.download_button(
                    "Descargar archivo seleccionado",
                    data=ruta_sel.read_bytes(),
                    file_name=ruta_sel.name,
                    mime=obtener_mime_archivo(ruta_sel),
                    key=f"descargar_web_{contexto}_{ruta_sel.name}_{ruta_sel.stat().st_mtime}",
                )

            with c2:
                nombre_zip = f"ICEBERG_Resultados_{carpeta.name}.zip"

                st.download_button(
                    "Descargar ZIP completo",
                    data=crear_zip_archivos(archivos),
                    file_name=nombre_zip,
                    mime="application/zip",
                    key=f"descargar_zip_web_{contexto}_{carpeta.name}_{len(archivos)}",
                )

        if st.session_state.get(mensaje_key):
            st.info(st.session_state[mensaje_key])

        with st.expander("Ver ruta del archivo seleccionado", expanded=False):
            st.code(str(ruta_sel), language="text")


def mostrar_login():
    st.markdown(
        """
        <div class="ice-card ice-warn">
            <strong>Paso 1. Validar acceso a ICEBERG</strong><br>
            <span class="ice-muted">
            Primero se validan las credenciales. Si son correctas, se habilita la descarga.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_login"):
        usuario = st.text_input("Usuario ICEBERG")
        password = st.text_input("Contraseña ICEBERG", type="password")
        validar = st.form_submit_button("Validar credenciales")

    if validar:
        if not usuario.strip():
            st.error("Debes ingresar el usuario de ICEBERG.")
            return

        if not password.strip():
            st.error("Debes ingresar la contraseña de ICEBERG.")
            return

        with st.spinner("Validando acceso a ICEBERG..."):
            ok, mensaje = validar_credenciales_iceberg(usuario.strip(), password.strip())

        if ok:
            st.session_state["login_validado"] = True
            st.session_state["iceberg_user"] = usuario.strip()
            st.session_state["iceberg_pass"] = password.strip()
            st.session_state["ultimo_error"] = ""
            st.success(mensaje)
            st.rerun()

        st.session_state["ultimo_error"] = mensaje
        st.error(mensaje)



def obtener_reportes_ui() -> tuple[list[str], dict[str, str]]:
    """
    Construye las opciones visibles de reportes/formato desde config.REPORTES_DISPONIBLES.

    Retorna:
    - lista de etiquetas visibles para Streamlit
    - mapa etiqueta -> clave_reporte
    """
    reportes = getattr(config, "REPORTES_DISPONIBLES", {})

    opciones = []
    mapa = {}

    for clave, reporte in reportes.items():
        nombre = reporte.get("nombre", clave)
        etiqueta = f"{nombre} [{clave}]"
        opciones.append(etiqueta)
        mapa[etiqueta] = clave

    if not opciones:
        etiqueta = "Ocupacion_Docentes [ocupacion_docente]"
        opciones = [etiqueta]
        mapa[etiqueta] = "ocupacion_docente"

    return opciones, mapa

def mostrar_descarga():
    st.markdown(
        """
        <div class="ice-card ice-ok">
            <strong>Paso 2. Descargar y consolidar</strong><br>
            <span class="ice-muted">
            Selecciona el formato/reporte y los periodos. La app mostrará avances y errores durante la ejecución.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opciones_reportes, mapa_reportes = obtener_reportes_ui()
    nonce_busqueda = st.session_state.get("busqueda_nonce", 0)

    etiqueta_default = None
    for etiqueta, clave in mapa_reportes.items():
        if clave == "ocupacion_docente":
            etiqueta_default = etiqueta
            break

    indice_default = opciones_reportes.index(etiqueta_default) if etiqueta_default in opciones_reportes else 0

    with st.form("form_descarga"):
        reporte_etiqueta = st.selectbox(
            "Formato / reporte ICEBERG",
            opciones_reportes,
            index=indice_default,
            key=f"reporte_iceberg_{nonce_busqueda}",
        )

        periodos = st.multiselect(
            "Periodos académicos",
            PERIODOS_UI,
            key=f"periodos_academicos_{nonce_busqueda}",
        )

        ejecutar = st.form_submit_button("Descargar y consolidar")

    if ejecutar:
        if not periodos:
            st.error("Debes seleccionar al menos un periodo.")
            return

        reporte_clave = mapa_reportes.get(reporte_etiqueta, "ocupacion_docente")
        reporte_info = getattr(config, "REPORTES_DISPONIBLES", {}).get(reporte_clave, {})
        reporte_nombre = reporte_info.get("nombre", reporte_clave)

        st.session_state["ultimo_error"] = ""
        st.session_state["ultima_ejecucion_ok"] = False
        st.session_state["consolidado_path"] = None
        st.session_state["consolidado_origen"] = ""
        st.session_state["reporte_consolidado_activo"] = reporte_clave
        st.session_state["nombre_reporte_consolidado_activo"] = reporte_nombre

        env = construir_env(periodos, [reporte_clave])

        st.info("Proceso iniciado. No cierres esta pestaña hasta finalizar.")
        st.write("Formato/reporte enviado:", f"{reporte_nombre} [{reporte_clave}]")
        st.write("Periodos enviados:", periodos)

        ok_descarga, error_descarga = ejecutar_script(
            "1_Descargar.py",
            env,
            "Paso 2.1 - Descarga desde ICEBERG",
        )

        if not ok_descarga:
            st.session_state["ultimo_error"] = error_descarga
            st.error("No se continuará porque fallá la descarga.")
            return

        ok_consolidacion, error_consolidacion = ejecutar_script(
            "2_Consolidar.py",
            env,
            "Paso 2.2 - Consolidación",
        )

        if not ok_consolidacion:
            st.session_state["ultimo_error"] = error_consolidacion
            st.error("No se continuará porque fallá la consolidación.")
            return

        consolidado = buscar_consolidado_mas_reciente()

        if not consolidado:
            mensaje = "La consolidación terminó, pero no se encontró Consolidado_Final*.xlsx."
            st.session_state["ultimo_error"] = mensaje
            st.error(mensaje)
            return

        st.session_state["consolidado_path"] = str(consolidado)
        st.session_state["consolidado_origen"] = "descarga"
        st.session_state["periodos_consolidado_activo"] = periodos
        st.session_state["fecha_consolidado_activo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["archivo_consolidado_activo"] = consolidado.name
        st.session_state["carpeta_consolidado_activo"] = str(consolidado.parent)
        st.session_state["ultima_ejecucion_ok"] = True

        mensaje_ok = (
            "Descarga y consolidacion finalizada correctamente. "
            f"Reporte: {reporte_nombre} [{reporte_clave}]."
        )

        registrar_consolidado_sesion(
            consolidado_path=consolidado,
            periodos=periodos,
            origen="descarga",
            mensaje=mensaje_ok,
        )

        st.session_state["resumen_ejecucion_actual"] = construir_resumen_ejecucion_actual(
            estado="OK",
            origen="descarga",
            periodos=periodos,
            consolidado_path=consolidado,
            mensaje=mensaje_ok,
        )

        st.success("Descarga y consolidación finalizadas. Ya puedes filtrar.")
        st.rerun()

def mostrar_panel_filtrado(consolidado_path: Path):
    st.divider()
    st.markdown(
        """
        <div class="ice-card ice-ok">
            <strong>Paso 3. Filtrar desde datos reales del consolidado</strong><br>
            <span class="ice-muted">
            Las dependencias/carreras y fechas se cargan directamente desde el archivo consolidado.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    limpiar_resultado_filtro_si_cambia_consolidado(consolidado_path)

    st.caption(f"Consolidado detectado: `{consolidado_path}`")

    try:
        df = pd.read_excel(consolidado_path, engine="openpyxl")
    except Exception as e:
        st.error(f"No fue posible leer el consolidado: {e}")
        return

    periodos_base = st.session_state.get("periodos_consolidado_activo", [])
    periodos_texto = ", ".join(periodos_base) if isinstance(periodos_base, list) else str(periodos_base)

    if periodos_texto:
        st.info(
            f"Consolidado cargado: {len(df):,} filas y {len(df.columns):,} columnas. "
            f"Periodos base: {periodos_texto}."
        )
    else:
        st.info(f"Consolidado cargado: {len(df):,} filas y {len(df.columns):,} columnas.")

    try:
        columnas = obtener_columnas_filtro(df)
    except Exception as e:
        st.error(f"No se pudieron detectar columnas clave para el filtrado: {e}")
        return

    col_dependencia = columnas["dependencia"]
    col_fecha = columnas["fecha"]

    dependencias_disponibles = sorted(
        serie_texto(df[col_dependencia]).replace({"nan": ""}).dropna().unique()
    )
    dependencias_disponibles = [d for d in dependencias_disponibles if d]

    fechas_disponibles = preparar_fechas_para_ui(df[col_fecha])

    nonce_filtro = st.session_state.get("filtro_nonce", 0)
    key_consolidado = str(abs(hash(str(consolidado_path))))[:10]
    key_base = f"{nonce_filtro}_{consolidado_path.name}_{key_consolidado}"

    st.markdown("#### Filtros principales")

    dependencias = st.multiselect(
        "Dependencias / carreras encontradas",
        dependencias_disponibles,
        key=f"dependencias_filtro_{key_base}",
    )

    fechas = st.multiselect(
        "Fechas de inicio encontradas",
        fechas_disponibles,
        key=f"fechas_filtro_{key_base}",
    )

    st.caption("Condiciones adicionales")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        excluir_practica = st.checkbox(
            "Excluir PRACTICA",
            value=True,
            key=f"excluir_practica_{key_base}",
        )

    with col2:
        excluir_materias_historicas = st.checkbox(
            "Excluir materias historicas",
            value=True,
            help="Replica las exclusiones del 3_Filtrar.py anterior.",
            key=f"excluir_historicas_{key_base}",
        )

    with col3:
        capacidad_mayor_cero = st.checkbox(
            "Capacidad != 0",
            value=True,
            key=f"capacidad_mayor_cero_{key_base}",
        )

    with col4:
        inscritos_mayor_cero = st.checkbox(
            "Inscritos != 0",
            value=True,
            key=f"inscritos_mayor_cero_{key_base}",
        )

    try:
        df_base_para_filtros_avanzados, _, _ = aplicar_filtro_con_diagnostico(
            df,
            dependencias=dependencias,
            fechas=fechas,
            excluir_practica=excluir_practica,
            excluir_materias_historicas=excluir_materias_historicas,
            capacidad_mayor_cero=capacidad_mayor_cero,
            inscritos_mayor_cero=inscritos_mayor_cero,
        )
    except Exception:
        df_base_para_filtros_avanzados = df.copy()

    filtros_avanzados = mostrar_filtros_avanzados_opcionales(
        df_base_para_filtros_avanzados,
        key_base=key_base,
    )

    aplicar = st.button(
        "Aplicar filtro",
        type="primary",
        key=f"btn_aplicar_filtro_{key_base}",
    )

    if aplicar:
        with st.spinner("Aplicando filtro en memoria..."):
            df_filtrado, df_diagnostico, columnas_usadas = aplicar_filtro_con_diagnostico(
                df,
                dependencias=dependencias,
                fechas=fechas,
                excluir_practica=excluir_practica,
                excluir_materias_historicas=excluir_materias_historicas,
                capacidad_mayor_cero=capacidad_mayor_cero,
                inscritos_mayor_cero=inscritos_mayor_cero,
            )

            df_filtrado, resumen_filtros_avanzados = aplicar_filtros_avanzados(
                df_filtrado,
                filtros_avanzados,
            )

        filtros_aplicados = {
            "dependencias": dependencias,
            "fechas": fechas,
            "excluir_practica": excluir_practica,
            "excluir_materias_historicas": excluir_materias_historicas,
            "capacidad_mayor_cero": capacidad_mayor_cero,
            "inscritos_mayor_cero": inscritos_mayor_cero,
            "columnas_usadas": columnas_usadas,
            "filtros_avanzados": resumen_filtros_avanzados,
            "periodos_base": periodos_base,
        }

        nombre_base = f"Filtrado_Dinamico_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        registrar_resultado_filtro_sesion(
            df_filtrado=df_filtrado,
            df_diagnostico=df_diagnostico,
            columnas_usadas=columnas_usadas,
            consolidado_path=consolidado_path,
            filtros_aplicados=filtros_aplicados,
            nombre_base=nombre_base,
        )

        if df_filtrado.empty:
            st.warning("El filtro se aplico correctamente, pero no produjo registros.")
        else:
            st.success(
                f"Filtro aplicado en memoria: {len(df_filtrado):,} registros encontrados. "
                "Descarga Excel o CSV solo si lo necesitas."
            )

    mostrar_resultado_filtro_sesion()
    mostrar_archivos_generados(consolidado_path.parent, contexto="principal")

def construir_resumen_ejecucion_actual(
    estado: str,
    origen: str,
    periodos=None,
    consolidado_path=None,
    mensaje: str = "",
) -> dict:
    """
    Construye un resumen visible solo en la sesion actual del usuario.
    No escribe archivos globales y no comparte informacion con otros usuarios.
    """
    if periodos is None:
        periodos = []

    if isinstance(periodos, str):
        periodos = [periodos]

    consolidado_str = ""
    carpeta_str = ""

    if consolidado_path:
        consolidado = Path(consolidado_path)
        consolidado_str = str(consolidado)
        carpeta_str = str(consolidado.parent)

    return {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": st.session_state.get("iceberg_user", ""),
        "entorno": etiqueta_modo_ejecucion(),
        "estado": estado,
        "origen": origen,
        "periodos": list(periodos) if isinstance(periodos, (list, tuple, set)) else [str(periodos)],
        "consolidado": consolidado_str,
        "carpeta": carpeta_str,
        "mensaje": mensaje,
    }


def mostrar_resumen_ejecucion_actual() -> None:
    """
    Muestra solo el resumen de la ejecucion actual de la sesion.
    """
    resumen = st.session_state.get("resumen_ejecucion_actual")

    if not resumen:
        return

    with st.expander("Resumen de ejecucion actual", expanded=False):
        st.caption(
            "Este resumen pertenece solo a esta sesion. "
            "No es una bitacora global ni muestra ejecuciones de otros usuarios."
        )

        periodos = resumen.get("periodos", [])
        periodos_texto = ", ".join(periodos) if isinstance(periodos, list) else str(periodos)

        datos = {
            "Fecha": resumen.get("fecha", ""),
            "Estado": resumen.get("estado", ""),
            "Origen": resumen.get("origen", ""),
            "Usuario": resumen.get("usuario", ""),
            "Entorno": resumen.get("entorno", ""),
            "Periodos": periodos_texto,
            "Mensaje": resumen.get("mensaje", ""),
        }

        st.dataframe(
            pd.DataFrame([datos]),
            use_container_width=True,
            hide_index=True,
        )

        consolidado = resumen.get("consolidado", "")
        if consolidado:
            with st.expander("Ver ruta tecnica de esta ejecucion", expanded=False):
                st.code(consolidado, language="text")


def mostrar_ultimo_consolidado():
    """
    Desactivado para uso compartido.
    Evita que un usuario cargue consolidados globales generados por otra sesion.
    """
    return

def main():
    st.set_page_config(
        page_title="ICEBERG - Reportes",
        page_icon="\U0001f4ca",
        layout="wide",
    )

    inicializar_estado()
    inicializar_workspace_sesion()
    verificar_timeout_inactividad()
    registrar_actividad()
    aplicar_estilos()

    st.title("ICEBERG - Reportes")
    st.caption("Descarga, consolidaci\u00f3n, filtrado y acceso r\u00e1pido a archivos generados.")
    st.caption(f"Modo actual: {etiqueta_modo_ejecucion()}")

    if st.session_state.get("mensaje_sesion"):
        st.info(st.session_state["mensaje_sesion"])
        st.session_state["mensaje_sesion"] = ""

    mostrar_sidebar()
    mostrar_diagnostico_tecnico_sidebar()

    if not st.session_state["login_validado"]:
        mostrar_login()
        return

    consolidado_session = st.session_state.get("consolidado_path")

    if consolidado_session:
        mostrar_consolidado_activo_sesion()
        mostrar_panel_filtrado(Path(consolidado_session))
        mostrar_consolidados_sesion()
    else:
        mostrar_descarga()
        mostrar_consolidados_sesion()

    if st.session_state["ultimo_error"]:
        st.error(st.session_state["ultimo_error"])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Ocurrió un error inesperado en la aplicación.")
        st.exception(e)
