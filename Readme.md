# ICEBERG Reportes - App Streamlit v11

Aplicación para descargar, consolidar, filtrar y consultar reportes académicos desde ICEBERG CUN usando Python, Playwright, Streamlit, Pandas y OpenPyXL.

## Estado validado

| Entorno | Estado |
|---|---:|
| Local Windows | Funcionando |
| GitHub Codespaces | Funcionando |
| Docker local | Funcionando |
| Streamlit Cloud | Funcionando |

## Objetivo

Automatizar el flujo de consulta de reportes ICEBERG:

1. Validar credenciales.
2. Descargar reportes por periodo.
3. Consolidar archivos descargados.
4. Aplicar filtros dinámicos.
5. Generar archivos Excel/CSV.
6. Permitir descarga individual o ZIP.

## Modos de ejecución

### Local Windows

```env
ICEBERG_MODO_LOCAL=true
ICEBERG_ENTORNO=local
```

Habilita abrir carpeta, abrir ubicación, abrir archivo y descargar resultados.

### GitHub Codespaces

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=codespaces
```

### Docker

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=docker
```

### Streamlit Cloud

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=streamlit_cloud
```

En entornos web/servidor se ocultan las acciones locales y se mantienen solo descargas.

## Estructura recomendada

```text
descarga_iceberg/
├── app.py
├── 1_Descargar.py
├── 2_Consolidar.py
├── 3_Filtrar.py
├── 3_2_FiltrarTodasEscuelas.py
├── config.py
├── requirements.txt
├── packages.txt
├── cloud_runtime.py
├── Dockerfile
├── docker-compose.yml
├── README.md
├── .env.example
├── .gitignore
├── .dockerignore
├── .streamlit/config.toml
├── .devcontainer/devcontainer.json
└── descargas_iceberg/
```

## requirements.txt

```txt
streamlit
pandas
openpyxl
python-dotenv
playwright
odfpy
```

## packages.txt para Streamlit Cloud

Debe contener solo paquetes, sin comentarios:

```txt
libasound2t64
libatk-bridge2.0-0t64
libatk1.0-0t64
libatspi2.0-0t64
libcairo2
libcups2t64
libdbus-1-3
libdrm2
libgbm1
libglib2.0-0t64
libgtk-3-0t64
libnspr4
libnss3
libpango-1.0-0
libx11-6
libx11-xcb1
libxcb1
libxcomposite1
libxdamage1
libxext6
libxfixes3
libxkbcommon0
libxrandr2
xvfb
```

## Ejecución local

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"
python -m streamlit run app.py
```

Abrir:

```text
http://localhost:8501
```

## Ejecución en Codespaces

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Abrir el puerto 8501 desde la pestaña Ports.

## Ejecución con Docker

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
docker compose up --build
```

Abrir:

```text
http://localhost:8501
```

Detener:

```powershell
docker compose down
```

## Streamlit Cloud

Configuración usada:

| Campo | Valor |
|---|---|
| Repository | `edwardovalle-star/Download_report_Iceberg` |
| Branch | `main` |
| Main file path | `app.py` |

Variables recomendadas:

```toml
ICEBERG_MODO_LOCAL = "false"
ICEBERG_ENTORNO = "streamlit_cloud"
PYTHONIOENCODING = "utf-8"
PYTHONUTF8 = "1"
```

## Playwright en Streamlit Cloud

Error corregido:

```text
Executable doesn't exist at /home/appuser/.cache/ms-playwright/...
Please run: playwright install
```

Solución aplicada: preparar Chromium con:

```bash
python -m playwright install chromium
```

antes de validar credenciales.

## Seguridad

No subir a GitHub:

```text
.env
.streamlit/secrets.toml
descargas_iceberg/
.venv/
*.xls
*.xlsx
*.csv
*.log
```

## Versión

Nombre sugerido:

```text
v11 - Streamlit Cloud funcional
```

Comandos recomendados:

```powershell
git status
git add .
git commit -m "Validar version v11 en Streamlit Cloud"
git push origin main
git tag v11-streamlit-cloud
git push origin v11-streamlit-cloud
```
