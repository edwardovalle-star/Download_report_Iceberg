# ICEBERG Reportes - Guía de usuario y despliegue v10

Este proyecto permite descargar, consolidar, filtrar y consultar reportes académicos desde la plataforma **ICEBERG CUN**.

La versión actual incluye dos formas principales de uso:

1. **Uso local en Windows**, ideal para el usuario que ejecuta la app en su propio computador.
2. **Uso en GitHub Codespaces**, ideal para probar o compartir la app fuera de `localhost`.

Además, la app ahora cuenta con una interfaz en **Streamlit** que permite:

- Validar credenciales de ICEBERG antes de descargar.
- Seleccionar periodos académicos.
- Descargar reportes.
- Consolidar archivos descargados.
- Filtrar desde datos reales del consolidado.
- Ver diagnóstico del filtro.
- Consultar archivos generados en una tabla seleccionable.
- Descargar archivos individuales.
- Descargar un ZIP completo con los resultados.
- Abrir carpetas o archivos cuando se ejecuta en modo local Windows.

---

## 1. Objetivo del proyecto

Automatizar el proceso de descarga y tratamiento de reportes de ICEBERG para evitar tareas manuales repetitivas como:

- Ingresar a ICEBERG.
- Seleccionar reporte.
- Elegir periodo por periodo.
- Descargar archivos.
- Consolidar manualmente varios archivos.
- Filtrar información por dependencia, fecha, capacidad, inscritos o materias.

---

## 2. Estado actual de la versión v10

La versión v10 está preparada para trabajar en dos modos:

| Modo | Uso principal | Acciones disponibles |
|---|---|---|
| Local Windows | Ejecutar desde el computador del usuario | Abrir carpeta, abrir ubicación, abrir archivo, descargar archivo, descargar ZIP |
| Web / Codespaces / Docker | Ejecutar fuera del computador local | Descargar archivo seleccionado y descargar ZIP completo |

Esto se controla con variables de entorno:

```env
ICEBERG_MODO_LOCAL=true
ICEBERG_ENTORNO=local
```

o:

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=codespaces
```

---

## 3. Estructura actual recomendada del proyecto

La carpeta del proyecto debería verse así:

```text
descarga_iceberg/
│
├── app.py
├── app_v10_despliegue.py
├── 1_Descargar.py
├── 2_Consolidar.py
├── 3_Filtrar.py
├── 3_2_FiltrarTodasEscuelas.py
├── config.py
├── requirements.txt
├── README.md
├── README_V10_DESPLIEGUE.md
├── .env.example
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── .devcontainer/
│   └── devcontainer.json
│
├── Dockerfile
├── docker-compose.yml
│
└── descargas_iceberg/
```

> La carpeta `descargas_iceberg/` se crea durante la ejecución y no debe subirse a GitHub.

---

## 4. Explicación de archivos principales

| Archivo o carpeta | Descripción |
|---|---|
| `app.py` | Aplicación principal en Streamlit. Es la interfaz para usuario final. |
| `app_v10_despliegue.py` | Copia de respaldo de la versión v10. |
| `1_Descargar.py` | Automatiza la descarga de reportes desde ICEBERG usando Playwright. |
| `2_Consolidar.py` | Consolida los archivos descargados en Excel y CSV. |
| `3_Filtrar.py` | Filtra el consolidado para una dependencia específica. |
| `3_2_FiltrarTodasEscuelas.py` | Filtra el consolidado sin restringir a una sola dependencia. |
| `config.py` | Configuración de reportes, periodos, URLs y carpetas. |
| `requirements.txt` | Librerías necesarias del proyecto. |
| `.streamlit/config.toml` | Configuración de Streamlit. |
| `.devcontainer/devcontainer.json` | Configuración para GitHub Codespaces. |
| `Dockerfile` | Configuración para crear una imagen Docker. |
| `docker-compose.yml` | Ejecución con Docker Compose. |
| `.env.example` | Plantilla de variables de entorno. |
| `.gitignore` | Lista de archivos que no deben subirse a GitHub. |

---

## 5. Requisitos generales

Para ejecución local:

- Python instalado.
- Acceso a internet.
- Usuario y contraseña válidos de ICEBERG.
- Permisos para consultar los reportes requeridos.
- Visual Studio Code recomendado.
- PowerShell recomendado en Windows.

Para Codespaces:

- Repositorio en GitHub.
- Acceso a GitHub Codespaces.
- Archivos `.devcontainer/devcontainer.json` y `requirements.txt` en el repositorio.
- Puerto `8501` habilitado desde la pestaña **Ports**.

---

## 6. Variables de entorno principales

### 6.1 Modo local Windows

Usar cuando la app se ejecuta en el computador del usuario.

```env
ICEBERG_MODO_LOCAL=true
ICEBERG_ENTORNO=local
```

En este modo la app muestra botones para:

- Abrir carpeta.
- Abrir ubicación del archivo.
- Abrir archivo directamente.
- Descargar archivo.
- Descargar ZIP.

### 6.2 Modo Codespaces

Usar cuando la app corre en GitHub Codespaces.

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=codespaces
```

En este modo la app oculta:

- Abrir carpeta.
- Abrir ubicación.
- Abrir archivo.

Y deja visibles:

- Descargar archivo seleccionado.
- Descargar ZIP completo.

### 6.3 Modo Docker

Usar cuando la app corre en contenedor Docker.

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=docker
```

---

## 7. Instalación y ejecución local en Windows

### 7.1 Abrir PowerShell en el proyecto

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
```

### 7.2 Crear entorno virtual

```powershell
python -m venv .venv
```

Si `python` no funciona:

```powershell
py -m venv .venv
```

### 7.3 Activar entorno virtual

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
```

Debe aparecer algo similar a:

```powershell
(.venv) PS C:\Users\ASUS\Documents\Github\descarga_iceberg>
```

### 7.4 Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 7.5 Instalar Chromium de Playwright

```powershell
python -m playwright install chromium
```

### 7.6 Ejecutar la app local

```powershell
$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"

python -m streamlit run app.py
```

La app debe abrir en:

```text
http://localhost:8501
```

---

## 8. Ejecución rápida local después de instalada

Cuando ya instalaste todo una vez, en próximas ejecuciones basta con:

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate

$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"

python -m streamlit run app.py
```

---

## 9. Uso de la app Streamlit en modo local

### Paso 1. Iniciar sesión

La app solicita usuario y contraseña de ICEBERG.

Primero valida que las credenciales sean correctas. Si el login funciona, permite continuar con la descarga.

### Paso 2. Descargar y consolidar

El usuario selecciona los periodos académicos y presiona:

```text
Descargar y consolidar
```

La app ejecuta:

- `1_Descargar.py`
- `2_Consolidar.py`

### Paso 3. Filtrar desde datos reales

Después de consolidar, la app lee el archivo consolidado y muestra:

- Dependencias/carreras encontradas.
- Fechas de inicio encontradas.
- Condiciones adicionales:
  - Excluir PRACTICA.
  - Excluir materias históricas.
  - Capacidad diferente de 0.
  - Inscritos diferente de 0.

### Paso 4. Archivos generados

La app muestra una tabla seleccionable con archivos como:

- `Filtrado_Dinamico_*.xlsx`
- `Filtrado_Dinamico_*.csv`
- `Consolidado_Final_OcupacionDocente.xlsx`
- `Consolidado_Final_OcupacionDocente.csv`
- `Ocupacion_Docentes_*.xls`
- `Log_Iceberg_*.log`

En modo local, permite:

- Abrir carpeta.
- Abrir ubicación del archivo.
- Abrir archivo.
- Descargar archivo.
- Descargar ZIP.

---

## 10. Ejecución en GitHub Codespaces

GitHub Codespaces permite ejecutar la app en una máquina remota de GitHub, sin depender del equipo local.

### 10.1 Subir el proyecto a GitHub

Desde el equipo local:

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg

git status
git add .
git commit -m "v10 funcional con Streamlit y Codespaces"
git push
```

Antes de subir, confirmar que no se suban:

```text
.env
descargas_iceberg/
.venv/
__pycache__/
```

### 10.2 Crear Codespace

En GitHub:

```text
Code > Codespaces > Create codespace on main
```

### 10.3 Verificar archivo `.devcontainer/devcontainer.json`

Debe existir:

```text
.devcontainer/devcontainer.json
```

Contenido recomendado:

```json
{
  "name": "ICEBERG Streamlit",
  "image": "mcr.microsoft.com/playwright/python:v1.55.0-noble",
  "postCreateCommand": "pip install --no-cache-dir -r requirements.txt && python -m playwright install --with-deps chromium",
  "forwardPorts": [8501],
  "portsAttributes": {
    "8501": {
      "label": "ICEBERG Streamlit",
      "onAutoForward": "openBrowser"
    }
  },
  "containerEnv": {
    "ICEBERG_MODO_LOCAL": "false",
    "ICEBERG_ENTORNO": "codespaces",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1"
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
    }
  }
}
```

### 10.4 Si no existe `.devcontainer/devcontainer.json`

Crearlo desde terminal:

```bash
mkdir -p .devcontainer
nano .devcontainer/devcontainer.json
```

Pegar el contenido recomendado, guardar con:

```text
Ctrl + O
Enter
Ctrl + X
```

Luego subirlo:

```bash
git status
git add .devcontainer/devcontainer.json
git commit -m "Agregar configuracion de Codespaces"
git push
```

### 10.5 Reconstruir el contenedor si modificaste el JSON

En Codespaces:

```text
Ctrl + Shift + P
```

Buscar:

```text
Codespaces: Rebuild Container
```

o:

```text
Dev Containers: Rebuild Container
```

### 10.6 Instalar dependencias manualmente si es necesario

Si el entorno no quedó listo automáticamente:

```bash
pip install --no-cache-dir -r requirements.txt
python -m playwright install --with-deps chromium
```

Si ya están las dependencias Linux y solo falta el navegador:

```bash
python -m playwright install chromium
```

### 10.7 Ejecutar Streamlit en Codespaces

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### 10.8 Abrir el puerto

En la pestaña **Ports**, buscar:

```text
8501
```

Abrirlo en el navegador.

El enlace generado será algo similar a:

```text
https://nombre-del-codespace-8501.app.github.dev
```

---

## 11. Qué es el puerto 8501

Streamlit usa por defecto el puerto:

```text
8501
```

En local se accede normalmente por:

```text
http://localhost:8501
```

En Codespaces, `localhost` pertenece a la máquina remota de GitHub. Por eso GitHub debe reenviar el puerto `8501` y entregar una URL externa.

El comando recomendado es:

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Donde:

| Parte | Significado |
|---|---|
| `--server.port 8501` | Indica que Streamlit usará el puerto 8501. |
| `--server.address 0.0.0.0` | Permite que Codespaces exponga la app fuera del contenedor. |

---

## 12. Visibilidad del puerto en Codespaces

En la pestaña **Ports**, el puerto puede estar en:

| Visibilidad | Significado |
|---|---|
| Private | Solo tú puedes abrir la app autenticado en GitHub. |
| Organization | Solo miembros de la organización pueden abrirla, si aplica. |
| Public | Cualquiera con el enlace puede abrirla. |

Recomendación para pruebas:

```text
Private
```

Solo cambiar a `Public` cuando se quiera compartir una prueba controlada.

---

## 13. Uso en Codespaces

En Codespaces la app debe mostrar:

```text
Modo actual: GitHub Codespaces
```

En este modo no deben aparecer:

- Abrir carpeta.
- Abrir ubicación.
- Abrir archivo.

Solo deben aparecer:

- Descargar archivo seleccionado.
- Descargar ZIP completo.

Esto es correcto porque Codespaces no puede abrir el Explorador de archivos del computador del usuario.

---

## 14. Docker como alternativa de despliegue

La v10 incluye `Dockerfile` y `docker-compose.yml`.

### 14.1 Ejecutar con Docker Compose

```bash
docker compose up --build
```

Abrir:

```text
http://localhost:8501
```

### 14.2 Ejecutar con Docker manualmente

```bash
docker build -t iceberg-streamlit .
```

```bash
docker run --rm -p 8501:8501 -e ICEBERG_MODO_LOCAL=false -e ICEBERG_ENTORNO=docker iceberg-streamlit
```

---

## 15. Archivo `requirements.txt` recomendado

```txt
streamlit>=1.58.0
pandas
openpyxl
python-dotenv
playwright
odfpy
```

---

## 16. Archivo `.streamlit/config.toml` recomendado

```toml
[browser]
gatherUsageStats = false

[server]
headless = true
port = 8501
address = "0.0.0.0"
```

---

## 17. Archivo `.gitignore` recomendado

```gitignore
.env
.streamlit/secrets.toml
descargas_iceberg/
__pycache__/
*.pyc
.venv/
.env.local
*.log
*.png
*.xls
*.xlsx
*.csv
```

---

## 18. Errores encontrados durante el desarrollo y solución

### 18.1 PowerShell no permite activar `.venv`

Error:

```text
Activate.ps1 porque la ejecución de scripts está deshabilitada en este sistema.
```

Solución:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
```

---

### 18.2 `No module named playwright`

Significa que Playwright no está instalado en el entorno activo.

Solución:

```powershell
python -m pip install playwright python-dotenv
python -m playwright install chromium
```

---

### 18.3 Falta Chromium de Playwright en Codespaces

Error:

```text
Executable doesn't exist at /home/codespace/.cache/ms-playwright/...
Looks like Playwright was just installed or updated.
Please run the following command to download new browsers:
playwright install
```

Solución:

```bash
python -m playwright install chromium
```

Si también faltan dependencias Linux:

```bash
python -m playwright install --with-deps chromium
```

---

### 18.4 Falta librería Linux `libatk-1.0.so.0`

Error:

```text
libatk-1.0.so.0: cannot open shared object file: No such file or directory
```

Significa que Chromium no puede iniciar porque faltan dependencias del sistema.

Solución:

```bash
python -m playwright install --with-deps chromium
```

O:

```bash
sudo apt-get update
python -m playwright install --with-deps chromium
```

---

### 18.5 Advertencia de Streamlit `use_container_width`

Mensaje:

```text
Please replace use_container_width with width.
use_container_width will be removed after 2025-12-31.
```

Solución:

Cambiar:

```python
st.dataframe(df, use_container_width=True)
```

por:

```python
st.dataframe(df, width="stretch")
```

---

### 18.6 `StreamlitDuplicateElementKey`

Error:

```text
StreamlitDuplicateElementKey: There are multiple elements with the same key
```

Causa:

La app estaba mostrando dos veces el panel de archivos generados con la misma `key`.

Solución:

- Dejar un solo panel de archivos generados.
- Usar keys únicas por contexto.
- En v9/v10 se dejó un solo panel al final del filtrado.

---

### 18.7 Mensaje gigante `DeltaGenerator`

Síntoma:

Después de presionar `Abrir carpeta`, la app mostraba un bloque enorme con información interna de Streamlit.

Causa:

Se usó una expresión tipo:

```python
st.success(mensaje) if ok else st.warning(mensaje)
```

Solución:

Usar estructura normal:

```python
if ok:
    st.success(mensaje)
else:
    st.warning(mensaje)
```

---

### 18.8 Botón abrir carpeta no parece abrir nada

Causa posible:

Windows puede abrir el Explorador detrás del navegador o no traerlo al frente.

Solución implementada:

- Usar `explorer.exe`.
- Si la ruta es carpeta, abrir la carpeta.
- Si la ruta es archivo, abrir la carpeta y seleccionar el archivo.

---

### 18.9 El filtro devuelve 0 filas

Causas posibles:

- Fecha no existe en el consolidado.
- Dependencia no coincide exactamente.
- Condiciones de capacidad o inscritos dejan todo en cero.
- Materias excluidas eliminan todos los registros.
- Se estaba usando una columna incorrecta para capacidad.

Solución aplicada en la app:

- Usar la columna `Capacidad` antes que `Num_capacidad`.
- Mostrar diagnóstico del filtro.
- Cargar fechas y dependencias reales desde el consolidado.

---

### 18.10 Error de codificación `cp1252` por emojis

Error posible en Windows:

```text
UnicodeEncodeError: 'charmap' codec can't encode character
```

Solución:

Configurar en la ejecución:

```python
env["PYTHONIOENCODING"] = "utf-8"
env["PYTHONUTF8"] = "1"
```

O ejecutar en PowerShell:

```powershell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
```

---

## 19. Validación rápida de Playwright

### Windows, Linux o Codespaces

```bash
python - <<'PY'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
PY
```

Resultado esperado:

```text
Example Domain
```

---

## 20. Seguridad

No subir ni compartir:

```text
.env
.streamlit/secrets.toml
descargas_iceberg/
.venv/
__pycache__/
*.log
*.xls
*.xlsx
*.csv
```

Motivos:

| Archivo o carpeta | Motivo |
|---|---|
| `.env` | Puede contener usuario y contraseña. |
| `.streamlit/secrets.toml` | Puede contener secretos. |
| `descargas_iceberg/` | Contiene reportes descargados desde ICEBERG. |
| `.venv/` | Entorno local pesado y reconstruible. |
| `*.xls`, `*.xlsx`, `*.csv` | Pueden contener datos académicos o personales. |
| `*.log` | Puede contener rutas, errores o información sensible. |

---

## 21. Git: subir cambios a GitHub

### 21.1 Revisar estado

```powershell
git status
```

Confirmar que no aparezcan:

```text
.env
descargas_iceberg/
```

### 21.2 Agregar cambios

```powershell
git add .
```

### 21.3 Crear commit

```powershell
git commit -m "Actualizar README y configuracion v10"
```

### 21.4 Subir a GitHub

```powershell
git push
```

Flujo completo recomendado:

```powershell
git status
git add .
git commit -m "Actualizar documentacion v10"
git pull origin main
git push origin main
```

---

## 22. Qué probar antes de dar por estable una versión

### Local

- La app abre en `http://localhost:8501`.
- Muestra `Modo actual: Local Windows`.
- Valida credenciales.
- Descarga reportes.
- Consolida.
- Filtra.
- Muestra archivos.
- Abre carpeta.
- Abre ubicación.
- Abre archivo.
- Descarga archivo.
- Descarga ZIP.

### Codespaces

- El Codespace instala dependencias.
- Playwright funciona.
- La app abre por puerto `8501`.
- Muestra `Modo actual: GitHub Codespaces`.
- Valida credenciales.
- Descarga reportes.
- Consolida.
- Filtra.
- No muestra botones de abrir carpeta/archivo.
- Descarga archivo seleccionado.
- Descarga ZIP completo.

---

## 23. Recomendación de uso actual

Para pruebas controladas:

```text
GitHub Codespaces
```

Para uso diario individual:

```text
Local Windows
```

Para versión institucional más estable:

```text
Docker en servidor o máquina controlada
```

---

## 24. Pendientes sugeridos para una versión futura

- Agregar página de ayuda dentro de la app.
- Agregar historial de ejecuciones.
- Agregar limpieza automática de carpetas antiguas.
- Agregar control de roles si se comparte públicamente.
- Evaluar despliegue final en Docker.
- Evaluar Streamlit Cloud si ICEBERG permite acceso externo.
- Agregar logs más amigables para usuario final.
- Agregar resumen final de ejecución con filas descargadas, consolidadas y filtradas.
- Agregar modo solo consulta para usuarios que no deban descargar desde ICEBERG.

---

## 25. Autor / responsable

Equipo LITE - Escuela de Ingeniería de Sistemas.

---

## 26. Nota final

Esta documentación corresponde a la versión v10 del proyecto, validada en modo local y en GitHub Codespaces.

Si ICEBERG cambia su interfaz, nombres de botones, estructura de reportes o permisos, puede ser necesario ajustar el código de automatización.
