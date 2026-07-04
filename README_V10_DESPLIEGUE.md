# ICEBERG Reportes - v10 despliegue

Esta versión está preparada para probar la app en:

- Equipo local Windows.
- GitHub Codespaces.
- Docker.
- Posible despliegue web.

## Cambio principal de v10

Se agrega soporte para dos modos:

### Modo local Windows

```env
ICEBERG_MODO_LOCAL=true
ICEBERG_ENTORNO=local
```

Muestra:

- Abrir carpeta.
- Abrir ubicación del archivo.
- Abrir archivo directamente.
- Descargar archivo.
- Descargar ZIP.

### Modo web / servidor

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=codespaces
```

Oculta:

- Abrir carpeta.
- Abrir ubicación del archivo.
- Abrir archivo directamente.

Mantiene:

- Descargar archivo seleccionado.
- Descargar ZIP completo.

Esto evita confundir al usuario cuando la app corre en Codespaces, Docker o Streamlit Cloud.

## Ejecución local

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg

python -m pip install -r requirements.txt
python -m playwright install chromium

$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"

python -m streamlit run app.py
```

## GitHub Codespaces

El proyecto incluye:

```text
.devcontainer/devcontainer.json
```

Al abrir el repo en Codespaces, se instala:

- Python.
- Dependencias de `requirements.txt`.
- Chromium para Playwright.

Para ejecutar:

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Luego abre el puerto 8501 desde la pestaña **Ports**.

En Codespaces ya se define:

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=codespaces
```

## Docker

Construir:

```bash
docker build -t iceberg-streamlit .
```

Ejecutar:

```bash
docker run --rm -p 8501:8501 -e ICEBERG_MODO_LOCAL=false -e ICEBERG_ENTORNO=docker iceberg-streamlit
```

Con `docker-compose`:

```bash
docker compose up --build
```

Abrir:

```text
http://localhost:8501
```

## Archivos importantes

```text
app.py
1_Descargar.py
2_Consolidar.py
config.py
requirements.txt
.streamlit/config.toml
.devcontainer/devcontainer.json
Dockerfile
docker-compose.yml
.env.example
.gitignore
```

## Seguridad

No subas credenciales al repositorio.

No subas:

```text
.env
.streamlit/secrets.toml
descargas_iceberg/
```

La app actualmente pide usuario y contraseña de ICEBERG desde la interfaz.

## Prueba recomendada

1. Probar local con `ICEBERG_MODO_LOCAL=true`.
2. Subir repo a GitHub.
3. Abrir Codespace.
4. Ejecutar Streamlit.
5. Confirmar si ICEBERG permite login desde Codespaces.
6. Si funciona, evaluar Docker o Streamlit Cloud como versión final.
