from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
from uuid import uuid4

import pandas as pd
import streamlit as st


MAX_CONSOLIDADOS_SESION = 10


def inicializar_workspace_sesion() -> None:
    """
    Inicializa el espacio temporal de trabajo de la sesion actual.
    No usa archivos globales ni comparte informacion con otras sesiones.
    """
    if "consolidados_sesion" not in st.session_state:
        st.session_state["consolidados_sesion"] = []


def registrar_consolidado_sesion(
    consolidado_path,
    periodos=None,
    origen: str = "descarga",
    mensaje: str = "",
) -> None:
    """
    Registra un consolidado generado durante la sesion actual.
    La lista queda solo en st.session_state.
    """
    inicializar_workspace_sesion()

    if periodos is None:
        periodos = []

    if isinstance(periodos, str):
        periodos = [periodos]

    consolidado = Path(consolidado_path)

    registro = {
        "id": uuid4().hex[:10],
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "periodos": list(periodos) if isinstance(periodos, (list, tuple, set)) else [str(periodos)],
        "origen": origen,
        "estado": "OK",
        "consolidado": str(consolidado),
        "carpeta": str(consolidado.parent),
        "archivo": consolidado.name,
        "mensaje": mensaje,
    }

    actuales = st.session_state.get("consolidados_sesion", [])

    # Evita duplicar exactamente el mismo consolidado.
    actuales = [
        item for item in actuales
        if item.get("consolidado") != registro["consolidado"]
    ]

    actuales.insert(0, registro)

    st.session_state["consolidados_sesion"] = actuales[:MAX_CONSOLIDADOS_SESION]


def obtener_consolidados_sesion() -> list[dict]:
    """
    Devuelve los consolidados disponibles solo para la sesion actual.
    """
    inicializar_workspace_sesion()
    return st.session_state.get("consolidados_sesion", [])


def limpiar_estado_visual_archivos() -> None:
    """
    Limpia selecciones y tablas visuales para evitar mezclar archivos
    de ejecuciones o consolidados diferentes.
    """
    prefijos = (
        "mensaje_archivos_",
        "tabla_archivos_",
    )

    claves_fijas = {
        "archivo_seleccionado",
        "archivo_seleccionado_path",
        "ruta_archivo_seleccionado",
        "archivo_activo",
        "archivo_activo_path",
    }

    for clave in list(st.session_state.keys()):
        if clave in claves_fijas or any(str(clave).startswith(prefijo) for prefijo in prefijos):
            del st.session_state[clave]


def crear_carpeta_reuso_consolidado(registro: dict) -> Path:
    """
    Crea una carpeta limpia de reuso y copia alli el consolidado base.
    Esto evita mezclar filtros nuevos con filtros de ejecuciones anteriores.
    """
    ruta_original = Path(registro.get("consolidado", ""))

    if not ruta_original.exists():
        raise FileNotFoundError("El consolidado original ya no existe.")

    carpeta_original = ruta_original.parent
    base_descargas = carpeta_original.parent

    sufijo = registro.get("id", "sesion")[:6]
    nombre_base = datetime.now().strftime("iceberg_%Y_%m_%d_%H_%M_%S_reuso_") + sufijo
    carpeta_reuso = base_descargas / nombre_base

    contador = 1
    while carpeta_reuso.exists():
        carpeta_reuso = base_descargas / f"{nombre_base}_{contador}"
        contador += 1

    carpeta_reuso.mkdir(parents=True, exist_ok=True)

    destino = carpeta_reuso / ruta_original.name
    shutil.copy2(ruta_original, destino)

    return destino


def obtener_registro_consolidado_activo() -> dict | None:
    """
    Devuelve el registro del consolidado activo si pertenece a esta sesion.
    """
    activo_id = st.session_state.get("consolidado_activo_id")

    if activo_id:
        for registro in obtener_consolidados_sesion():
            if registro.get("id") == activo_id:
                return registro

    ruta_activa = st.session_state.get("consolidado_path")

    if not ruta_activa:
        return None

    for registro in obtener_consolidados_sesion():
        if registro.get("consolidado") == ruta_activa:
            return registro

    return None


def activar_consolidado_sesion(registro: dict) -> None:
    """
    Activa un consolidado de la sesion actual creando una carpeta limpia de reuso.
    """
    ruta = registro.get("consolidado", "")

    if not ruta:
        st.warning("No se encontro la ruta del consolidado seleccionado.")
        return

    if not Path(ruta).exists():
        st.warning(
            "El consolidado seleccionado ya no existe en el almacenamiento temporal de la app."
        )
        return

    try:
        ruta_reuso = crear_carpeta_reuso_consolidado(registro)
    except Exception as exc:
        st.error(f"No se pudo preparar la carpeta de reuso: {exc}")
        return

    limpiar_estado_visual_archivos()

    st.session_state["consolidado_path"] = str(ruta_reuso)
    st.session_state["consolidado_origen"] = "sesion_reuso"
    st.session_state["consolidado_activo_id"] = registro.get("id", "")
    st.session_state["periodos_consolidado_activo"] = registro.get("periodos", [])
    st.session_state["fecha_consolidado_activo"] = registro.get("fecha", "")
    st.session_state["archivo_consolidado_activo"] = registro.get("archivo", ruta_reuso.name)
    st.session_state["carpeta_consolidado_activo"] = str(ruta_reuso.parent)
    st.session_state["ultima_ejecucion_ok"] = True
    st.session_state["ultimo_error"] = ""


def mostrar_consolidado_activo_sesion() -> None:
    """
    Muestra una unica alerta con la informacion importante del consolidado activo.
    """
    ruta_activa = st.session_state.get("consolidado_path")

    if not ruta_activa:
        return

    registro = obtener_registro_consolidado_activo()

    if registro:
        periodos = registro.get("periodos", [])
        archivo = registro.get("archivo", Path(ruta_activa).name)
        fecha = registro.get("fecha", "")
    else:
        periodos = st.session_state.get("periodos_consolidado_activo", [])
        archivo = st.session_state.get("archivo_consolidado_activo", Path(ruta_activa).name)
        fecha = st.session_state.get("fecha_consolidado_activo", "")

    periodos_texto = ", ".join(periodos) if isinstance(periodos, list) else str(periodos)
    origen = st.session_state.get("consolidado_origen", "")

    modo = "reuso de sesi\u00f3n" if origen == "sesion_reuso" else "descarga actual"

    st.info(
        f"Consolidado activo: {archivo} | "
        f"Periodos: {periodos_texto or 'No identificados'} | "
        f"Modo: {modo}"
        + (f" | Generado: {fecha}" if fecha else "")
    )


def mostrar_consolidados_sesion() -> None:
    """
    Muestra los consolidados generados durante la sesion actual y permite reutilizarlos
    sin duplicar la informacion en tabla y listado.
    """
    registros = obtener_consolidados_sesion()

    if not registros:
        return

    with st.expander("Mis consolidados de esta sesi\u00f3n", expanded=False):
        st.caption(
            "Estos consolidados pertenecen solo a esta sesi\u00f3n del navegador. "
            "No se muestran ejecuciones de otros usuarios."
        )

        activo_id = st.session_state.get("consolidado_activo_id", "")

        filas = []

        for idx, registro in enumerate(registros, start=1):
            periodos = registro.get("periodos", [])
            periodos_texto = ", ".join(periodos) if isinstance(periodos, list) else str(periodos)

            filas.append({
                "Usar": False,
                "Activo": "Si" if registro.get("id") == activo_id else "",
                "#": idx,
                "Fecha": registro.get("fecha", ""),
                "Periodos": periodos_texto,
                "Archivo": registro.get("archivo", ""),
                "Origen": registro.get("origen", ""),
                "Estado": registro.get("estado", ""),
                "ID": registro.get("id", ""),
            })

        df = pd.DataFrame(filas)

        df_editado = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=[
                "Activo",
                "#",
                "Fecha",
                "Periodos",
                "Archivo",
                "Origen",
                "Estado",
                "ID",
            ],
            column_config={
                "Usar": st.column_config.CheckboxColumn(
                    "Usar",
                    help="Marca un consolidado para cargarlo y filtrarlo.",
                    default=False,
                ),
                "ID": None,
            },
            key="editor_consolidados_sesion",
        )

        seleccionados = df_editado[df_editado["Usar"] == True]

        col1, col2 = st.columns([1, 4])

        with col1:
            cargar = st.button(
                "Cargar seleccionado",
                disabled=seleccionados.empty,
                key="btn_cargar_consolidado_sesion_seleccionado",
            )

        with col2:
            if seleccionados.empty:
                st.caption("Selecciona un consolidado para volver a filtrarlo sin descargar nuevamente.")
            elif len(seleccionados) > 1:
                st.warning("Selecciona solo un consolidado a la vez.")
            else:
                st.caption("Se cargara una copia limpia del consolidado seleccionado para filtrar.")

        if cargar:
            if len(seleccionados) > 1:
                st.warning("Selecciona solo un consolidado a la vez.")
                return

            registro_id = seleccionados.iloc[0]["ID"]
            registro = next(
                (item for item in registros if item.get("id") == registro_id),
                None,
            )

            if not registro:
                st.warning("No se encontro el consolidado seleccionado.")
                return

            activar_consolidado_sesion(registro)
            st.rerun()

        with st.expander("Ver rutas t\u00e9cnicas de esta sesi\u00f3n", expanded=False):
            for idx, registro in enumerate(registros, start=1):
                st.code(
                    f"{idx}. {registro.get('consolidado', '')}",
                    language="text",
                )
