# Guia de usuario - ICEBERG Reportes v12

## 1. Objetivo de la herramienta

La aplicacion permite descargar, consolidar, reutilizar y filtrar reportes de ICEBERG desde una interfaz web.

La version v12 incluye:

- Inicio de sesion controlado.
- Nueva busqueda sin cerrar sesion.
- Cierre de sesion.
- Reutilizacion de consolidados generados durante la misma sesion.
- Filtrado en memoria.
- Filtros avanzados dependientes estilo Excel.
- Descarga o guardado del filtro solo cuando el usuario lo decida.

## 2. Inicio de sesion

Al abrir la aplicacion, el usuario debe ingresar sus credenciales de ICEBERG.

Mientras no exista una sesion validada, no se muestran las opciones de descarga, consolidacion ni filtrado.

## 3. Nueva busqueda y cierre de sesion

En la barra lateral se encuentran dos acciones principales.

### Nueva busqueda

Limpia la busqueda actual, el consolidado activo y los filtros aplicados.

No cierra la sesion del usuario.

Los consolidados generados durante la sesion actual se mantienen disponibles en la seccion "Mis consolidados de esta sesion".

### Cerrar sesion

Cierra completamente la sesion actual.

Tambien limpia los consolidados de la sesion, filtros y estado temporal.

## 4. Descarga y consolidacion

El usuario selecciona los parametros del reporte y ejecuta la descarga.

La aplicacion genera los archivos base y consolida la informacion en un archivo principal.

Cuando existe un consolidado activo, la aplicacion muestra directamente el panel de filtrado.

## 5. Mis consolidados de esta sesion

La seccion "Mis consolidados de esta sesion" permite reutilizar consolidados generados durante la sesion actual del navegador.

Estos consolidados no son una bitacora global.

Cada usuario ve solamente los consolidados generados durante su propia sesion.

Al cargar un consolidado anterior, la aplicacion crea una copia de trabajo para evitar mezclar filtros nuevos con ejecuciones anteriores.

## 6. Filtros principales

Los filtros principales permiten consultar el consolidado por criterios frecuentes:

- Dependencia o carrera.
- Fecha de inicio.
- Excluir PRACTICA.
- Excluir materias historicas.
- Capacidad diferente de cero.
- Inscritos diferente de cero.

Estos filtros se aplican sobre los datos reales del consolidado.

## 7. Filtros avanzados opcionales

La seccion "Filtros avanzados opcionales" permite agregar criterios adicionales por cualquier campo disponible en el consolidado.

Cada filtro avanzado permite seleccionar:

- Campo.
- Condicion.
- Valores disponibles.

Los valores disponibles son dependientes de los filtros principales y de los filtros avanzados anteriores.

Esto evita seleccionar combinaciones que no existen en el consolidado.

## 8. Condiciones disponibles

Los filtros avanzados permiten usar condiciones como:

- Incluir seleccionados.
- Excluir seleccionados.
- Contiene.
- No contiene.
- Vacio.
- No vacio.
- Mayor que.
- Menor que.
- Mayor o igual.
- Menor o igual.

## 9. Resultado del filtro

Al aplicar el filtro, la aplicacion muestra un resumen en tabla con dos columnas:

- Campo.
- Valor.

Este resumen permite validar rapidamente los criterios aplicados.

Tambien se muestra una vista previa del resultado filtrado.

## 10. Descargar o guardar el filtro

El filtro no se guarda automaticamente en la carpeta del consolidado.

El usuario puede decidir entre:

### Descargar Excel

Descarga el resultado filtrado al equipo del usuario.

### Descargar CSV

Descarga el resultado filtrado en formato CSV.

### Guardar en carpeta

Guarda el resultado filtrado en la carpeta de trabajo del consolidado activo.

Esta opcion es util cuando el usuario quiere conservar el filtro junto con la ejecucion.

## 11. Recomendaciones de uso

- Aplicar primero filtros principales.
- Luego agregar filtros avanzados.
- Revisar el resumen de filtros aplicados.
- Validar la vista previa.
- Descargar o guardar solo cuando el resultado sea correcto.

## 12. Diferencia entre descargar y guardar

Descargar envia el archivo al computador del usuario.

Guardar en carpeta conserva el archivo dentro de la carpeta activa del consolidado.

La aplicacion no crea archivos de filtro automaticamente al aplicar filtros.
