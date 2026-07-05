# Prueba de despliegue en Streamlit Community Cloud - ICEBERG

Este documento sirve para probar si la app ICEBERG puede funcionar en **Streamlit Community Cloud**.

## 1. Objetivo

Validar si Streamlit Cloud puede ejecutar:

- Streamlit.
- Playwright.
- Chromium.
- Login a ICEBERG.
- Descarga de archivos.
- Consolidación.
- Filtrado.
- Descarga ZIP.

## 2. Advertencia importante

Streamlit Cloud puede ser suficiente para publicar la app por URL, pero esta prueba debe confirmar dos cosas:

1. Que Playwright/Chromium funcione correctamente.
2. Que ICEBERG permita acceso desde el entorno cloud.

Si alguna de esas dos falla, la opción más sólida seguirá siendo Docker en una máquina controlada o servidor.

## 3. Archivos necesarios

En la raíz del repo deben existir:

```text
app.py
1_Descargar.py
2_Consolidar.py
config.py
requirements.txt
packages.txt
.streamlit/config.toml
```

Opcionalmente:

```text
cloud_runtime.py
```

## 4. requirements.txt

Debe incluir:

```txt
streamlit>=1.58.0
pandas
openpyxl
python-dotenv
playwright
odfpy
```

Streamlit Community Cloud usa archivos de dependencias Python como `requirements.txt` para instalar paquetes. También permite un archivo `packages.txt` para dependencias externas del sistema.

## 5. packages.txt

Se recomienda agregar un archivo `packages.txt` para dependencias Linux de Chromium/Playwright.

Contenido inicial sugerido:

```txt
libasound2
libatk-bridge2.0-0
libatk1.0-0
libatspi2.0-0
libcairo2
libcups2
libdbus-1-3
libdrm2
libgbm1
libglib2.0-0
libgtk-3-0
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

## 6. Variables sugeridas para Streamlit Cloud

En la app, usar modo web:

```env
ICEBERG_MODO_LOCAL=false
ICEBERG_ENTORNO=streamlit_cloud
PYTHONIOENCODING=utf-8
PYTHONUTF8=1
```

En Streamlit Cloud estas variables pueden manejarse desde Secrets o desde el propio código si no son sensibles.

## 7. Credenciales ICEBERG

Por ahora se recomienda que cada usuario escriba sus credenciales en la interfaz.

No subir `.env` al repositorio.

## 8. Parche opcional para Chromium

Si Streamlit Cloud instala Playwright pero no descarga Chromium, puede aparecer un error como:

```text
Executable doesn't exist at ~/.cache/ms-playwright/...
Please run: playwright install
```

Para manejarlo, se puede usar `cloud_runtime.py`.

En `app.py`, cerca de los imports o antes de validar credenciales:

```python
try:
    from cloud_runtime import preparar_playwright_cloud
    preparar_playwright_cloud()
except Exception as e:
    st.warning(f"No fue posible preparar Playwright automáticamente: {e}")
```

## 9. Pasos de despliegue

1. Subir repo a GitHub.
2. Verificar que no se suba `.env`.
3. Entrar a Streamlit Community Cloud.
4. Crear una nueva app desde el repo.
5. Seleccionar rama.
6. Seleccionar archivo principal:

```text
app.py
```

7. En Advanced settings, seleccionar versión de Python compatible.
8. Agregar secrets si se van a usar.
9. Deploy.

## 10. Checklist de validación

- [ ] La app despliega sin error.
- [ ] La app muestra modo web o Streamlit Cloud.
- [ ] No aparecen botones de abrir carpeta/archivo.
- [ ] Playwright inicia Chromium.
- [ ] El login a ICEBERG funciona.
- [ ] Descarga archivos.
- [ ] Consolida.
- [ ] Filtra.
- [ ] Permite descargar archivo seleccionado.
- [ ] Permite descargar ZIP completo.

## 11. Posibles resultados

### Resultado A: funciona completo

Streamlit Cloud puede ser candidato para publicación simple por URL.

### Resultado B: falla Playwright

Revisar logs, `packages.txt` y posible uso de `cloud_runtime.py`.

### Resultado C: falla acceso a ICEBERG

ICEBERG puede estar bloqueando acceso desde el entorno cloud. En ese caso, usar Docker en un entorno con acceso permitido.

### Resultado D: se cae por tiempo o recursos

Usar Docker o servidor controlado.

## 12. Decisión recomendada

- Si Streamlit Cloud funciona: usarlo como alternativa simple.
- Si no funciona: mantener Codespaces para pruebas y Docker como candidato estable.
