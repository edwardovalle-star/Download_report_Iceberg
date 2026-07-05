from __future__ import annotations

from uuid import uuid4

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
    return serie.where(~serie.isna(), "").astype(str).str.strip()


def _numero_serie(serie: pd.Series) -> pd.Series:
    texto = _texto_serie(serie).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


def _valor_numero(valor: str):
    valor = str(valor).strip().replace(",", ".")
    if not valor:
        return None

    convertido = pd.to_numeric(pd.Series([valor]), errors="coerce").iloc[0]
    if pd.isna(convertido):
        return None

    return convertido


def _tipo_estimado(serie: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(serie):
        return "Numero"

    if pd.api.types.is_datetime64_any_dtype(serie):
        return "Fecha"

    muestra_numerica = pd.to_numeric(
        _texto_serie(serie).str.replace(",", ".", regex=False),
        errors="coerce",
    )

    if muestra_numerica.notna().mean() >= 0.8:
        return "Numero"

    return "Texto"


def _valores_unicos_columna(df: pd.DataFrame, campo: str) -> list[str]:
    if campo not in df.columns:
        return []

    valores = (
        _texto_serie(df[campo])
        .replace({"nan": ""})
        .dropna()
        .unique()
        .tolist()
    )

    valores = [v for v in valores if str(v).strip()]

    try:
        return sorted(valores, key=lambda x: str(x).casefold())
    except Exception:
        return valores


def _estado_filtros_key(key_base: str) -> str:
    return f"filtros_avanzados_config_{key_base}"


def _inicializar_filtros_avanzados(key_base: str) -> None:
    estado_key = _estado_filtros_key(key_base)

    if estado_key not in st.session_state:
        st.session_state[estado_key] = []


def _agregar_filtro_avanzado(key_base: str, max_filtros: int) -> None:
    estado_key = _estado_filtros_key(key_base)
    _inicializar_filtros_avanzados(key_base)

    filtros = st.session_state[estado_key]

    if len(filtros) >= max_filtros:
        st.warning("Ya alcanzaste la cantidad maxima de filtros avanzados para este consolidado.")
        return

    filtros.append({"id": uuid4().hex[:10]})
    st.session_state[estado_key] = filtros


def _quitar_filtro_avanzado(key_base: str, filtro_id: str) -> None:
    estado_key = _estado_filtros_key(key_base)
    filtros = st.session_state.get(estado_key, [])

    st.session_state[estado_key] = [
        filtro for filtro in filtros
        if filtro.get("id") != filtro_id
    ]


def mostrar_filtros_avanzados_opcionales(
    df: pd.DataFrame,
    key_base: str,
) -> list[dict]:
    """
    Muestra filtros avanzados estilo Excel con valores dependientes.
    Preserva campo, condicion y valores cuando se agregan nuevos filtros.
    """
    max_filtros = len(df.columns)
    _inicializar_filtros_avanzados(key_base)

    estado_key = _estado_filtros_key(key_base)
    filtros_config = st.session_state[estado_key]
    filtros_resultado = []

    with st.expander("Filtros avanzados opcionales", expanded=False):
        st.caption(
            "Agrega filtros adicionales usando los campos reales del consolidado. "
            "Los valores disponibles se actualizan segun los filtros principales "
            "y los filtros avanzados anteriores."
        )

        col_add, col_info = st.columns([1, 4])

        with col_add:
            if st.button(
                "Agregar filtro",
                key=f"btn_agregar_filtro_avanzado_{key_base}",
                disabled=len(filtros_config) >= max_filtros,
            ):
                _agregar_filtro_avanzado(key_base, max_filtros)
                st.rerun()

        with col_info:
            st.caption(
                f"Filtros avanzados activos: {len(filtros_config)} de {max_filtros} posibles."
            )

        with st.expander("Ver campos disponibles", expanded=False):
            df_campos = pd.DataFrame({
                "#": range(1, len(df.columns) + 1),
                "Campo": list(df.columns),
            })

            st.dataframe(
                df_campos,
                use_container_width=True,
                hide_index=True,
            )

        if df.empty:
            st.warning(
                "Los filtros principales no tienen registros disponibles. "
                "Ajusta los filtros principales para habilitar valores avanzados."
            )

        if not filtros_config:
            st.info("No hay filtros avanzados agregados. Usa el boton Agregar filtro si necesitas criterios adicionales.")
            return []

        columnas = list(df.columns)

        df_contexto = df.copy()
        filtros_actualizados = []

        for idx, filtro in enumerate(list(filtros_config), start=1):
            filtro_id = filtro.get("id", str(idx))

            campo_guardado = filtro.get("campo", columnas[0] if columnas else "")
            if campo_guardado not in columnas and columnas:
                campo_guardado = columnas[0]

            operador_guardado = filtro.get("operador", "Incluir seleccionados")
            if operador_guardado not in OPERADORES_AVANZADOS:
                operador_guardado = "Incluir seleccionados"

            label_vis = "visible" if idx == 1 else "collapsed"

            col1, col2, col3, col4 = st.columns([2.1, 1.5, 3.4, 0.8])

            with col1:
                campo = st.selectbox(
                    "Campo",
                    columnas,
                    index=columnas.index(campo_guardado) if campo_guardado in columnas else 0,
                    key=f"adv_campo_{filtro_id}_{key_base}",
                    label_visibility=label_vis,
                )

            with col2:
                operador = st.selectbox(
                    "Condicion",
                    OPERADORES_AVANZADOS,
                    index=OPERADORES_AVANZADOS.index(operador_guardado),
                    key=f"adv_operador_{filtro_id}_{key_base}",
                    label_visibility=label_vis,
                )

            valores = []
            valor_texto = ""

            with col3:
                if operador in ["Incluir seleccionados", "Excluir seleccionados"]:
                    opciones = _valores_unicos_columna(df_contexto, campo)

                    key_valores = f"adv_valores_{filtro_id}_{key_base}"
                    valores_guardados = filtro.get("valores", [])

                    if key_valores not in st.session_state:
                        st.session_state[key_valores] = [
                            valor for valor in valores_guardados
                            if valor in opciones
                        ]
                    else:
                        seleccion_actual = st.session_state.get(key_valores, [])
                        if isinstance(seleccion_actual, list):
                            st.session_state[key_valores] = [
                                valor for valor in seleccion_actual
                                if valor in opciones
                            ]

                    valores = st.multiselect(
                        "Valores disponibles",
                        opciones,
                        key=key_valores,
                        placeholder="Selecciona uno o varios valores",
                        label_visibility=label_vis,
                    )

                    if not opciones:
                        st.caption("No hay valores disponibles con los filtros anteriores.")

                elif operador in ["Contiene", "No contiene"]:
                    key_texto = f"adv_texto_{filtro_id}_{key_base}"

                    if key_texto not in st.session_state:
                        st.session_state[key_texto] = filtro.get("valor", "")

                    valor_texto = st.text_input(
                        "Texto a buscar",
                        key=key_texto,
                        placeholder="Ej: PROGRAMACION",
                        label_visibility=label_vis,
                    )

                elif operador in ["Mayor que", "Menor que", "Mayor o igual", "Menor o igual"]:
                    key_numero = f"adv_numero_{filtro_id}_{key_base}"

                    if key_numero not in st.session_state:
                        st.session_state[key_numero] = filtro.get("valor", "")

                    valor_texto = st.text_input(
                        "Valor numerico",
                        key=key_numero,
                        placeholder="Ej: 10",
                        label_visibility=label_vis,
                    )

                else:
                    if idx == 1:
                        st.caption("Esta condicion no requiere valor.")

            with col4:
                if idx == 1:
                    st.write("")
                if st.button(
                    "Quitar",
                    key=f"btn_quitar_filtro_{filtro_id}_{key_base}",
                ):
                    _quitar_filtro_avanzado(key_base, filtro_id)
                    st.rerun()

            filtro_actual = {
                "id": filtro_id,
                "campo": campo,
                "operador": operador,
                "valores": valores,
                "valor": valor_texto,
            }

            filtros_resultado.append(filtro_actual)
            filtros_actualizados.append(filtro_actual)

            try:
                df_contexto, _ = aplicar_filtros_avanzados(
                    df_contexto,
                    [filtro_actual],
                )
            except Exception:
                pass

        st.session_state[estado_key] = filtros_actualizados

    return filtros_resultado

def _resumen_criterio_usuario(filtro: dict) -> dict | None:
    campo = filtro.get("campo", "")
    operador = filtro.get("operador", "")
    valores = filtro.get("valores") or []
    valor = str(filtro.get("valor", "")).strip()

    if operador == "Incluir seleccionados":
        if not valores:
            return None
        return {"Campo": campo, "Valor": "Incluye: " + ", ".join(map(str, valores))}

    if operador == "Excluir seleccionados":
        if not valores:
            return None
        return {"Campo": campo, "Valor": "Excluye: " + ", ".join(map(str, valores))}

    if operador == "Contiene":
        if not valor:
            return None
        return {"Campo": campo, "Valor": f"Contiene: {valor}"}

    if operador == "No contiene":
        if not valor:
            return None
        return {"Campo": campo, "Valor": f"No contiene: {valor}"}

    if operador == "Vacio":
        return {"Campo": campo, "Valor": "Vacio"}

    if operador == "No vacio":
        return {"Campo": campo, "Valor": "No vacio"}

    if operador in ["Mayor que", "Menor que", "Mayor o igual", "Menor o igual"]:
        if not valor:
            return None
        return {"Campo": campo, "Valor": f"{operador}: {valor}"}

    return {"Campo": campo, "Valor": f"{operador}: {valor}".strip()}


def construir_resumen_filtros_avanzados(filtros: list[dict]) -> list[dict]:
    resumen = []

    for filtro in filtros or []:
        item = _resumen_criterio_usuario(filtro)
        if item:
            resumen.append(item)

    return resumen


def aplicar_filtros_avanzados(
    df: pd.DataFrame,
    filtros: list[dict],
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Aplica filtros avanzados sobre el DataFrame ya filtrado por criterios base.
    """
    if not filtros:
        return df, []

    resultado = df.copy()
    resumen = []

    for filtro in filtros:
        campo = filtro.get("campo", "")
        operador = filtro.get("operador", "")
        valores = filtro.get("valores") or []
        valor = str(filtro.get("valor", "")).strip()

        if campo not in resultado.columns:
            continue

        serie = resultado[campo]
        texto = _texto_serie(serie)
        texto_min = texto.str.casefold()

        condicion = None

        if operador == "Incluir seleccionados":
            if not valores:
                continue

            seleccion = {str(v).strip().casefold() for v in valores}
            condicion = texto_min.isin(seleccion)

        elif operador == "Excluir seleccionados":
            if not valores:
                continue

            seleccion = {str(v).strip().casefold() for v in valores}
            condicion = ~texto_min.isin(seleccion)

        elif operador == "Contiene":
            if not valor:
                continue

            condicion = texto.str.contains(valor, case=False, na=False, regex=False)

        elif operador == "No contiene":
            if not valor:
                continue

            condicion = ~texto.str.contains(valor, case=False, na=False, regex=False)

        elif operador == "Vacio":
            condicion = serie.isna() | texto.eq("") | texto_min.eq("nan")

        elif operador == "No vacio":
            condicion = ~(serie.isna() | texto.eq("") | texto_min.eq("nan"))

        elif operador in ["Mayor que", "Menor que", "Mayor o igual", "Menor o igual"]:
            numero_usuario = _valor_numero(valor)

            if numero_usuario is None:
                continue

            numeros = _numero_serie(serie)

            if operador == "Mayor que":
                condicion = numeros > numero_usuario
            elif operador == "Menor que":
                condicion = numeros < numero_usuario
            elif operador == "Mayor o igual":
                condicion = numeros >= numero_usuario
            elif operador == "Menor o igual":
                condicion = numeros <= numero_usuario

        if condicion is None:
            continue

        resultado = resultado[condicion].copy()

        item_resumen = _resumen_criterio_usuario(filtro)
        if item_resumen:
            resumen.append(item_resumen)

    return resultado, resumen
