from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


MAX_FILAS_PREVISUALIZACION = 500


def _limpiar_resultado_filtro_actual() -> None:
    """
    Limpia el resultado temporal del filtro actual.
    """
    claves = [
        "resultado_filtro_actual",
        "df_filtrado_actual",
        "df_diagnostico_actual",
        "columnas_usadas_filtro_actual",
    ]

    for clave in claves:
        if clave in st.session_state:
            del st.session_state[clave]


def limpiar_resultado_filtro_si_cambia_consolidado(consolidado_path) -> None:
    """
    Si cambia el consolidado activo, limpia el filtro temporal anterior.
    """
    ruta_actual = str(Path(consolidado_path))
    ruta_previa = st.session_state.get("filtro_consolidado_actual_path", "")

    if ruta_previa != ruta_actual:
        _limpiar_resultado_filtro_actual()
        st.session_state["filtro_consolidado_actual_path"] = ruta_actual


def convertir_df_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Convierte un DataFrame a Excel en memoria.
    No guarda archivos fisicos.
    """
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtrado")

    return buffer.getvalue()


def convertir_df_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convierte un DataFrame a CSV en memoria.
    No guarda archivos fisicos.
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def registrar_resultado_filtro_sesion(
    df_filtrado: pd.DataFrame,
    df_diagnostico: pd.DataFrame | None,
    columnas_usadas: dict | None,
    consolidado_path,
    filtros_aplicados: dict | None = None,
    nombre_base: str | None = None,
) -> None:
    """
    Guarda el resultado del filtro solo en la sesion actual del usuario.
    """
    if nombre_base is None:
        nombre_base = f"Filtrado_Dinamico_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    st.session_state["resultado_filtro_actual"] = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre_base": nombre_base,
        "consolidado": str(Path(consolidado_path)),
        "filas": int(len(df_filtrado)),
        "columnas": int(len(df_filtrado.columns)),
        "filtros_aplicados": filtros_aplicados or {},
    }

    st.session_state["df_filtrado_actual"] = df_filtrado.copy()
    st.session_state["df_diagnostico_actual"] = (
        df_diagnostico.copy()
        if isinstance(df_diagnostico, pd.DataFrame)
        else pd.DataFrame()
    )
    st.session_state["columnas_usadas_filtro_actual"] = columnas_usadas or {}



def _texto_lista_usuario(valores) -> str:
    """
    Convierte listas o valores simples en texto entendible para el usuario.
    """
    if valores is None:
        return ""

    if isinstance(valores, (list, tuple, set)):
        valores_limpios = [str(v) for v in valores if str(v).strip()]
        return ", ".join(valores_limpios)

    return str(valores)


def _construir_lineas_filtros_usuario(filtros: dict) -> list[dict]:
    """
    Construye una tabla Campo / Valor con los criterios aplicados.
    """
    lineas = []

    periodos = _texto_lista_usuario(filtros.get("periodos_base"))
    if periodos:
        lineas.append({"Campo": "Periodos base", "Valor": periodos})

    if filtros.get("excluir_practica"):
        lineas.append({"Campo": "Materias", "Valor": "!= PRACTICA"})

    if filtros.get("excluir_materias_historicas"):
        lineas.append({"Campo": "Materias historicas", "Valor": "Excluidas"})

    if filtros.get("capacidad_mayor_cero"):
        lineas.append({"Campo": "Capacidad", "Valor": "!= 0"})

    if filtros.get("inscritos_mayor_cero"):
        lineas.append({"Campo": "Inscritos", "Valor": "!= 0"})

    dependencias = _texto_lista_usuario(filtros.get("dependencias"))
    if dependencias:
        lineas.append({"Campo": "Dependencia", "Valor": dependencias})

    fechas = _texto_lista_usuario(filtros.get("fechas"))
    if fechas:
        lineas.append({"Campo": "Fecha de inicio", "Valor": fechas})

    filtros_avanzados = filtros.get("filtros_avanzados") or []

    for filtro_avanzado in filtros_avanzados:
        if isinstance(filtro_avanzado, dict):
            campo = filtro_avanzado.get("Campo") or filtro_avanzado.get("campo") or "Filtro avanzado"
            valor = filtro_avanzado.get("Valor") or filtro_avanzado.get("valor") or ""
            lineas.append({"Campo": campo, "Valor": valor})
        elif filtro_avanzado:
            lineas.append({"Campo": "Filtro avanzado", "Valor": str(filtro_avanzado)})

    if not lineas:
        lineas.append({"Campo": "Filtros", "Valor": "Sin criterios especificos seleccionados."})

    return lineas

def _resolver_rutas_guardado_filtro(carpeta: Path, nombre_base: str) -> tuple[Path, Path]:
    """
    Devuelve rutas unicas para guardar Excel y CSV sin sobrescribir archivos existentes.
    """
    salida_xlsx = carpeta / f"{nombre_base}.xlsx"
    salida_csv = carpeta / f"{nombre_base}.csv"

    if not salida_xlsx.exists() and not salida_csv.exists():
        return salida_xlsx, salida_csv

    contador = 1

    while True:
        salida_xlsx = carpeta / f"{nombre_base}_{contador}.xlsx"
        salida_csv = carpeta / f"{nombre_base}_{contador}.csv"

        if not salida_xlsx.exists() and not salida_csv.exists():
            return salida_xlsx, salida_csv

        contador += 1


def _guardar_filtro_en_carpeta_trabajo(df_filtrado: pd.DataFrame, resumen: dict) -> tuple[Path, Path]:
    """
    Guarda el filtro actual en la carpeta activa del consolidado solo cuando el usuario lo decide.
    """
    consolidado = Path(resumen.get("consolidado", ""))

    if not consolidado:
        raise ValueError("No se encontro la ruta del consolidado activo.")

    carpeta = consolidado.parent
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre_base = resumen.get("nombre_base", "Filtrado_Dinamico")

    salida_xlsx, salida_csv = _resolver_rutas_guardado_filtro(carpeta, nombre_base)

    df_filtrado.to_excel(salida_xlsx, index=False, engine="openpyxl")
    df_filtrado.to_csv(salida_csv, index=False, encoding="utf-8-sig")

    st.session_state["ultimo_filtro_guardado"] = {
        "xlsx": str(salida_xlsx),
        "csv": str(salida_csv),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return salida_xlsx, salida_csv


def mostrar_resultado_filtro_sesion() -> None:
    """
    Muestra el resultado temporal del filtro en lenguaje de usuario final.
    No guarda archivos automaticamente.
    """
    resumen = st.session_state.get("resultado_filtro_actual")
    df_filtrado = st.session_state.get("df_filtrado_actual")

    if not resumen or df_filtrado is None:
        return

    filtros = resumen.get("filtros_aplicados", {})
    periodos_base = filtros.get("periodos_base", [])
    periodos_texto = _texto_lista_usuario(periodos_base)

    st.markdown("### Resultado del filtro")

    with st.expander("Resumen de filtros aplicados", expanded=False):
        resumen_filtros = _construir_lineas_filtros_usuario(filtros)
        st.dataframe(
            pd.DataFrame(resumen_filtros),
            use_container_width=True,
            hide_index=True,
        )

    if df_filtrado.empty:
        st.warning(
            "El filtro no produjo registros. Revisa los criterios aplicados "
            "y vuelve a intentar."
        )
    else:
        st.success(
            "Filtro aplicado correctamente. Puedes revisar la vista previa, "
            "descargar el resultado o guardarlo en la carpeta de trabajo."
        )

    if not df_filtrado.empty:
        if len(df_filtrado) > MAX_FILAS_PREVISUALIZACION:
            st.caption(
                f"Vista previa: primeras {MAX_FILAS_PREVISUALIZACION:,} filas "
                f"del resultado filtrado."
            )
            df_preview = df_filtrado.head(MAX_FILAS_PREVISUALIZACION)
        else:
            st.markdown(
                '<div class="ice-table-title">Vista previa del resultado filtrado</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="ice-section-note">Revisa los datos antes de descargar o guardar el resultado.</div>',
                unsafe_allow_html=True,
            )
            df_preview = df_filtrado

        st.dataframe(
            df_preview,
            use_container_width=True,
            hide_index=True,
        )

        nombre_base = resumen.get("nombre_base", "Filtrado_Dinamico")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                "Descargar Excel",
                data=convertir_df_excel_bytes(df_filtrado),
                file_name=f"{nombre_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_excel_{nombre_base}",
            )

        with col2:
            st.download_button(
                "Descargar CSV",
                data=convertir_df_csv_bytes(df_filtrado),
                file_name=f"{nombre_base}.csv",
                mime="text/csv",
                key=f"download_csv_{nombre_base}",
            )

        with col3:
            guardar = st.button(
                "Guardar en carpeta",
                key=f"guardar_filtro_carpeta_{nombre_base}",
            )

        if guardar:
            try:
                salida_xlsx, salida_csv = _guardar_filtro_en_carpeta_trabajo(
                    df_filtrado,
                    resumen,
                )

                st.success(
                    "Filtro guardado en la carpeta de trabajo del consolidado activo."
                )

                with st.expander("Ver archivos guardados", expanded=False):
                    st.code(str(salida_xlsx), language="text")
                    st.code(str(salida_csv), language="text")

            except Exception as exc:
                st.error(f"No se pudo guardar el filtro en carpeta: {exc}")
