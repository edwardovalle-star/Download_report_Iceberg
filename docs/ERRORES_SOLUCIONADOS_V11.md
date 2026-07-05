# Errores solucionados v11

## Repositorio no encontrado

Solución:

```text
Repository: edwardovalle-star/Download_report_Iceberg
Branch: main
Main file path: app.py
```

## packages.txt con comentarios

Error:

```text
Unable to locate package #
Unable to locate package Dependencias
```

Solución: dejar solo nombres de paquetes.

## Conflicto Debian

Error:

```text
libcups2t64 : Breaks: libcups2
libglib2.0-0t64 : Breaks: libglib2.0-0
```

Solución: usar paquetes compatibles `t64`.

## Código PowerShell pegado en packages.txt

Error:

```text
Unable to locate package $txt
xargs: unmatched single quote
```

Solución: limpiar `packages.txt`.

## Streamlit no encontrado

Error:

```text
streamlit: command not found
```

Solución: agregar `streamlit` a `requirements.txt`.

## Chromium no descargado

Error:

```text
BrowserType.launch: Executable doesn't exist
Please run: playwright install
```

Solución: ejecutar `python -m playwright install chromium`.
