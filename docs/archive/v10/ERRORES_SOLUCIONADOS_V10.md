# Registro de errores solucionados - ICEBERG v10

## 1. PowerShell bloquea entorno virtual

Error:

```text
Activate.ps1 porque la ejecución de scripts está deshabilitada
```

Solución:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## 2. Playwright no instalado

Error:

```text
No module named playwright
```

Solución:

```powershell
python -m pip install playwright
python -m playwright install chromium
```

---

## 3. Chromium faltante en Codespaces

Error:

```text
Executable doesn't exist at /home/codespace/.cache/ms-playwright/...
```

Solución:

```bash
python -m playwright install chromium
```

---

## 4. Librería Linux faltante

Error:

```text
libatk-1.0.so.0: cannot open shared object file
```

Solución:

```bash
python -m playwright install --with-deps chromium
```

---

## 5. Docker no instalado

Error:

```text
docker : El término 'docker' no se reconoce
```

Solución:

1. Instalar WSL.
2. Reiniciar Windows.
3. Instalar Docker Desktop.
4. Validar:

```powershell
docker --version
docker compose version
```

---

## 6. Falta docker-compose.yml

Error:

```text
no configuration file provided: not found
```

Solución:

Crear `docker-compose.yml` en la raíz del proyecto.

---

## 7. Docker no resuelve ICEBERG

Error:

```text
Page.goto: net::ERR_NAME_NOT_RESOLVED at https://sig.cun.edu.co/icebergrs/
```

Solución aplicada:

Agregar DNS al `docker-compose.yml` si es necesario:

```yaml
dns:
  - 8.8.8.8
  - 1.1.1.1
```

---

## 8. StreamlitDuplicateElementKey

Error:

```text
There are multiple elements with the same key
```

Solución:

- Evitar duplicar paneles.
- Usar keys únicas.
- Dejar un solo panel de archivos generados.

---

## 9. DeltaGenerator visible en pantalla

Causa:

Uso de ternario con funciones de Streamlit.

Solución:

```python
if ok:
    st.success(mensaje)
else:
    st.warning(mensaje)
```

---

## 10. use_container_width obsoleto

Advertencia:

```text
use_container_width will be removed after 2025-12-31
```

Solución:

```python
st.dataframe(df, width="stretch")
```
