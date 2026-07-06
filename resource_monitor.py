from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import psutil
except Exception:
    psutil = None


CARPETA_DESCARGAS_DEFAULT = Path("descargas_iceberg")
LIMITE_REFERENCIA_MB = 2764


def _formato_mb(bytes_valor: int | float | None) -> str:
    if bytes_valor is None:
        return "N/D"

    try:
        return f"{bytes_valor / (1024 * 1024):,.1f} MB"
    except Exception:
        return "N/D"


def _tamano_carpeta(carpeta: Path) -> tuple[int, int]:
    if not carpeta.exists():
        return 0, 0

    total = 0
    cantidad = 0

    for archivo in carpeta.rglob("*"):
        try:
            if archivo.is_file():
                total += archivo.stat().st_size
                cantidad += 1
        except Exception:
            pass

    return cantidad, total


def _dataframes_en_sesion() -> tuple[int, int]:
    cantidad = 0
    total_bytes = 0

    for valor in st.session_state.values():
        try:
            if isinstance(valor, pd.DataFrame):
                cantidad += 1
                total_bytes += int(valor.memory_usage(deep=True).sum())
        except Exception:
            pass

    return cantidad, total_bytes


def _tamano_session_state_aproximado() -> int:
    total = 0

    for clave, valor in st.session_state.items():
        try:
            total += sys.getsizeof(clave)
            total += sys.getsizeof(valor)
        except Exception:
            pass

    return total


def obtener_diagnostico_recursos(carpeta_descargas: Path | None = None) -> dict:
    carpeta = carpeta_descargas or CARPETA_DESCARGAS_DEFAULT

    diagnostico = {
        "psutil_disponible": psutil is not None,
        "ram_proceso_bytes": None,
        "cpu_proceso_pct": None,
        "ram_sistema_disponible_bytes": None,
        "ram_sistema_pct": None,
        "archivos_descargas": 0,
        "tamano_descargas_bytes": 0,
        "dataframes_sesion": 0,
        "dataframes_sesion_bytes": 0,
        "session_state_keys": len(st.session_state.keys()),
        "session_state_aprox_bytes": _tamano_session_state_aproximado(),
    }

    cantidad_archivos, tamano_descargas = _tamano_carpeta(carpeta)
    diagnostico["archivos_descargas"] = cantidad_archivos
    diagnostico["tamano_descargas_bytes"] = tamano_descargas

    cantidad_df, tamano_df = _dataframes_en_sesion()
    diagnostico["dataframes_sesion"] = cantidad_df
    diagnostico["dataframes_sesion_bytes"] = tamano_df

    if psutil is None:
        return diagnostico

    try:
        proceso = psutil.Process(os.getpid())

        diagnostico["ram_proceso_bytes"] = proceso.memory_info().rss
        diagnostico["cpu_proceso_pct"] = proceso.cpu_percent(interval=0.05)

        memoria = psutil.virtual_memory()
        diagnostico["ram_sistema_disponible_bytes"] = memoria.available
        diagnostico["ram_sistema_pct"] = memoria.percent

    except Exception:
        pass

    return diagnostico



def _carpetas_protegidas_sesion() -> set[Path]:
    """
    Identifica carpetas que no deben borrarse porque pueden estar activas
    en la sesion actual.
    """
    protegidas = set()

    posibles_rutas = [
        st.session_state.get("carpeta_consolidado_activo"),
    ]

    consolidado_path = st.session_state.get("consolidado_path")

    if consolidado_path:
        try:
            posibles_rutas.append(str(Path(consolidado_path).parent))
        except Exception:
            pass

    for registro in st.session_state.get("consolidados_sesion", []) or []:
        try:
            ruta = registro.get("consolidado")
            if ruta:
                posibles_rutas.append(str(Path(ruta).parent))
        except Exception:
            pass

    for ruta in posibles_rutas:
        try:
            if ruta:
                protegidas.add(Path(ruta).resolve())
        except Exception:
            pass

    return protegidas


def limpiar_temporales_antiguos(
    carpeta_base: Path | None = None,
    conservar_ultimas: int = 5,
) -> dict:
    """
    Elimina carpetas antiguas dentro de descargas_iceberg.
    Conserva las mas recientes y las carpetas activas de la sesion.
    """
    carpeta = carpeta_base or CARPETA_DESCARGAS_DEFAULT

    resultado = {
        "carpetas_eliminadas": 0,
        "archivos_eliminados": 0,
        "bytes_liberados": 0,
        "errores": [],
    }

    if not carpeta.exists():
        return resultado

    protegidas = _carpetas_protegidas_sesion()

    carpetas = [
        item for item in carpeta.iterdir()
        if item.is_dir()
    ]

    carpetas = sorted(
        carpetas,
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    candidatas = carpetas[max(conservar_ultimas, 0):]

    for carpeta_item in candidatas:
        try:
            ruta_resuelta = carpeta_item.resolve()

            if ruta_resuelta in protegidas:
                continue

            archivos, tamano = _tamano_carpeta(carpeta_item)

            import shutil
            shutil.rmtree(carpeta_item)

            resultado["carpetas_eliminadas"] += 1
            resultado["archivos_eliminados"] += archivos
            resultado["bytes_liberados"] += tamano

        except Exception as exc:
            resultado["errores"].append(f"{carpeta_item}: {exc}")

    return resultado

def mostrar_diagnostico_tecnico_sidebar(carpeta_descargas: Path | None = None) -> None:
    with st.sidebar:
        with st.expander("Diagnostico tecnico", expanded=False):
            diagnostico = obtener_diagnostico_recursos(carpeta_descargas)

            if not diagnostico.get("psutil_disponible"):
                st.warning("psutil no esta disponible. Instala psutil para ver RAM y CPU.")

            ram_proceso_bytes = diagnostico.get("ram_proceso_bytes") or 0

            ram_referencia_pct = (
                ram_proceso_bytes / (LIMITE_REFERENCIA_MB * 1024 * 1024) * 100
                if ram_proceso_bytes
                else 0
            )

            st.caption("Uso aproximado del proceso actual")
            st.write(f"RAM proceso: {_formato_mb(diagnostico.get('ram_proceso_bytes'))}")
            st.write(f"RAM proceso vs 2.7 GB: {ram_referencia_pct:,.1f}%")
            st.write(f"CPU proceso: {diagnostico.get('cpu_proceso_pct', 'N/D')}%")

            st.caption("Memoria del entorno")
            st.write(f"RAM disponible: {_formato_mb(diagnostico.get('ram_sistema_disponible_bytes'))}")
            st.write(f"RAM usada sistema: {diagnostico.get('ram_sistema_pct', 'N/D')}%")

            st.caption("Archivos temporales")
            st.write(
                f"descargas_iceberg: "
                f"{diagnostico.get('archivos_descargas', 0)} archivos / "
                f"{_formato_mb(diagnostico.get('tamano_descargas_bytes'))}"
            )

            st.caption("Sesion actual")
            st.write(
                f"DataFrames en sesion: "
                f"{diagnostico.get('dataframes_sesion', 0)} / "
                f"{_formato_mb(diagnostico.get('dataframes_sesion_bytes'))}"
            )
            st.write(f"Claves session_state: {diagnostico.get('session_state_keys', 0)}")
            st.write(
                f"session_state aprox.: "
                f"{_formato_mb(diagnostico.get('session_state_aprox_bytes'))}"
            )

            if ram_referencia_pct >= 80:
                st.error("Alerta: el proceso se acerca al limite de memoria de referencia.")
            elif ram_referencia_pct >= 60:
                st.warning("Advertencia: el proceso esta usando una parte importante de la memoria.")
            else:
                st.success("Uso de memoria dentro de un rango razonable.")

            st.caption("Limpieza segura")

            conservar = st.number_input(
                "Mantener ultimas carpetas",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                key="num_conservar_carpetas_temporales",
            )

            if st.button("Limpiar temporales antiguos", key="btn_limpiar_temporales_antiguos"):
                resultado = limpiar_temporales_antiguos(
                    carpeta_base=carpeta_descargas or CARPETA_DESCARGAS_DEFAULT,
                    conservar_ultimas=int(conservar),
                )

                st.success(
                    "Limpieza finalizada: "
                    f"{resultado['carpetas_eliminadas']} carpetas, "
                    f"{resultado['archivos_eliminados']} archivos, "
                    f"{_formato_mb(resultado['bytes_liberados'])} liberados."
                )

                if resultado["errores"]:
                    with st.expander("Ver errores de limpieza", expanded=False):
                        for error in resultado["errores"]:
                            st.code(error, language="text")

            if st.button("Actualizar diagnostico", key="btn_actualizar_diagnostico_tecnico"):
                st.rerun()
