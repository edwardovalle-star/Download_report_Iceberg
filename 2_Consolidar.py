import os
import glob
import pandas as pd
from datetime import datetime
import config

def log_consolidacion(mensaje: str, tipo: str = "INFO"):
    """Log específico para consolidación."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    simbolos = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    simbolo = simbolos.get(tipo, "•")
    print(f"[{timestamp}] {simbolo} {mensaje}")

def obtener_carpeta_mas_reciente():
    """
    Busca la carpeta de descarga más reciente en descargas_iceberg.
    Retorna la ruta completa o None si no hay carpetas.
    """
    if not os.path.exists(config.CARPETA_BASE):
        return None
    
    carpetas = []
    for item in os.listdir(config.CARPETA_BASE):
        ruta_completa = os.path.join(config.CARPETA_BASE, item)
        if os.path.isdir(ruta_completa) and item.startswith(config.CARPETA_ICEBERG):
            carpetas.append((ruta_completa, os.path.getctime(ruta_completa)))
    
    if not carpetas:
        return None
    
    # Ordenar por fecha de creación y devolver la más reciente
    carpetas.sort(key=lambda x: x[1], reverse=True)
    return carpetas[0][0]

def leer_falso_excel(ruta_archivo):
    """
    Intenta leer un archivo de texto plano disfrazado de Excel (.xls).
    Prueba separadores comunes (Tab y Coma) y codificación latin-1.
    """
    try:
        # Intento 1: Texto separado por Tabulaciones (Formato más común en reportes legacy)
        df = pd.read_csv(ruta_archivo, sep='\t', encoding='latin-1', on_bad_lines='skip')
        
        # Validación: Si solo tiene 1 columna, probablemente el separador falló
        if df.shape[1] < 2:
            raise ValueError("Posible error de separador (Tabs)")
        return df
        
    except Exception:
        try:
            # Intento 2: Texto separado por Comas o Punto y Coma
            df = pd.read_csv(ruta_archivo, sep=None, engine='python', encoding='latin-1')
            return df
        except Exception as e:
            log_consolidacion(f"Error interpretando archivo de texto: {e}", "WARNING")
            return None

def limpiar_ids_enteros(df):
    """
    Elimina el sufijo .0 de las columnas de identificación (IDs, Cédulas, Aulas).
    Esto ocurre cuando pandas interpreta enteros como floats por tener nulos.
    """
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

def consolidar_archivos(source_folder):
    """Busca archivos descargados, los interpreta y consolida en un Excel real."""
    log_consolidacion("INICIANDO CONSOLIDACIÓN (TEXTO PLANO -> EXCEL)", "INFO")
    log_consolidacion(f"Carpeta objetivo: {source_folder}", "INFO")

    if not os.path.exists(source_folder):
        log_consolidacion(f"La carpeta {source_folder} no existe", "ERROR")
        return False

    # Buscar archivos con varias extensiones
    extensions = ['*.xls', '*.txt', '*.csv', '*.ods', '*.xlsx']
    archivos = []
    for ext in extensions:
        archivos.extend(glob.glob(os.path.join(source_folder, ext)))
    
    # Excluir archivos consolidados previos y temporales
    archivos = [f for f in archivos 
                if "Consolidado_Final" not in f 
                and "~$" not in f
                and not os.path.basename(f).startswith("Log_")]

    if not archivos:
        log_consolidacion("No hay archivos para consolidar en la carpeta", "WARNING")
        return False

    log_consolidacion(f"Encontrados {len(archivos)} archivo(s) para procesar", "INFO")
    
    lista_dfs = []
    archivos_procesados = 0
    archivos_fallidos = 0

    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        log_consolidacion(f"Procesando: {nombre_archivo}", "INFO")
        
        df = None
        
        # Determinar estrategia de lectura según extensión
        if archivo.endswith('.ods'):
            try:
                df = pd.read_excel(archivo, engine="odf")
            except Exception as e:
                log_consolidacion(f"Error leyendo ODS: {e}", "WARNING")
        elif archivo.endswith('.xlsx'):
            try:
                df = pd.read_excel(archivo)
            except Exception as e:
                log_consolidacion(f"Error leyendo XLSX: {e}", "WARNING")
        else:
            # Asumimos que es el "falso excel" (Texto plano)
            df = leer_falso_excel(archivo)

        if df is not None and not df.empty:
            # Limpieza: Eliminar comillas dobles en columnas
            df.columns = df.columns.str.replace('"', '').str.strip()
            
            # Limpieza: Eliminar comillas en los datos de texto
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.replace('"', '').str.strip()

            lista_dfs.append(df)
            archivos_procesados += 1
            log_consolidacion(f"✓ Procesado ({len(df)} registros)", "SUCCESS")
        else:
            archivos_fallidos += 1
            log_consolidacion("✗ FALLÓ o archivo vacío", "ERROR")

    # Generar consolidado
    if lista_dfs:
        try:
            consolidado = pd.concat(lista_dfs, ignore_index=True)
            log_consolidacion("Limpiando formatos de IDs (.0)...", "INFO")
            consolidado = limpiar_ids_enteros(consolidado)
            # Guardar con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(source_folder, f"Consolidado_Final_OcupacionDocente.xlsx")
            consolidado.to_csv(output_path.replace(".xlsx", ".csv"), index=False, encoding='utf-8-sig', sep=',')
            consolidado.to_excel(output_path, index=False, engine='openpyxl')
            
            log_consolidacion("", "INFO")
            log_consolidacion("="*60, "INFO")
            log_consolidacion("CONSOLIDACIÓN COMPLETADA", "SUCCESS")
            log_consolidacion("="*60, "INFO")
            log_consolidacion(f"Archivo: {os.path.basename(output_path)}", "INFO")
            log_consolidacion(f"Ruta: {output_path}", "INFO")
            log_consolidacion(f"Total de filas: {len(consolidado):,}", "INFO")
            log_consolidacion(f"Total de columnas: {len(consolidado.columns)}", "INFO")
            log_consolidacion(f"Archivos procesados: {archivos_procesados}/{len(archivos)}", "INFO")
            if archivos_fallidos > 0:
                log_consolidacion(f"Archivos fallidos: {archivos_fallidos}", "WARNING")
            log_consolidacion("="*60, "INFO")
            
            return True
            
        except Exception as e:
            log_consolidacion(f"Error guardando consolidado: {e}", "ERROR")
            return False
    else:
        log_consolidacion("No se pudo generar data válida para consolidar", "ERROR")
        return False

def main():
    """Función principal que determina la carpeta a consolidar."""
    print("\n" + "="*60)
    print("🔄 CONSOLIDADOR DE REPORTES ICEBERG")
    print("="*60 + "\n")
    
    # Intentar usar la carpeta configurada (la más reciente)
    carpeta_objetivo = config.CARPETA_DESCARGAS
    
    # Si no existe, buscar la carpeta más reciente manualmente
    if not os.path.exists(carpeta_objetivo):
        log_consolidacion("Carpeta configurada no existe, buscando la más reciente...", "WARNING")
        carpeta_objetivo = obtener_carpeta_mas_reciente()
        
        if not carpeta_objetivo:
            log_consolidacion("No se encontraron carpetas de descarga", "ERROR")
            log_consolidacion("Ejecuta primero 1_Descargar.py", "INFO")
            return 1
        
        log_consolidacion(f"Usando carpeta: {os.path.basename(carpeta_objetivo)}", "INFO")
    
    # Ejecutar consolidación
    exito = consolidar_archivos(carpeta_objetivo)
    
    if exito:
        log_consolidacion("\n✅ Proceso completado exitosamente", "SUCCESS")
        return 0
    else:
        log_consolidacion("\n❌ Proceso completado con errores", "ERROR")
        return 1

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