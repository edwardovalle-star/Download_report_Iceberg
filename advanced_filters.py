from __future__ import annotations

from html import escape

import uuid

import pandas as pd
import streamlit as st


OPERADORES_AVANZADOS = [
    "Incluir seleccionados",
    "Excluir seleccionados",
    "Contiene",
    "No contiene",
    "Vacio",
    "No vacio",
    "Mayor que",
    "Menor que",
    "Mayor o igual",
    "Menor o igual",
]


def _texto_serie(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.strip()


def _numero_serie(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie, errors="coerce")


def _valor_numero(valor: object) -> float | None:
    try:
        if valor is None or str(valor).strip() == "":
            return None

        return float(str(valor).replace(",", ".").strip())
    except Exception:
        return None


def _tipo_estimado(serie: pd.Series) -> str:
    muestra = serie.dropna()

    if muestra.empty:
        return "Vacio"

    numerica = pd.to_numeric(muestra, errors="coerce")

    if numerica.notna().mean() >= 0.80:
        return "Numero"

    fechas = pd.to_datetime(muestra, errors="coerce", dayfirst=True)

    if fechas.notna().mean() >= 0.80:
        return "Fecha"

    return "Texto"


def _valores_unicos_columna(df: pd.DataFrame, campo: str, limite: int = 500) -> list[str]:
    if campo not in df.columns:
        return []

    serie = df[campo].dropna().astype(str).str.strip()
    valores = sorted({valor for valor in serie.tolist() if valor and valor.lower() != "nan"})

    return valores[:limite]


def _estado_filtros_key(key_base: str) -> str:
    return f"filtros_avanzados_{key_base}"


def _inicializar_filtros_avanzados(key_base: str) -> None:
    key = _estado_filtros_key(key_base)

    if key not in st.session_state:
        st.session_state[key] = []


def _agregar_filtro_avanzado(key_base: str, max_filtros: int) -> None:
    key = _estado_filtros_key(key_base)
    _inicializar_filtros_avanzados(key_base)

    filtros = st.session_state.get(key, [])

    if len(filtros) >= max_filtros:
        return

    filtros.append(
        {
            "id": uuid.uuid4().hex[:10],
            "campo": "",
            "operador": "Incluir seleccionados",
            "valores": [],
            "valor": "",
        }
    )

    st.session_state[key] = filtros


def _quitar_filtro_avanzado(key_base: str, filtro_id: str) -> None:
    key = _estado_filtros_key(key_base)
    filtros = st.session_state.get(key, [])

    st.session_state[key] = [
        filtro for filtro in filtros
        if str(filtro.get("id")) != str(filtro_id)
    ]


def _dataframe_campos_disponibles(df: pd.DataFrame) -> pd.DataFrame:
    filas = []

    for indice, columna in enumerate(df.columns, start=1):
        serie = df[columna].dropna().astype(str).str.strip()

        valores = [
            valor
            for valor in serie.unique().tolist()
            if valor and valor.lower() != "nan"
        ]

        ejemplos = ", ".join(valores[:3])

        if len(ejemplos) > 180:
            ejemplos = ejemplos[:177] + "..."

        filas.append(
            {
                "#": indice,
                "Campo": str(columna),
                "Ejemplos de registros": ejemplos,
                "Valores unicos": len(set(valores)),
            }
        )

    return pd.DataFrame(
        filas,
        columns=["#", "Campo", "Ejemplos de registros", "Valores unicos"],
    )


def _html_campos_disponibles(df: pd.DataFrame) -> str:
    tabla = _dataframe_campos_disponibles(df)

    filas_html = []

    for _, fila in tabla.iterrows():
        numero = escape(str(fila.get("#", "")))
        campo = escape(str(fila.get("Campo", "")))
        ejemplos = escape(str(fila.get("Ejemplos de registros", "")))
        valores = escape(str(fila.get("Valores unicos", "")))

        filas_html.append(
            f"""
            <tr>
                <td class="ice-ag-index" data-label="#">{numero}</td>
                <td class="ice-ag-field" data-label="Campo">{campo}</td>
                <td class="ice-ag-example" data-label="Ejemplos de registros" title="{ejemplos}">{ejemplos}</td>
                <td class="ice-ag-count" data-label="Valores unicos">{valores}</td>
            </tr>
            """
        )

    total_campos = len(tabla)

    return f"""
    <div class="ice-ag-panel">
        <div class="ice-ag-topbar">
            <div>
                <div class="ice-ag-title">Matriz de campos disponibles</div>
                <div>Campos reales detectados desde el consolidado activo.</div>
            </div>
            <span class="ice-ag-pill">{total_campos} campos</span>
        </div>

        <div class="ice-ag-grid-wrap">
            <table class="ice-ag-table" aria-label="Campos disponibles">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Campo</th>
                        <th>Ejemplos de registros</th>
                        <th>Valores unicos</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(filas_html)}
                </tbody>
            </table>
        </div>
    </div>
    """

def mostrar_filtros_avanzados_opcionales(df: pd.DataFrame, key_base: str) -> list[dict]:
    """
    Muestra filtros avanzados opcionales.
    Los valores disponibles se actualizan segun los filtros principales
    y los filtros avanzados anteriores.
    """
    _inicializar_filtros_avanzados(key_base)

    estado_key = _estado_filtros_key(key_base)
    filtros = st.session_state.get(estado_key, [])

    columnas = [str(col) for col in df.columns]
    max_filtros = len(columnas)

    st.markdown("#### Filtros avanzados opcionales")
    st.caption(
        "Agrega filtros adicionales usando los campos reales del consolidado. "
        "Los valores disponibles se actualizan segun los filtros principales y los filtros avanzados anteriores."
    )

    with st.expander("Ver campos disponibles", expanded=False):
        st.markdown(
            _html_campos_disponibles(df),
            unsafe_allow_html=True,
        )

    col_btn, col_info = st.columns([1.1, 3.2])

    with col_btn:
        if st.button(
            "Agregar filtro",
            key=f"btn_agregar_filtro_avanzado_{key_base}",
        ):
            _agregar_filtro_avanzado(key_base, max_filtros=max_filtros)
            st.rerun()

    with col_info:
        st.caption(f"Filtros avanzados activos: {len(filtros)} de {max_filtros} posibles.")

    if not filtros:
        return []

    st.markdown(
        """
        <div class="ice-filter-grid-header">
            <div>Campo</div>
            <div>Condicion</div>
            <div>Valores / criterio</div>
            <div>Accion</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filtros_actualizados = []
    filtros_previos_para_valores = []

    for indice, filtro in enumerate(filtros):
        if indice > 0:
            st.markdown('<div class="ice-filter-row-separator"></div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="ice-filter-row-label">Filtro avanzado {indice + 1}</div>',
            unsafe_allow_html=True,
        )

        filtro_id = str(filtro.get("id") or uuid.uuid4().hex[:10])
        filtro["id"] = filtro_id

        df_para_valores = df.copy()

        if filtros_previos_para_valores:
            try:
                df_para_valores, _ = aplicar_filtros_avanzados(
                    df_para_valores,
                    filtros_previos_para_valores,
                )
            except Exception:
                df_para_valores = df.copy()

        campo_actual = str(filtro.get("campo") or "")
        if campo_actual not in columnas:
            campo_actual = columnas[0] if columnas else ""

        operador_actual = str(filtro.get("operador") or "Incluir seleccionados")
        if operador_actual not in OPERADORES_AVANZADOS:
            operador_actual = "Incluir seleccionados"

        label_visibility = "visible" if indice == 0 else "collapsed"

        col_campo, col_operador, col_valores, col_quitar = st.columns([1.55, 1.25, 2.6, 0.70])

        with col_campo:
            campo = st.selectbox(
                "Campo",
                columnas,
                index=columnas.index(campo_actual) if campo_actual in columnas else 0,
                key=f"adv_campo_{filtro_id}_{key_base}",
                label_visibility=label_visibility,
            )

        with col_operador:
            operador = st.selectbox(
                "Condicion",
                OPERADORES_AVANZADOS,
                index=OPERADORES_AVANZADOS.index(operador_actual),
                key=f"adv_operador_{filtro_id}_{key_base}",
                label_visibility=label_visibility,
            )

        valores = []
        valor_texto = str(filtro.get("valor") or "")

        with col_valores:
            if operador in {"Incluir seleccionados", "Excluir seleccionados"}:
                valores_disponibles = _valores_unicos_columna(df_para_valores, campo)
                valores_default = [
                    str(valor)
                    for valor in filtro.get("valores", [])
                    if str(valor) in valores_disponibles
                ]

                valores = st.multiselect(
                    "Valores disponibles",
                    valores_disponibles,
                    default=valores_default,
                    key=f"adv_valores_{filtro_id}_{key_base}",
                    label_visibility=label_visibility,
                )

                valor_texto = ""
            elif operador in {"Contiene", "No contiene"}:
                valor_texto = st.text_input(
                    "Texto a buscar",
                    value=valor_texto,
                    key=f"adv_valor_texto_{filtro_id}_{key_base}",
                    label_visibility=label_visibility,
                )
                valores = []
            elif operador in {"Mayor que", "Menor que", "Mayor o igual", "Menor o igual"}:
                valor_texto = st.text_input(
                    "Valor numerico",
                    value=valor_texto,
                    key=f"adv_valor_numero_{filtro_id}_{key_base}",
                    label_visibility=label_visibility,
                )
                valores = []
            else:
                st.caption("No requiere valor.")
                valores = []
                valor_texto = ""

        with col_quitar:
            if indice == 0:
                st.markdown("<div style='height: 1.7rem'></div>", unsafe_allow_html=True)

            if st.button(
                "Quitar",
                key=f"btn_quitar_filtro_{filtro_id}_{key_base}",
            ):
                _quitar_filtro_avanzado(key_base, filtro_id)
                st.rerun()

        filtro_actualizado = {
            "id": filtro_id,
            "campo": campo,
            "operador": operador,
            "valores": valores,
            "valor": valor_texto,
        }

        filtros_actualizados.append(filtro_actualizado)
        filtros_previos_para_valores.append(filtro_actualizado)

    st.session_state[estado_key] = filtros_actualizados

    return filtros_actualizados


def _resumen_criterio_usuario(filtro: dict) -> str:
    operador = filtro.get("operador", "")
    valores = filtro.get("valores", [])
    valor = str(filtro.get("valor", "")).strip()

    if operador in {"Incluir seleccionados", "Excluir seleccionados"}:
        return ", ".join([str(v) for v in valores]) if valores else "Sin seleccion"

    if operador in {"Contiene", "No contiene"}:
        return valor or "Sin texto"

    if operador in {"Mayor que", "Menor que", "Mayor o igual", "Menor o igual"}:
        return valor or "Sin numero"

    return operador


def construir_resumen_filtros_avanzados(filtros: list[dict]) -> list[dict]:
    resumen = []

    for filtro in filtros or []:
        resumen.append(
            {
                "Campo": filtro.get("campo", ""),
                "Condicion": filtro.get("operador", ""),
                "Valor": _resumen_criterio_usuario(filtro),
            }
        )

    return resumen


def aplicar_filtros_avanzados(df: pd.DataFrame, filtros: list[dict]) -> tuple[pd.DataFrame, list[dict]]:
    df_resultado = df.copy()
    resumen = []

    for filtro in filtros or []:
        campo = filtro.get("campo")
        operador = filtro.get("operador")

        if not campo or campo not in df_resultado.columns:
            continue

        serie = df_resultado[campo]
        condicion = None
        detalle = ""

        if operador == "Incluir seleccionados":
            valores = [str(valor) for valor in filtro.get("valores", [])]
            if not valores:
                continue

            condicion = _texto_serie(serie).isin(valores)
            detalle = ", ".join(valores)

        elif operador == "Excluir seleccionados":
            valores = [str(valor) for valor in filtro.get("valores", [])]
            if not valores:
                continue

            condicion = ~_texto_serie(serie).isin(valores)
            detalle = ", ".join(valores)

        elif operador == "Contiene":
            valor = str(filtro.get("valor", "")).strip()
            if not valor:
                continue

            condicion = _texto_serie(serie).str.contains(valor, case=False, regex=False, na=False)
            detalle = valor

        elif operador == "No contiene":
            valor = str(filtro.get("valor", "")).strip()
            if not valor:
                continue

            condicion = ~_texto_serie(serie).str.contains(valor, case=False, regex=False, na=False)
            detalle = valor

        elif operador == "Vacio":
            texto = _texto_serie(serie)
            condicion = serie.isna() | texto.eq("") | texto.str.lower().eq("nan")
            detalle = "Campo vacio"

        elif operador == "No vacio":
            texto = _texto_serie(serie)
            condicion = ~(serie.isna() | texto.eq("") | texto.str.lower().eq("nan"))
            detalle = "Campo no vacio"

        elif operador in {"Mayor que", "Menor que", "Mayor o igual", "Menor o igual"}:
            valor_num = _valor_numero(filtro.get("valor"))
            if valor_num is None:
                continue

            numero = _numero_serie(serie)

            if operador == "Mayor que":
                condicion = numero > valor_num
            elif operador == "Menor que":
                condicion = numero < valor_num
            elif operador == "Mayor o igual":
                condicion = numero >= valor_num
            elif operador == "Menor o igual":
                condicion = numero <= valor_num

            detalle = str(valor_num)

        if condicion is None:
            continue

        antes = len(df_resultado)
        df_resultado = df_resultado[condicion].copy()
        despues = len(df_resultado)

        resumen.append(
            {
                "Campo": campo,
                "Condicion": operador,
                "Valor": detalle,
                "Filas antes": antes,
                "Filas despues": despues,
            }
        )

    return df_resultado, resumen
