import pandas as pd
import os
from datetime import datetime
import config

# --- CONFIGURACIÓN DEL FILTRO ---
# Define aquí el valor de fecha para filtrar (columna U: "Fec_inicio_grupo")
VALOR_FECHA_FILTRO = "02/02/2026"  # Formato: DD/MM/YYYY

# --- CONFIGURACIÓN AVANZADA (Opcional) ---
# Si necesitas filtrar por múltiples fechas, descomenta y edita:
# VALORES_FECHAS_MULTIPLES = ["02/02/2026", "09/02/2026", "16/02/2026"]
VALORES_FECHAS_MULTIPLES = None  # None = usar solo VALOR_FECHA_FILTRO

# Dependencia a filtrar
#DEPENDENCIA_OBJETIVO = "INGENIERIA DE SISTEMAS"

# Materias a excluir (puedes agregar más)
# MATERIAS_EXCLUIDAS = [
#     "TRABAJO DE INVESTIGACION EN INGENIERIA",
#     "PLAN DE NEGOCIO APLICADO PARA ESCUELA DE INGENIERIA",
#     "COMPRENSION Y PRODUCCION DE TEXTOS"
# ]

# Patrón regex para excluir materias (ej: todas las que contengan "PRACTICA")
PATRON_EXCLUIR = "PRACTICA"

def log_filtrado(mensaje: str, tipo: str = "INFO"):
    """Log específico para filtrado."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    simbolos = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    simbolo = simbolos.get(tipo, "•")
    print(f"[{timestamp}] {simbolo} {mensaje}")

def obtener_carpeta_mas_reciente():
    """Busca la carpeta de descarga más reciente."""
    if not os.path.exists(config.CARPETA_BASE):
        return None

    carpetas = []
    for item in os.listdir(config.CARPETA_BASE):
        ruta_completa = os.path.join(config.CARPETA_BASE, item)
        if os.path.isdir(ruta_completa) and item.startswith(config.CARPETA_ICEBERG+"_"):
            carpetas.append((ruta_completa, os.path.getctime(ruta_completa)))

    if not carpetas:
        return None

    carpetas.sort(key=lambda x: x[1], reverse=True)
    return carpetas[0][0]

def buscar_archivo_consolidado(carpeta):
    """Busca el archivo consolidado más reciente en la carpeta."""
    import glob

    # Buscar archivos consolidados
    archivos = glob.glob(os.path.join(carpeta, "Consolidado_Final*.xlsx"))

    if not archivos:
        return None

    # Si hay varios, tomar el más reciente
    if len(archivos) > 1:
        archivos.sort(key=lambda x: os.path.getctime(x), reverse=True)

    return archivos[0]

def mostrar_estadisticas_filtrado(df_original, df_filtrado, condiciones_aplicadas):
    """Muestra estadísticas detalladas del filtrado."""
    log_filtrado("", "INFO")
    log_filtrado("="*60, "INFO")
    log_filtrado("ESTADÍSTICAS DE FILTRADO", "INFO")
    log_filtrado("="*60, "INFO")
    log_filtrado(f"Registros originales: {len(df_original):,}", "INFO")
    log_filtrado(f"Registros resultantes: {len(df_filtrado):,}", "SUCCESS")

    if len(df_original) > 0:
        porcentaje = (len(df_filtrado) / len(df_original)) * 100
        log_filtrado(f"Porcentaje retenido: {porcentaje:.2f}%", "INFO")

    log_filtrado("", "INFO")
    log_filtrado("Condiciones aplicadas:", "INFO")
    for i, cond in enumerate(condiciones_aplicadas, 1):
        log_filtrado(f"  {i}. {cond}", "INFO")

    if len(df_filtrado) > 0:
        log_filtrado("", "INFO")
        log_filtrado("Resumen de datos filtrados:", "INFO")

        # Columnas clave para mostrar estadísticas
        try:
            col_capacidad = df_filtrado.iloc[:, 12]
            col_inscritos = df_filtrado.iloc[:, 13]

            log_filtrado(f"  Total capacidad: {col_capacidad.sum():,}", "INFO")
            log_filtrado(f"  Total inscritos: {col_inscritos.sum():,}", "INFO")

            if col_capacidad.sum() > 0:
                ocupacion = (col_inscritos.sum() / col_capacidad.sum()) * 100
                log_filtrado(f"  Ocupación promedio: {ocupacion:.2f}%", "INFO")
        except:
            pass

    log_filtrado("="*60, "INFO")

def limpiar_ids_enteros(df):
    """
    Elimina el sufijo .0 de las columnas de identificación (IDs, Cédulas, Aulas).
    Esto ocurre cuando pandas interpreta enteros como floats por tener nulos.

    CORREGIDO: Ahora hace una copia explícita para evitar SettingWithCopyWarning.
    """
    # IMPORTANTE: Crear una copia explícita para evitar warnings
    df = df.copy()

    columnas_ids = [
        'Num_identificacion',
        'Id_aula',
        'Id_grupo',
        'Num_grupo',
        'Id_sede',
        'Id_regional',
        'Num_capacidad'
    ]

    for col in columnas_ids:
        if col in df.columns:
            # 1. Asegurar que es string
            df[col] = df[col].astype(str)
            # 2. Reemplazar '.0' al final de la cadena
            df[col] = df[col].str.replace(r'\.0$', '', regex=True)
            # 3. Limpiar valores 'nan' o 'None' que quedan como texto
            df[col] = df[col].replace({'nan': '', 'None': '', '<NA>': ''})

    return df

def filtrar_datos():
    """Aplica los filtros configurados al archivo consolidado."""
    log_filtrado("INICIANDO PROCESO DE FILTRADO", "INFO")

    # Determinar carpeta objetivo
    carpeta_objetivo = config.CARPETA_DESCARGAS

    if not os.path.exists(carpeta_objetivo):
        log_filtrado(carpeta_objetivo)
        log_filtrado("Carpeta configurada no existe, buscando la más reciente...", "WARNING")
        carpeta_objetivo = obtener_carpeta_mas_reciente()

        if not carpeta_objetivo:
            log_filtrado("No se encontraron carpetas de descarga", "ERROR")
            log_filtrado("Ejecuta primero 1_Descargar.py", "INFO")
            return False

    # Buscar archivo consolidado
    archivo_entrada = buscar_archivo_consolidado(carpeta_objetivo)

    if not archivo_entrada:
        log_filtrado("No se encontró archivo consolidado en la carpeta", "ERROR")
        log_filtrado("Ejecuta primero 2_Consolidar.py", "INFO")
        return False

    log_filtrado(f"Archivo de entrada: {os.path.basename(archivo_entrada)}", "INFO")

    # Generar nombre de archivo de salida con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = os.path.join(carpeta_objetivo, f"Filtrado_TodasLasEscuelas_{timestamp}.xlsx")

    try:
        # Leer archivo
        log_filtrado("Leyendo archivo consolidado...", "INFO")
        df = pd.read_excel(archivo_entrada, engine='openpyxl')
        log_filtrado(f"✓ Archivo leído: {len(df):,} registros", "SUCCESS")

        # Construir condiciones
        log_filtrado("Aplicando filtros...", "INFO")

        condiciones_texto = []

        # 1. Filtro por Dependencia (columna AO = índice 40)
       # condicion_dependencia = (df.iloc[:, 40] == DEPENDENCIA_OBJETIVO)
       # condiciones_texto.append(f'Dependencia = "{DEPENDENCIA_OBJETIVO}"')

        # 2. Excluir materias con patrón PRACTICA (columna G = índice 6)
        condicion_practica = (~df.iloc[:, 6].astype(str).str.contains(
            PATRON_EXCLUIR, regex=True, case=False, na=False
        ))
        condiciones_texto.append(f'Materia NO contiene "{PATRON_EXCLUIR}"')

        # 3. Excluir materias específicas
        condicion_materias = True
        # for materia in MATERIAS_EXCLUIDAS:
        #     condicion_materias = condicion_materias & (df.iloc[:, 6] != materia)
        #     condiciones_texto.append(f'Materia != "{materia}"')

        # 4. Capacidad != 0 (columna M = índice 12)
        condicion_capacidad = (df.iloc[:, 12] != 0)
        condiciones_texto.append("Capacidad != 0")

        # 5. Inscritos != 0 (columna N = índice 13)
        condicion_inscritos = (df.iloc[:, 13] != 0)
        condiciones_texto.append("Inscritos != 0")

        # 6. Fecha de inicio (columna U = índice 20)
        if VALORES_FECHAS_MULTIPLES:
            condicion_fecha = df.iloc[:, 20].isin(VALORES_FECHAS_MULTIPLES)
            fechas_str = ", ".join(VALORES_FECHAS_MULTIPLES)
            condiciones_texto.append(f"Fecha inicio en: {fechas_str}")
        else:
            condicion_fecha = (df.iloc[:, 20] == VALOR_FECHA_FILTRO)
            condiciones_texto.append(f'Fecha inicio = "{VALOR_FECHA_FILTRO}"')

        # Combinar todas las condiciones
        condicion_final = (
            #condicion_dependencia &
            condicion_practica &
            condicion_materias &
            condicion_capacidad &
            condicion_inscritos &
            condicion_fecha
        )

        # Aplicar filtro
        df_filtrado = df[condicion_final].copy()  # ← IMPORTANTE: .copy() para evitar warnings

        # Mostrar estadísticas
        mostrar_estadisticas_filtrado(df, df_filtrado, condiciones_texto)

        # Guardar resultado
        if not df_filtrado.empty:
            log_filtrado("Limpiando formatos de IDs (.0)...", "INFO")
            df_filtrado = limpiar_ids_enteros(df_filtrado)

            # Guardar en CSV y Excel
            df_filtrado.to_csv(
                archivo_salida.replace(".xlsx", ".csv"),
                index=False,
                encoding='utf-8-sig',
                sep=','
            )
            df_filtrado.to_excel(archivo_salida, index=False, engine='openpyxl')

            log_filtrado("", "INFO")
            log_filtrado(f"Archivo guardado: {os.path.basename(archivo_salida)}", "SUCCESS")
            log_filtrado(f"Ruta completa: {archivo_salida}", "INFO")
            return True
        else:
            log_filtrado("", "WARNING")
            log_filtrado("El filtro no arrojó resultados (0 filas)", "WARNING")
            log_filtrado(f"Verifica el valor de fecha: {VALOR_FECHA_FILTRO}", "INFO")
            log_filtrado("O revisa las otras condiciones de filtrado", "INFO")
            return False

    except Exception as e:
        log_filtrado(f"Error procesando el archivo: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("\n" + "="*60)
    print("🔍 FILTRADOR DE REPORTES ICEBERG")
    print("="*60 + "\n")

    exito = filtrar_datos()

    if exito:
        log_filtrado("\n✅ Proceso completado exitosamente", "SUCCESS")
        return 0
    else:
        log_filtrado("\n⚠️  Proceso completado (revisar advertencias)", "WARNING")
        return 0  # No es un error fatal si no hay resultados

if __name__ == "__main__":
    import sys
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)