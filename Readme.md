# ICEBERG Reportes - App Streamlit v10

Proyecto para **descargar, consolidar, filtrar y consultar reportes académicos de ICEBERG CUN** mediante una aplicación web construida con **Python, Playwright y Streamlit**.

La aplicación permite automatizar el flujo que antes se hacía manualmente:

1. Ingresar a ICEBERG.
2. Seleccionar un reporte.
3. Descargar archivos por periodo.
4. Consolidar los archivos descargados.
5. Filtrar desde datos reales del consolidado.
6. Descargar resultados en Excel, CSV o ZIP.

---

## 1. Estado actual del proyecto

La versión actual fue validada en tres escenarios:

| Entorno | Estado | Uso recomendado |
|---|---:|---|
| Local Windows | Validado | Trabajo diario individual |
| GitHub Codespaces | Validado | Pruebas compartidas fuera de localhost |
| Docker local | Validado | Base para posible despliegue estable |

---

## 2. Modos de ejecución

La app diferencia entre modo local y modo web/servidor usando variables de entorno.

### Modo local Windows

```env
ICEBERG_MODO_LOCAL=true
ICEBERG_ENTORNO=local
```

En este modo aparecen estas acciones:

- Abrir carpeta.
- Abrir ubicación del archivo.
- Abrir archivo directamente.
- Descargar archivo seleccionado.
- Descargar ZIP completo.

### Modo web / Codespaces / Docker

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=codespaces
```

o:

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=docker
```

En este modo se ocultan las acciones locales:

- Abrir carpeta.
- Abrir ubicación.
- Abrir archivo.

Y se mantienen:

- Descargar archivo seleccionado.
- Descargar ZIP completo.

Esto evita confundir al usuario final cuando la app corre en un entorno remoto o contenedor.

---

## 3. Estructura recomendada del proyecto

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
├── .env.example
├── .gitignore
├── .dockerignore
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

> La carpeta `descargas_iceberg/` se genera durante la ejecución y no debe subirse a GitHub.

---

## 4. Archivos principales

| Archivo | Función |
|---|---|
| `app.py` | Aplicación Streamlit principal para usuario final. |
| `1_Descargar.py` | Descarga reportes desde ICEBERG usando Playwright. |
| `2_Consolidar.py` | Consolida archivos descargados en Excel y CSV. |
| `3_Filtrar.py` | Filtra el consolidado para una dependencia específica. |
| `3_2_FiltrarTodasEscuelas.py` | Filtra el consolidado sin limitar a una dependencia. |
| `config.py` | Configuración de reportes, URLs, periodos y carpetas. |
| `requirements.txt` | Dependencias Python. |
| `.streamlit/config.toml` | Configuración de Streamlit. |
| `.devcontainer/devcontainer.json` | Configuración para GitHub Codespaces. |
| `Dockerfile` | Construcción del contenedor Docker. |
| `docker-compose.yml` | Ejecución de Docker Compose. |
| `.env.example` | Plantilla de variables de entorno. |
| `.gitignore` | Archivos que no deben subirse al repositorio. |
| `.dockerignore` | Archivos que no deben copiarse a la imagen Docker. |

---

## 5. Requisitos

### Para ejecución local

- Windows 10/11.
- Python instalado.
- Acceso a internet.
- Usuario y contraseña válidos de ICEBERG.
- Permisos para consultar los reportes.
- Visual Studio Code recomendado.
- PowerShell recomendado.

### Para Codespaces

- Repositorio en GitHub.
- Acceso a GitHub Codespaces.
- Archivo `.devcontainer/devcontainer.json`.
- Puerto `8501` abierto desde la pestaña **Ports**.

### Para Docker

- WSL instalado y actualizado.
- Docker Desktop instalado.
- Docker Compose disponible.

---

## 6. Instalación local en Windows

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Ejecutar local

```powershell
$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"
python -m streamlit run app.py
```

Abrir:

```text
http://localhost:8501
```

---

## 7. Ejecución rápida local después de instalada

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"
python -m streamlit run app.py
```

---

## 8. Uso general de la app

### Paso 1. Validar credenciales

La app solicita usuario y contraseña de ICEBERG. Primero valida que el acceso funcione.

### Paso 2. Descargar y consolidar

Selecciona uno o varios periodos y presiona:

```text
Descargar y consolidar
```

La app ejecuta internamente:

- `1_Descargar.py`
- `2_Consolidar.py`

### Paso 3. Filtrar

La app lee el consolidado y permite filtrar por:

- Dependencia/carrera.
- Fecha de inicio.
- Excluir materias con `PRACTICA`.
- Excluir materias históricas.
- Capacidad diferente de cero.
- Inscritos diferente de cero.

### Paso 4. Archivos generados

La app muestra una tabla seleccionable con archivos generados.

Ejemplos:

```text
Filtrado_Dinamico_*.xlsx
Filtrado_Dinamico_*.csv
Consolidado_Final_OcupacionDocente.xlsx
Consolidado_Final_OcupacionDocente.csv
Ocupacion_Docentes_*.xls
Log_Iceberg_*.log
```

---

## 9. GitHub Codespaces

### 9.1 Subir el proyecto a GitHub

Antes de subir, revisar:

```powershell
git status
```

Confirmar que no aparezcan:

```text
.env
descargas_iceberg/
.venv/
```

Subir cambios:

```powershell
git add .
git commit -m "Version v10 funcional local codespaces docker"
git push
```

### 9.2 Crear Codespace

En GitHub:

```text
Code > Codespaces > Create codespace on main
```

### 9.3 Archivo `.devcontainer/devcontainer.json`

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

### 9.4 Ejecutar Streamlit en Codespaces

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### 9.5 Abrir el puerto

En la pestaña **Ports**, abrir el puerto:

```text
8501
```

La URL será similar a:

```text
https://nombre-del-codespace-8501.app.github.dev
```

### 9.6 Resultado esperado en Codespaces

La app debe mostrar:

```text
Modo actual: GitHub Codespaces
```

Y solo debe permitir:

- Descargar archivo seleccionado.
- Descargar ZIP completo.

---

## 10. Explicación del puerto 8501

Streamlit usa por defecto el puerto:

```text
8501
```

En local:

```text
http://localhost:8501
```

En Codespaces, `localhost` pertenece a la máquina remota de GitHub. Por eso Codespaces reenvía el puerto y genera una URL externa.

Comando recomendado:

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

| Parámetro | Explicación |
|---|---|
| `--server.port 8501` | Define el puerto donde corre Streamlit. |
| `--server.address 0.0.0.0` | Permite exponer la app fuera del contenedor. |

---

## 11. Docker

Docker permite ejecutar la app empaquetada en un contenedor. Esto ayuda a validar que la aplicación no dependa únicamente del entorno local de Windows.

### 11.1 Requisitos para Docker en Windows

Primero instalar WSL:

```powershell
wsl --install
wsl --update
```

Después reiniciar Windows.

Luego instalar Docker Desktop y verificar:

```powershell
docker --version
docker compose version
```

### 11.2 Ejecutar con Docker Compose

Desde la carpeta del proyecto:

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
docker compose up --build
```

Abrir:

```text
http://localhost:8501
```

La app debe mostrar:

```text
Modo actual: Docker / Servidor
```

### 11.3 Detener Docker

```powershell
docker compose down
```

### 11.4 Dockerfile recomendado

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium

COPY . .

ENV ICEBERG_MODO_LOCAL=false
ENV ICEBERG_ENTORNO=docker
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUTF8=1

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

### 11.5 `docker-compose.yml` recomendado

```yaml
services:
  iceberg-streamlit:
    build: .
    container_name: iceberg-streamlit
    ports:
      - "8501:8501"
    environment:
      ICEBERG_MODO_LOCAL: "false"
      ICEBERG_ENTORNO: "docker"
      PYTHONIOENCODING: "utf-8"
      PYTHONUTF8: "1"
    volumes:
      - ./descargas_iceberg:/app/descargas_iceberg
    restart: unless-stopped
```

### 11.6 Si Docker no resuelve `sig.cun.edu.co`

Error:

```text
Page.goto: net::ERR_NAME_NOT_RESOLVED at https://sig.cun.edu.co/icebergrs/
```

Solución inicial:

```yaml
dns:
  - 8.8.8.8
  - 1.1.1.1
```

Ejemplo:

```yaml
services:
  iceberg-streamlit:
    build: .
    container_name: iceberg-streamlit
    ports:
      - "8501:8501"
    environment:
      ICEBERG_MODO_LOCAL: "false"
      ICEBERG_ENTORNO: "docker"
      PYTHONIOENCODING: "utf-8"
      PYTHONUTF8: "1"
    dns:
      - 8.8.8.8
      - 1.1.1.1
    volumes:
      - ./descargas_iceberg:/app/descargas_iceberg
    restart: unless-stopped
```

Luego:

```powershell
docker compose down
docker compose up --build
```

---

## 12. Archivos de configuración recomendados

### 12.1 `requirements.txt`

```txt
streamlit>=1.58.0
pandas
openpyxl
python-dotenv
playwright
odfpy
```

### 12.2 `.streamlit/config.toml`

```toml
[browser]
gatherUsageStats = false

[server]
headless = true
port = 8501
address = "0.0.0.0"
```

### 12.3 `.gitignore`

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

### 12.4 `.dockerignore`

```gitignore
.env
.venv/
__pycache__/
descargas_iceberg/
*.log
*.xls
*.xlsx
*.csv
.git/
```

---

## 13. Errores encontrados y soluciones

| Error | Causa | Solución |
|---|---|---|
| `Activate.ps1 ... ejecución de scripts deshabilitada` | PowerShell bloquea scripts | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `No module named playwright` | Playwright no está instalado en el entorno activo | `python -m pip install playwright` |
| `Executable doesn't exist ... ms-playwright` | Falta descargar Chromium | `python -m playwright install chromium` |
| `libatk-1.0.so.0` | Faltan dependencias Linux de Chromium | `python -m playwright install --with-deps chromium` |
| `use_container_width will be removed` | API antigua de Streamlit | Cambiar a `width="stretch"` |
| `StreamlitDuplicateElementKey` | Dos elementos con la misma key | Usar keys únicas o dejar un solo panel |
| Bloque gigante `DeltaGenerator` | Uso de ternario con `st.success`/`st.warning` | Usar `if/else` normal |
| Abrir carpeta no parece funcionar | Explorador puede quedar detrás del navegador | Usar `explorer.exe` |
| Filtro devuelve 0 filas | Fecha/condiciones/columnas no coinciden | Revisar diagnóstico y columnas |
| `UnicodeEncodeError cp1252` | Consola Windows no soporta caracteres | Usar `PYTHONIOENCODING=utf-8` |
| `docker no se reconoce` | Docker Desktop no está instalado | Instalar Docker Desktop |
| `no configuration file provided: not found` | Falta `docker-compose.yml` | Crear archivo en la raíz del proyecto |
| `ERR_NAME_NOT_RESOLVED` en Docker | DNS del contenedor no resuelve ICEBERG | Agregar DNS o revisar red |

---

## 14. Validación rápida de Playwright

### Windows, Linux, Codespaces o Docker

```bash
python - <<'PYTEST'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
PYTEST
```

Resultado esperado:

```text
Example Domain
```

---

## 15. Seguridad

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
| `*.xls`, `*.xlsx`, `*.csv` | Pueden contener información académica o personal. |
| `*.log` | Puede contener rutas, errores o datos técnicos sensibles. |

---

## 16. Git: subir cambios a GitHub

```powershell
git status
git add .
git commit -m "Actualizar README y documentacion de despliegue"
git pull origin main
git push origin main
```

---

## 17. Checklist antes de considerar estable una versión

### Local Windows

- [ ] La app abre en `http://localhost:8501`.
- [ ] Muestra `Modo actual: Local Windows`.
- [ ] Valida credenciales.
- [ ] Descarga reportes.
- [ ] Consolida.
- [ ] Filtra.
- [ ] Muestra archivos generados.
- [ ] Abre carpeta.
- [ ] Abre ubicación.
- [ ] Abre archivo.
- [ ] Descarga archivo seleccionado.
- [ ] Descarga ZIP completo.

### Codespaces

- [ ] El Codespace instala dependencias.
- [ ] Playwright funciona.
- [ ] La app abre por puerto `8501`.
- [ ] Muestra `Modo actual: GitHub Codespaces`.
- [ ] Valida credenciales.
- [ ] Descarga reportes.
- [ ] Consolida.
- [ ] Filtra.
- [ ] No muestra botones de abrir carpeta/archivo.
- [ ] Descarga archivo seleccionado.
- [ ] Descarga ZIP completo.

### Docker

- [ ] Docker Desktop está instalado.
- [ ] `docker compose up --build` levanta la app.
- [ ] La app abre en `http://localhost:8501`.
- [ ] Muestra `Modo actual: Docker / Servidor`.
- [ ] Valida credenciales.
- [ ] Descarga reportes.
- [ ] Consolida.
- [ ] Filtra.
- [ ] No muestra botones locales.
- [ ] Descarga archivo seleccionado.
- [ ] Descarga ZIP completo.

---

## 18. Recomendación actual

| Escenario | Recomendación |
|---|---|
| Trabajo diario propio | Local Windows |
| Pruebas y demostraciones | GitHub Codespaces |
| Candidato a versión estable | Docker |
| Posible publicación simple | Evaluar Streamlit Cloud |

---

## 19. Pendientes sugeridos para versiones futuras

- Agregar historial de ejecuciones.
- Agregar limpieza automática de carpetas antiguas.
- Agregar página de ayuda dentro de la app.
- Agregar resumen final de ejecución.
- Agregar control de usuarios si se comparte públicamente.
- Evaluar Streamlit Cloud.
- Evaluar Docker en nube o servidor institucional.
- Agregar logs más amigables para usuario final.
- Agregar modo solo consulta.
- Agregar selector de reporte desde la interfaz.

---

## 20. Autor / responsable

Equipo LITE - Escuela de Ingeniería de Sistemas.

---

## 21. Nota final

Esta documentación corresponde a la versión v10 del proyecto, validada en modo local, GitHub Codespaces y Docker local.

Si ICEBERG cambia su interfaz, nombres de botones, estructura de reportes, permisos o políticas de acceso, puede ser necesario ajustar el código de automatización.
