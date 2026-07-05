# Notas de seguridad y operación

## Archivos que no se deben subir

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

## Recomendaciones

1. Mantener el repositorio privado si contiene lógica institucional.
2. No almacenar credenciales personales en el código.
3. Usar variables/secrets para valores sensibles.
4. Evitar subir reportes descargados.
5. Mantener registros de versión con Git.
6. Validar cambios primero en local o Codespaces antes de afectar Streamlit Cloud.

## Riesgos operativos

- ICEBERG puede cambiar su interfaz.
- ICEBERG puede bloquear accesos desde ciertos entornos cloud.
- Streamlit Cloud puede cambiar su imagen base.
- Playwright puede requerir nuevas dependencias.
