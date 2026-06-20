"""
4_CargarBD.py - Carga de datos a PostgreSQL
============================================
Busca el archivo Consolidado_Final más reciente y lo carga a PostgreSQL.
Incluye backup automático de datos anteriores.
"""

import os
import glob
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import config

def log_bd(mensaje: str, tipo: str = "INFO"):
    """Log específico para carga de BD."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    simbolos = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    simbolo = simbolos.get(tipo, "•")
    print(f"[{timestamp}] {simbolo} {mensaje}")

def limpiar_nombres_columnas(df):
    """
    Normaliza los nombres de las columnas para coincidir con PostgreSQL.
    Ejemplo: 'Correo Institucional' -> 'correo_institucional'
    """
    # Convertir a minúsculas y reemplazar espacios
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('.', '_')
        .str.replace('á', 'a').str.replace('é', 'e')
        .str.replace('í', 'i').str.replace('ó', 'o')
        .str.replace('ú', 'u').str.replace('ñ', 'n')
    )
    
    # Mapeos específicos
    renames = {
        "fec_finn_grupo": "fec_fin_grupo",  # Doble n
        "nom_sede_1": "nom_sede_alt",  # Columna duplicada
    }
    df = df.rename(columns=renames)
    
    return df

def transformar_datos(df):
    """Transforma y limpia los datos antes de cargar."""
    log_bd("Transformando datos...", "INFO")
    
    # Convertir vacíos a None (NULL en SQL)
    df = df.where(pd.notnull(df), None)
    
    # Fechas (DD/MM/YYYY -> YYYY-MM-DD)
    cols_fecha = ['fec_inicio_grupo', 'fec_fin_grupo']
    for col in cols_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
    
    # Números decimales (coma -> punto)
    cols_decimales = ['porcentaje_ocupacion_aula', 'num_capacidad']
    for col in cols_decimales:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Números enteros
    cols_enteros = ['creditos', 'capacidad', 'num_inscritos', 'inscritos_neto', 
                    'num_nivel', 'num_grupo', 'num_capacidad', 'id_grupo']
    for col in cols_enteros:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')
    
    # Booleanos
    if 'check_moodle' in df.columns:
        df['check_moodle'] = df['check_moodle'].astype(str).str.strip() == '1'
    
    # Agregar campos de gestión
    df['estado_gestion'] = 'PENDIENTE'
    df['origen_dato'] = 'CARGA_MASIVA'
    df['fecha_carga'] = datetime.now()
    
    log_bd(f"✓ Datos transformados: {len(df)} registros", "SUCCESS")
    return df

def realizar_backup(conn, tabla_principal: str, tabla_historial: str):
    """Realiza backup de la tabla principal al historial."""
    log_bd(f"Creando backup de '{tabla_principal}'...", "INFO")
    
    try:
        # Verificar si existe la tabla principal
        check_query = text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{tabla_principal}'
            )
        """)
        tabla_existe = conn.execute(check_query).scalar()
        
        if not tabla_existe:
            log_bd(f"Tabla '{tabla_principal}' no existe (primera carga)", "WARNING")
            return False
        
        # Crear tabla de historial si no existe
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {tabla_historial} (
                LIKE {tabla_principal} INCLUDING ALL
            );
        """))
        
        # Agregar columna de timestamp si no existe
        conn.execute(text(f"""
            ALTER TABLE {tabla_historial} 
            ADD COLUMN IF NOT EXISTS fecha_archivado TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """))
        
        # Copiar datos actuales al historial
        conn.execute(text(f"""
            INSERT INTO {tabla_historial} 
            SELECT *, CURRENT_TIMESTAMP as fecha_archivado
            FROM {tabla_principal}
        """))
        
        # Contar registros archivados
        result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla_principal}"))
        count = result.scalar()
        
        log_bd(f"✓ Backup completado: {count:,} registros archivados", "SUCCESS")
        return True
        
    except Exception as e:
        log_bd(f"Error en backup: {e}", "ERROR")
        return False

def cargar_a_postgresql(df, tabla_principal: str = 'tbl_aca_consolidado'):
    """Carga el DataFrame a PostgreSQL con backup automático."""
    log_bd("="*60, "INFO")
    log_bd("INICIANDO CARGA A POSTGRESQL", "INFO")
    log_bd("="*60, "INFO")
    
    try:
        # Crear engine
        engine = create_engine(config.DATABASE_URL)
        
        # Verificar conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log_bd("✓ Conexión a BD establecida", "SUCCESS")
        
        with engine.begin() as conn:
            # Backup de datos anteriores
            tabla_historial = f"{tabla_principal}_historial"
            realizar_backup(conn, tabla_principal, tabla_historial)
            
            # Verificar si tabla existe
            check_query = text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{tabla_principal}'
                )
            """)
            tabla_existe = conn.execute(check_query).scalar()
            
            if tabla_existe:
                # Limpiar tabla existente
                log_bd(f"Limpiando tabla '{tabla_principal}'...", "INFO")
                conn.execute(text(f"TRUNCATE TABLE {tabla_principal} CASCADE"))
                modo_carga = 'append'
            else:
                log_bd(f"Tabla '{tabla_principal}' no existe, se creará", "WARNING")
                modo_carga = 'replace'
            
            # Cargar datos nuevos
            log_bd(f"Cargando {len(df):,} registros (modo: {modo_carga})...", "INFO")
            
            df.to_sql(
                tabla_principal,
                conn,
                if_exists=modo_carga,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            # Verificar carga
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla_principal}"))
            count_final = result.scalar()
            
            log_bd("", "INFO")
            log_bd("="*60, "INFO")
            log_bd("CARGA COMPLETADA", "SUCCESS")
            log_bd("="*60, "INFO")
            log_bd(f"Registros cargados: {count_final:,}", "INFO")
            log_bd(f"Tabla: {tabla_principal}", "INFO")
            log_bd("="*60, "INFO")
            
        engine.dispose()
        return True
        
    except Exception as e:
        log_bd(f"Error durante carga a BD: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def cargar_y_procesar_csv(ruta_csv):
    """Lee y procesa el archivo CSV."""
    log_bd(f"Leyendo archivo: {os.path.basename(ruta_csv)}", "INFO")
    
    if not os.path.exists(ruta_csv):
        log_bd("Archivo no existe", "ERROR")
        return None
    
    try:
        # Intentar diferentes separadores
        df = None
        
        # Intento 1: Punto y coma
        try:
            df = pd.read_csv(ruta_csv, sep=';', encoding='latin-1', dtype=str)
            if len(df.columns) >= 2:
                log_bd("✓ Archivo leído con separador ';'", "SUCCESS")
        except:
            pass
        
        # Intento 2: Coma
        if df is None or len(df.columns) < 2:
            try:
                df = pd.read_csv(ruta_csv, sep=',', encoding='utf-8', dtype=str)
                log_bd("✓ Archivo leído con separador ','", "SUCCESS")
            except:
                pass
        
        # Intento 3: Tabulador
        if df is None or len(df.columns) < 2:
            df = pd.read_csv(ruta_csv, sep='\t', encoding='latin-1', dtype=str)
            log_bd("✓ Archivo leído con separador TAB", "SUCCESS")
        
        log_bd(f"Filas leídas: {len(df):,}", "INFO")
        log_bd(f"Columnas: {len(df.columns)}", "INFO")
        
        # Limpiar nombres de columnas
        df = limpiar_nombres_columnas(df)
        
        # Transformar datos
        df = transformar_datos(df)
        
        return df
        
    except Exception as e:
        log_bd(f"Error procesando CSV: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def buscar_archivo_reciente(nombre_archivo: str, carpeta_base: str):
    """
    Busca recursivamente el archivo más reciente con el nombre dado.
    """
    log_bd(f"Buscando '{nombre_archivo}' en '{carpeta_base}'...", "INFO")
    
    if not os.path.exists(carpeta_base):
        log_bd(f"Carpeta base no existe: {carpeta_base}", "ERROR")
        return None
    
    archivos_encontrados = []
    
    # Recorrer árbol de directorios
    for root, dirs, files in os.walk(carpeta_base):
        if nombre_archivo in files:
            ruta_completa = os.path.join(root, nombre_archivo)
            tiempo_modificacion = os.path.getmtime(ruta_completa)
            archivos_encontrados.append((ruta_completa, tiempo_modificacion))
    
    if not archivos_encontrados:
        log_bd("No se encontró el archivo", "ERROR")
        return None
    
    # Ordenar por fecha (más reciente primero)
    archivos_encontrados.sort(key=lambda x: x[1], reverse=True)
    
    archivo_mas_reciente = archivos_encontrados[0][0]
    fecha_mod = datetime.fromtimestamp(archivos_encontrados[0][1])
    
    log_bd(f"✓ Archivo encontrado", "SUCCESS")
    log_bd(f"  Ruta: {archivo_mas_reciente}", "INFO")
    log_bd(f"  Modificado: {fecha_mod.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    
    return archivo_mas_reciente

def main():
    """Función principal."""
    print("\n" + "="*60)
    print("💾 CARGA A BASE DE DATOS - Iceberg RPA")
    print("="*60 + "\n")
    
    inicio = datetime.now()
    
    # Configuración
    NOMBRE_ARCHIVO = "Consolidado_Final_OcupacionDocente.csv"
    CARPETA_BUSQUEDA = config.CARPETA_BASE
    
    # Buscar archivo más reciente
    ruta_archivo = buscar_archivo_reciente(NOMBRE_ARCHIVO, CARPETA_BUSQUEDA)
    
    if not ruta_archivo:
        log_bd("No se pudo iniciar carga: archivo no encontrado", "ERROR")
        log_bd("Ejecuta primero 2_Consolidar.py", "INFO")
        return 1
    
    # Procesar CSV
    df_procesado = cargar_y_procesar_csv(ruta_archivo)
    
    if df_procesado is None:
        log_bd("Error procesando CSV", "ERROR")
        return 1
    
    # Cargar a PostgreSQL
    if not cargar_a_postgresql(df_procesado):
        log_bd("Error en carga a BD", "ERROR")
        return 1
    
    # Resumen final
    fin = datetime.now()
    duracion = (fin - inicio).total_seconds()
    
    print("\n" + "="*60)
    log_bd(f"PROCESO COMPLETADO EN {duracion:.2f} segundos", "SUCCESS")
    print("="*60 + "\n")
    
    return 0

if __name__ == "__main__":
    import sys
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Proceso interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)