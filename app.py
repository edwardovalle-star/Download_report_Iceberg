import os
import sys
import subprocess
import zipfile
from pathlib import Path
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st

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
except Exception:
    sync_playwright = None



BASE_DIR = Path(__file__).resolve().parent
ICEBERG_LOGIN_URL = "https://sig.cun.edu.co/icebergrs/"

# Modo de ejecución:
# - true  : ejecución local en Windows. Habilita abrir carpeta/archivo.
# - false : ejecución web/servidor/Codespaces/Docker. Solo muestra descargas.
MODO_LOCAL = os.getenv("ICEBERG_MODO_LOCAL", "false").strip().lower() in {"1", "true", "yes", "si", "sí"}

# Etiqueta visual para que el usuario identifique dónde está corriendo.
ENTORNO_APP = os.getenv("ICEBERG_ENTORNO", "streamlit_cloud").strip().lower()



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
    if MODO_LOCAL:
        return "Local Windows"

    if ENTORNO_APP in {"codespaces", "github_codespaces"}:
        return "GitHub Codespaces"

    if ENTORNO_APP in {"docker", "contenedor", "container"}:
        return "Docker / Servidor"

    if ENTORNO_APP in {"streamlit", "streamlit_cloud", "cloud"}:
        return "Streamlit Cloud"

    return "Web / Servidor"



def inicializar_estado():
    defaults = {
        "login_validado": False,
        "iceberg_user": "",
        "iceberg_pass": "",
        "consolidado_path": None,
        "ultimo_error": "",
        "ultima_ejecucion_ok": False,
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
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        .ice-ok {border-left: 6px solid #16a34a;}
        .ice-warn {border-left: 6px solid #f59e0b;}
        .ice-error {border-left: 6px solid #dc2626;}
        .ice-muted {
            color: #6b7280;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def limpiar_sesion_login():
    st.session_state["login_validado"] = False
    st.session_state["iceberg_user"] = ""
    st.session_state["iceberg_pass"] = ""
    st.session_state["ultimo_error"] = ""


def mostrar_sidebar():
    with st.sidebar:
        st.header("Estado")

        if st.session_state["login_validado"]:
            st.success("Login validado")
            st.write(f"Usuario: `{st.session_state['iceberg_user']}`")

            if st.button("Cambiar credenciales"):
                limpiar_sesion_login()
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

        if st.session_state["ultima_ejecucion_ok"]:
            st.success("Última ejecución correcta")
        elif st.session_state["ultimo_error"]:
            st.error("Última ejecución con error")
        else:
            st.info("Sin ejecución reciente")


def validar_credenciales_iceberg(usuario: str, password: str) -> tuple[bool, str]:
    """
    Valida credenciales antes de ejecutar la descarga completa.

    Esto evita que el usuario haga clic en Descargar y consolidar
    y luego quede sin respuesta clara si el login falla.
    """
    if sync_playwright is None:
        return False, "Playwright no está instalado o no está disponible. Revisa requirements.txt."

    ok_chromium, mensaje_chromium = asegurar_chromium_playwright()

    if not ok_chromium:
        return False, mensaje_chromium

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
            page.locator("#userName").fill(usuario)
            page.locator('input[name="password"]').fill(password)
            page.get_by_role("button", name="Login").click()

            try:
                page.wait_for_load_state("networkidle", timeout=45000)
            except Exception:
                # ICEBERG no siempre llega a networkidle.
                pass

            html = page.content().lower()
            url_actual = page.url.lower()

            if "logoff" in html or "reportgroup.action" in html or "reports" in html:
                browser.close()
                return True, "Credenciales validadas correctamente."

            sigue_en_login = False
            try:
                sigue_en_login = page.locator("#userName").is_visible(timeout=2000)
            except Exception:
                sigue_en_login = False

            browser.close()

            if sigue_en_login or "login" in url_actual:
                return False, "No fue posible iniciar sesión. Revisa usuario y contraseña."

            return False, "No se pudo confirmar el login. Intenta nuevamente."

    except Exception as e:
        if browser:
            try:
                browser.close()
            except Exception:
                pass

        return False, f"Error validando credenciales: {e}"


def construir_env(periodos: list[str]) -> dict:
    env = os.environ.copy()

    # Evita errores de codificación con emojis o tildes en Windows.
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    # Variables que leen config.py y los scripts hijos.
    env["ICEBERG_USER"] = st.session_state["iceberg_user"]
    env["ICEBERG_PASS"] = st.session_state["iceberg_pass"]
    env["ICEBERG_PERIODOS"] = ",".join(periodos)

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


def mostrar_descarga():
    st.markdown(
        """
        <div class="ice-card ice-ok">
            <strong>Paso 2. Descargar y consolidar</strong><br>
            <span class="ice-muted">
            Selecciona los periodos. La app mostrará avances y errores durante la ejecución.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_descarga"):
        periodos = st.multiselect(
            "Periodos académicos",
            PERIODOS_UI,
        )

        ejecutar = st.form_submit_button("Descargar y consolidar")

    if ejecutar:
        if not periodos:
            st.error("Debes seleccionar al menos un periodo.")
            return

        st.session_state["ultimo_error"] = ""
        st.session_state["ultima_ejecucion_ok"] = False
        st.session_state["consolidado_path"] = None

        env = construir_env(periodos)

        st.info("Proceso iniciado. No cierres esta pestaña hasta finalizar.")
        st.write("Periodos enviados:", periodos)

        ok_descarga, error_descarga = ejecutar_script(
            "1_Descargar.py",
            env,
            "Paso 2.1 - Descarga desde ICEBERG",
        )

        if not ok_descarga:
            st.session_state["ultimo_error"] = error_descarga
            st.error("No se continuará porque falló la descarga.")
            return

        ok_consolidacion, error_consolidacion = ejecutar_script(
            "2_Consolidar.py",
            env,
            "Paso 2.2 - Consolidación",
        )

        if not ok_consolidacion:
            st.session_state["ultimo_error"] = error_consolidacion
            st.error("No se continuará porque falló la consolidación.")
            return

        consolidado = buscar_consolidado_mas_reciente()

        if not consolidado:
            mensaje = "La consolidación terminó, pero no se encontró Consolidado_Final*.xlsx."
            st.session_state["ultimo_error"] = mensaje
            st.error(mensaje)
            return

        st.session_state["consolidado_path"] = str(consolidado)
        st.session_state["ultima_ejecucion_ok"] = True

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

    st.caption(f"Consolidado detectado: `{consolidado_path}`")

    try:
        df = pd.read_excel(consolidado_path, engine="openpyxl")
    except Exception as e:
        st.error(f"No fue posible leer el consolidado: {e}")
        return

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

    with st.form("form_filtrado"):
        dependencias = st.multiselect(
            "Dependencias / carreras encontradas",
            dependencias_disponibles,
        )

        fechas = st.multiselect(
            "Fechas de inicio encontradas",
            fechas_disponibles,
        )

        st.caption("Condiciones adicionales")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            excluir_practica = st.checkbox(
                "Excluir PRACTICA",
                value=True,
            )

        with col2:
            excluir_materias_historicas = st.checkbox(
                "Excluir materias históricas",
                value=True,
                help="Replica las exclusiones del 3_Filtrar.py anterior.",
            )

        with col3:
            capacidad_mayor_cero = st.checkbox(
                "Capacidad != 0",
                value=True,
            )

        with col4:
            inscritos_mayor_cero = st.checkbox(
                "Inscritos != 0",
                value=True,
            )

        aplicar = st.form_submit_button("Aplicar filtro")

    if aplicar:
        with st.spinner("Aplicando filtro..."):
            df_filtrado, df_diagnostico, columnas_usadas = aplicar_filtro_con_diagnostico(
                df=df,
                dependencias=dependencias,
                fechas=fechas,
                excluir_practica=excluir_practica,
                excluir_materias_historicas=excluir_materias_historicas,
                capacidad_mayor_cero=capacidad_mayor_cero,
                inscritos_mayor_cero=inscritos_mayor_cero,
            )

        with st.expander("Ver diagnóstico del filtro", expanded=df_filtrado.empty):
            st.dataframe(df_diagnostico, width="stretch")
            st.json(columnas_usadas)

        st.success(f"Resultado filtrado: {len(df_filtrado):,} filas.")

        if df_filtrado.empty:
            st.warning(
                "El filtro no arrojó resultados. Revisa el diagnóstico anterior para identificar qué condición eliminó los registros."
            )
            return

        st.dataframe(df_filtrado, width="stretch")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = f"Filtrado_Dinamico_{timestamp}"

        carpeta_salida = consolidado_path.parent
        salida_xlsx = carpeta_salida / f"{nombre_base}.xlsx"
        salida_csv = carpeta_salida / f"{nombre_base}.csv"

        df_filtrado.to_excel(salida_xlsx, index=False, engine="openpyxl")
        df_filtrado.to_csv(salida_csv, index=False, encoding="utf-8-sig")
        st.info(f"Archivos guardados en: {carpeta_salida}")

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "Descargar Excel",
                data=convertir_excel_bytes(df_filtrado),
                file_name=f"{nombre_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with c2:
            st.download_button(
                "Descargar CSV",
                data=df_filtrado.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{nombre_base}.csv",
                mime="text/csv",
            )

    # Panel único de archivos generados.
    # Se deja al final para que, si el usuario acaba de filtrar,
    # también aparezcan los archivos Filtrado_Dinamico recién guardados.
    mostrar_archivos_generados(consolidado_path.parent, contexto="principal")


def mostrar_ultimo_consolidado():
    consolidado_existente = buscar_consolidado_mas_reciente()

    if consolidado_existente:
        with st.expander("Usar último consolidado existente"):
            st.write(consolidado_existente)
            if st.button("Cargar último consolidado para filtrar"):
                st.session_state["consolidado_path"] = str(consolidado_existente)
                st.rerun()


def main():
    st.set_page_config(
        page_title="ICEBERG - Reportes",
        page_icon="📊",
        layout="wide",
    )

    inicializar_estado()
    aplicar_estilos()

    st.title("ICEBERG - Reportes")
    st.caption("Descarga, consolidación, filtrado y acceso rápido a archivos generados.")
    st.caption(f"Modo actual: {etiqueta_modo_ejecucion()}")

    mostrar_sidebar()

    if not st.session_state["login_validado"]:
        mostrar_login()
        mostrar_ultimo_consolidado()
        return

    mostrar_descarga()

    consolidado_session = st.session_state.get("consolidado_path")

    if consolidado_session:
        mostrar_panel_filtrado(Path(consolidado_session))
    else:
        mostrar_ultimo_consolidado()

    if st.session_state["ultimo_error"]:
        st.error(st.session_state["ultimo_error"])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Ocurrió un error inesperado en la aplicación.")
        st.exception(e)
