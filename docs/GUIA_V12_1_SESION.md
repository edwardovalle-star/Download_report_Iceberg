# ICEBERG app.py v12.1

Cambios incluidos:

1. Botón Nueva búsqueda.
   - Limpia resultados, filtros y selección de archivos.
   - Mantiene sesión validada.

2. Botón Cerrar sesión.
   - Limpia credenciales y estado completo de la app.

3. Botón Cambiar credenciales.
   - Cierra la sesión actual y vuelve al formulario de login.

4. Cierre por inactividad.
   - Por defecto: 30 minutos.
   - Variable opcional:
     ICEBERG_INACTIVIDAD_MINUTOS=30

5. Limpieza visual de formularios.
   - Se agregaron keys dinámicas para resetear periodos y filtros.

Instalación:

1. Reemplazar app.py por este archivo.
2. Ejecutar localmente.
3. Probar login, descarga, filtro, nueva búsqueda y cierre de sesión.
4. Subir a rama v12-mejoras-operativas.

Comandos sugeridos:

```powershell
Copy-Item .\app_v12_1.py .\app.py -Force
python -m streamlit run app.py
git status
git add app.py
git commit -m "Agregar controles de sesion v12.1"
git push origin v12-mejoras-operativas
```
