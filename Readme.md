# Bot de Descarga de Reportes ICEBERG

Este proyecto permite descargar automáticamente reportes desde la plataforma **ICEBERG CUN** usando **Python** y **Playwright**.

El programa abre ICEBERG, inicia sesión, entra al reporte configurado, selecciona cada periodo, descarga los archivos y luego permite consolidarlos en un archivo final de Excel.

---

## 1. ¿Para qué sirve este proyecto?

Este bot sirve para automatizar la descarga, consolidación y filtrado de reportes de ICEBERG, evitando que el usuario tenga que ingresar manualmente a la plataforma, seleccionar periodo por periodo, descargar cada archivo y unirlos manualmente.

Actualmente el proyecto permite descargar reportes como:

- Ocupación docente.
- Estudiantes matriculados.
- Estudiantes con pago, matrícula y datos de contacto.
- Estudiantes con pago sin inscripción de matrícula.

---

## 2. ¿Qué necesita tener el usuario antes de empezar?

Antes de ejecutar el proyecto, el usuario debe tener:

- Un computador con Windows, Linux o macOS.
- Python instalado.
- Acceso a internet.
- Usuario y contraseña válidos de ICEBERG.
- Permisos en ICEBERG para consultar los reportes.
- El proyecto descargado o compartido en una carpeta local.

En Windows, se recomienda usar:

- **PowerShell**
- **Visual Studio Code**
- **Explorador de archivos**

---

## 3. Estructura esperada del proyecto

La carpeta del proyecto debe verse más o menos así:

```bash
descarga_iceberg/
│
├── 1_Descargar.py
├── 2_Consolidar.py
├── 3_Filtrar.py
├── 3_2_FiltrarTodasEscuelas.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

Explicación sencilla:

| Archivo | ¿Para qué sirve? |
|---|---|
| `1_Descargar.py` | Descarga los reportes desde ICEBERG. |
| `2_Consolidar.py` | Consolida los archivos descargados en un Excel final. |
| `3_Filtrar.py` | Filtra el consolidado final para una dependencia específica, por ejemplo Ingeniería de Sistemas. |
| `3_2_FiltrarTodasEscuelas.py` | Filtra el consolidado final sin limitarlo a una sola dependencia o escuela. |
| `config.py` | Tiene la configuración de reportes, periodos, URLs y carpetas. |
| `requirements.txt` | Lista las librerías que se deben instalar. |
| `.env` | Guarda el usuario y contraseña de ICEBERG. No se comparte. |
| `.env.example` | Ejemplo para que otro usuario sepa qué debe poner en su `.env`. |
| `.gitignore` | Indica qué archivos no se deben subir o compartir. |
| `README.md` | Documento con instrucciones del proyecto. |

---

## 4. Cómo leer correctamente este README en Visual Studio Code

Si abres el archivo `README.md` en VSCode, normalmente se abre en modo texto. Para verlo como documento bonito, debes abrir la vista previa.

### Opción 1: abrir vista previa

Con el archivo `README.md` abierto, presiona:

```bash
Ctrl + Shift + V
```

### Opción 2: abrir vista previa al lado

Con el archivo `README.md` abierto, presiona:

```bash
Ctrl + K
```

Luego suelta las teclas y presiona:

```bash
V
```

Esto abre el README en una columna al lado, mientras el archivo editable queda en la otra.

---

## 5. Cómo tener botón de copiar en los comandos del README

En algunos visores como GitHub aparece automáticamente un botón para copiar los comandos.

En VSCode, normalmente no aparece ese botón por defecto. Para tener un botón de copiar en los bloques de código, instala una extensión.

### Pasos para instalar la extensión

1. Abre Visual Studio Code.
2. Ve al menú lateral izquierdo.
3. Haz clic en el ícono de extensiones.
4. También puedes abrir extensiones con:

```bash
Ctrl + Shift + X
```

5. En el buscador escribe:

```bash
Markdown Code Copy Button
```

6. Instala la extensión.
7. Abre nuevamente el archivo `README.md`.
8. Abre la vista previa con:

```bash
Ctrl + Shift + V
```

9. Pasa el mouse encima de un bloque de código.
10. Debería aparecer un botón para copiar el comando.

---

## 6. Cómo crear una carpeta para el proyecto en Windows

### Forma visual

1. Abre el Explorador de archivos.
2. Entra a la ubicación donde quieres guardar el proyecto, por ejemplo:

```bash
Documentos/Github
```

3. Haz clic derecho en un espacio en blanco.
4. Selecciona:

```bash
Nuevo > Carpeta
```

5. Coloca este nombre:

```bash
descarga_iceberg
```

6. Entra a la carpeta haciendo doble clic.

### Forma por PowerShell

Abre PowerShell y ejecuta:

```powershell
cd C:\Users\ASUS\Documents\Github
mkdir descarga_iceberg
cd descarga_iceberg
```

---

## 7. Cómo crear archivos manualmente en Windows

Si necesitas crear archivos como `requirements.txt`, `.env`, `.env.example` o `.gitignore`, puedes hacerlo desde el Explorador de archivos.

### Paso recomendado: mostrar extensiones de archivo

Antes de crear los archivos, activa la visualización de extensiones.

1. Abre el Explorador de archivos.
2. En la parte superior, haz clic en **Ver**.
3. Entra a **Mostrar**.
4. Activa la opción:

```bash
Extensiones de nombre de archivo
```

Esto es importante para evitar que Windows cree archivos como:

```bash
.env.txt
requirements.txt.txt
```

El nombre correcto debe ser:

```bash
.env
requirements.txt
```

No debe terminar en `.txt` adicional.

---

## 8. Crear el archivo `requirements.txt`

Este archivo indica qué librerías necesita el proyecto para descargar y consolidar los reportes.

### Forma visual

1. Entra a la carpeta del proyecto.
2. Haz clic derecho en un espacio en blanco.
3. Selecciona:

```bash
Nuevo > Documento de texto
```

4. Cambia el nombre del archivo a:

```bash
requirements.txt
```

5. Ábrelo con Bloc de notas o VSCode.
6. Escribe esto:

```txt
playwright
python-dotenv
pandas
openpyxl
odfpy
```

7. Guarda el archivo.

### Forma por PowerShell

Desde la carpeta del proyecto:

```powershell
notepad requirements.txt
```

Pega este contenido:

```txt
playwright
python-dotenv
pandas
openpyxl
odfpy
```

Guarda y cierra.

---

## 9. Crear el archivo `.env`

El archivo `.env` guarda las credenciales de ICEBERG.

> Este archivo no se debe compartir.

### Forma visual

1. Entra a la carpeta del proyecto.
2. Haz clic derecho en un espacio en blanco.
3. Selecciona:

```bash
Nuevo > Documento de texto
```

4. Cambia el nombre del archivo a:

```bash
.env
```

5. Si Windows muestra una advertencia sobre cambiar la extensión, acepta.
6. Abre el archivo con Bloc de notas o VSCode.
7. Escribe:

```env
ICEBERG_USER=tu_usuario_iceberg
ICEBERG_PASS=tu_contraseña_iceberg
```

Ejemplo:

```env
ICEBERG_USER=usuario_prueba
ICEBERG_PASS=ClaveSegura123
```

8. Guarda el archivo.

### Forma por PowerShell

Desde la carpeta del proyecto:

```powershell
notepad .env
```

Pega:

```env
ICEBERG_USER=tu_usuario_iceberg
ICEBERG_PASS=tu_contraseña_iceberg
```

Guarda y cierra.

---

## 10. Crear el archivo `.env.example`

Este archivo sirve para compartir el proyecto con otra persona sin entregar la contraseña real.

### Forma visual

1. En la carpeta del proyecto, haz clic derecho en un espacio en blanco.
2. Selecciona:

```bash
Nuevo > Documento de texto
```

3. Cambia el nombre a:

```bash
.env.example
```

4. Ábrelo y escribe:

```env
ICEBERG_USER=colocar_usuario_iceberg
ICEBERG_PASS=colocar_contraseña_iceberg
```

5. Guarda el archivo.

### Forma por PowerShell

```powershell
notepad .env.example
```

Contenido:

```env
ICEBERG_USER=colocar_usuario_iceberg
ICEBERG_PASS=colocar_contraseña_iceberg
```

---

## 11. Crear el archivo `.gitignore`

Este archivo evita que se compartan archivos sensibles o innecesarios.

### Forma visual

1. En la carpeta del proyecto, haz clic derecho en un espacio en blanco.
2. Selecciona:

```bash
Nuevo > Documento de texto
```

3. Cambia el nombre a:

```bash
.gitignore
```

4. Ábrelo y escribe:

```gitignore
.env
.venv/
__pycache__/
descargas_iceberg/
*.log
*.png
*.xls
*.xlsx
```

5. Guarda el archivo.

### Forma por PowerShell

```powershell
notepad .gitignore
```

Contenido:

```gitignore
.env
.venv/
__pycache__/
descargas_iceberg/
*.log
*.png
*.xls
*.xlsx
```

---

## 12. Abrir PowerShell en la carpeta del proyecto

### Opción 1: desde Visual Studio Code

1. Abre la carpeta del proyecto en VSCode.
2. En el menú superior selecciona:

```bash
Terminal > New Terminal
```

3. Se abrirá una terminal en la parte inferior.

### Opción 2: desde el Explorador de archivos

1. Entra a la carpeta del proyecto.
2. Haz clic en la barra de dirección del Explorador.
3. Escribe:

```bash
powershell
```

4. Presiona Enter.

Esto abre PowerShell directamente en esa carpeta.

### Opción 3: desde PowerShell manualmente

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
```

---

## 13. Crear el entorno virtual

El entorno virtual es una carpeta local donde se instalan las librerías del proyecto.

Desde PowerShell, dentro de la carpeta del proyecto, ejecuta:

```powershell
python -m venv .venv
```

Si `python` no funciona, prueba:

```powershell
py -m venv .venv
```

Después de ejecutarlo, aparecerá una carpeta llamada:

```bash
.venv
```

---

## 14. Activar el entorno virtual

En PowerShell ejecuta:

```powershell
.\.venv\Scripts\activate
```

Si todo sale bien, la terminal debe mostrar algo así:

```powershell
(.venv) PS C:\Users\ASUS\Documents\Github\descarga_iceberg>
```

El texto `(.venv)` indica que el entorno virtual está activo.

---

## 15. Error común: PowerShell no permite activar el entorno virtual

Puede aparecer un error como este:

```powershell
No se puede cargar el archivo .venv\Scripts\Activate.ps1 porque la ejecución de scripts está deshabilitada en este sistema.
```

Esto ocurre porque PowerShell tiene bloqueada la ejecución de scripts.

### Solución recomendada

Ejecuta este comando:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Luego vuelve a activar el entorno:

```powershell
.\.venv\Scripts\activate
```

Esta solución solo aplica para la ventana actual de PowerShell. Cuando cierres esa ventana, la configuración vuelve a la normalidad.

---

## 16. Instalar las librerías del proyecto

Con el entorno virtual activo `(.venv)`, ejecuta:

```powershell
python -m pip install -r requirements.txt
```

También puedes usar:

```powershell
pip install -r requirements.txt
```

Si todo está bien, se instalarán:

- `playwright`
- `python-dotenv`
- `pandas`
- `openpyxl`
- `odfpy`

---

## 17. Aviso común de pip: `Cache entry deserialization failed`

Puede aparecer este mensaje:

```powershell
WARNING: Cache entry deserialization failed, entry ignored
```

No es un error grave. Normalmente significa que una parte de la caché de `pip` no se pudo leer.

Puedes continuar.

Si quieres limpiarlo, ejecuta:

```powershell
pip cache purge
```

Y luego vuelve a instalar:

```powershell
python -m pip install --no-cache-dir -r requirements.txt
```

---

## 18. Aviso común de pip: hay una nueva versión disponible

Puede aparecer algo como:

```powershell
A new release of pip is available
```

No impide ejecutar el proyecto.

Si quieres actualizar `pip`, ejecuta:

```powershell
python -m pip install --upgrade pip
```

---

## 19. Error común: `No module named playwright`

Puede aparecer este error al intentar instalar Chromium:

```powershell
No module named playwright
```

Esto significa que Playwright no quedó instalado dentro del entorno virtual.

### Solución

Con el entorno virtual activo `(.venv)`, ejecuta:

```powershell
python -m pip install playwright python-dotenv
```

Luego instala Chromium:

```powershell
python -m playwright install chromium
```

---

## 20. Instalar Chromium de Playwright

Después de instalar las librerías, ejecuta:

```powershell
python -m playwright install chromium
```

Este comando instala el navegador que usará el bot para abrir ICEBERG.

---

## 21. Validar que Playwright quedó instalado

Puedes validar con:

```powershell
python -m pip show playwright
```

Si aparece información como nombre, versión y ubicación, quedó instalado correctamente.

También puedes validar `python-dotenv`:

```powershell
python -m pip show python-dotenv
```

---

## 22. Ejecutar el bot

Con el entorno virtual activo, ejecuta:

```powershell
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

Si `python` no funciona, prueba:

```powershell
py 1_Descargar.py
```

---

## 23. Qué debe pasar al ejecutar el bot

El programa debe mostrar mensajes similares a estos:

```bash
[*] Carpeta de descarga creada: ./descargas_iceberg/iceberg_2026_06_20_08_30
[08:30:01.123] 🤖 Iniciando Bot de Descarga Iceberg
[08:30:01.124] 📂 Carpeta de descarga: ./descargas_iceberg/iceberg_2026_06_20_08_30
[08:30:02.500] 🚀 Lanzando navegador...
[08:30:05.200] 🔐 Iniciando sesión en Iceberg...
[08:30:08.700] ✅ Login completado.
[08:30:09.100] --- Procesando tarea: Ocupacion_Docentes ---
[08:30:09.500]    > PERIODO : 26T03 | intento 1/3
[08:30:15.900]      Generando reporte...
[08:30:25.300]      Esperando enlace Excel...
[08:30:30.800]      Descargando Excel...
[08:30:31.400]      🎉 Archivo guardado: Ocupacion_Docentes_26T03_083031.xls
[08:30:32.000] 🏁 Proceso de descarga finalizado.
```

---

## 24. Dónde quedan los archivos descargados

Los archivos quedan dentro de:

```bash
descargas_iceberg/
```

Cada ejecución crea una carpeta nueva con fecha y hora:

```bash
descargas_iceberg/
└── iceberg_2026_06_20_08_30/
    ├── Ocupacion_Docentes_26T03_083031.xls
    ├── Ocupacion_Docentes_26P03_083155.xls
    ├── Ocupacion_Docentes_26V03_083220.xls
    └── Log_Iceberg_2026_06_20_08_30.log
```

---

## 25. Cómo configurar los periodos

Los periodos están en `config.py`, en esta parte:

```python
PERIODOS_BASE = [
    "26T03", "26P03", "26V03", "26V02", "26T02", "26P02",
    "2026B", "26ET2", "26ES2", "26ES3", "2026Q",
    "26I02", "26I03", "26PI2", "26PI3"
]
```

Para cambiar los periodos:

1. Abre `config.py`.
2. Busca `PERIODOS_BASE`.
3. Agrega o elimina periodos.
4. Guarda el archivo.
5. Ejecuta de nuevo el bot.

Ejemplo:

```python
PERIODOS_BASE = [
    "26V03",
    "26T03",
    "26P03"
]
```

---

## 26. Cómo cambiar el reporte a descargar

En `config.py`, el reporte activo se configura en:

```python
REPORTES_A_DESCARGAR = [
    {
        **REPORTES_DISPONIBLES["ocupacion_docente"],
        "periodos": PERIODOS_BASE
    }
]
```

Para descargar otro reporte, cambia la clave:

```python
REPORTES_DISPONIBLES["ocupacion_docente"]
```

Por ejemplo, para descargar matriculados:

```python
REPORTES_A_DESCARGAR = [
    {
        **REPORTES_DISPONIBLES["matriculados_grupo_periodo"],
        "periodos": PERIODOS_BASE
    }
]
```

---

## 27. Cómo descargar varios reportes

Puedes dejar varios reportes dentro de `REPORTES_A_DESCARGAR`:

```python
REPORTES_A_DESCARGAR = [
    {
        **REPORTES_DISPONIBLES["ocupacion_docente"],
        "periodos": PERIODOS_BASE
    },
    {
        **REPORTES_DISPONIBLES["matriculados_grupo_periodo"],
        "periodos": PERIODOS_BASE
    }
]
```

---

## 28. Mostrar el navegador mientras el bot trabaja

En `config.py` existe esta variable:

```python
MOSTRAR_NAVEGADOR = False
```

Si está en `False`, el bot trabaja en segundo plano.

Si quieres ver lo que hace el bot, cambia a:

```python
MOSTRAR_NAVEGADOR = True
```

Esto sirve para revisar errores de login, reportes, botones o periodos.

---

## 29. Comandos completos para instalar desde cero en Windows

Ejecuta estos comandos en PowerShell, dentro de la carpeta del proyecto:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

Si aparece `No module named playwright`, ejecuta:

```powershell
python -m pip install playwright python-dotenv
python -m playwright install chromium
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

---

## 30. Comandos completos para instalar desde cero en Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 1_Descargar.py
python3 2_Consolidar.py
python3 3_Filtrar.py
```

---


## 31. Consolidar los archivos descargados

Después de ejecutar:

```powershell
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

el proyecto descarga los archivos de ICEBERG dentro de la carpeta:

```bash
descargas_iceberg/
```

Luego se puede ejecutar el segundo archivo:

```powershell
python 2_Consolidar.py
```

Este archivo toma los reportes descargados y genera un consolidado final en Excel.

---

## 32. ¿Qué hace `2_Consolidar.py`?

El archivo `2_Consolidar.py` se encarga de:

1. Buscar la carpeta de descarga configurada.
2. Si no encuentra esa carpeta, buscar la carpeta más reciente dentro de `descargas_iceberg`.
3. Buscar archivos descargados con extensiones como:

```bash
.xls
.txt
.csv
.ods
.xlsx
```

4. Ignorar archivos que no deben procesarse, como:

```bash
Consolidado_Final
Log_
~$
```

5. Leer archivos de ICEBERG que parecen Excel, pero realmente pueden venir como texto plano separado por tabulaciones.
6. Limpiar comillas dobles en nombres de columnas y datos.
7. Corregir columnas de identificación para quitar valores terminados en `.0`.
8. Unir todos los archivos válidos en un solo consolidado.
9. Crear un archivo final en Excel y una copia en CSV.

---

## 33. Archivos que genera la consolidación

Al ejecutar:

```powershell
python 2_Consolidar.py
```

se generan archivos como:

```bash
Consolidado_Final_OcupacionDocente.xlsx
Consolidado_Final_OcupacionDocente.csv
```

Estos archivos quedan en la misma carpeta donde están los reportes descargados.

Ejemplo:

```bash
descargas_iceberg/
└── iceberg_2026_06_20_08_30/
    ├── Ocupacion_Docentes_26T03_083031.xls
    ├── Ocupacion_Docentes_26P03_083155.xls
    ├── Ocupacion_Docentes_26V03_083220.xls
    ├── Consolidado_Final_OcupacionDocente.xlsx
    └── Consolidado_Final_OcupacionDocente.csv
```

---

## 34. Flujo recomendado de uso

El flujo normal del proyecto es:

### Paso 1: activar el entorno virtual

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
```

### Paso 2: descargar los reportes desde ICEBERG

```powershell
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

### Paso 3: consolidar los reportes descargados

```powershell
python 2_Consolidar.py
```

---

## 35. Ejecutar descarga, consolidación y filtrado en un solo bloque

Si ya tienes todo instalado y configurado, puedes ejecutar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

---

## 36. Resultado esperado de la consolidación

Al ejecutar correctamente el consolidador, deberías ver mensajes similares a estos:

```bash
============================================================
🔄 CONSOLIDADOR DE REPORTES ICEBERG
============================================================

[08:45:10] ℹ️ INICIANDO CONSOLIDACIÓN (TEXTO PLANO -> EXCEL)
[08:45:10] ℹ️ Carpeta objetivo: ./descargas_iceberg/iceberg_2026_06_20_08_30
[08:45:11] ℹ️ Encontrados 3 archivo(s) para procesar
[08:45:11] ℹ️ Procesando: Ocupacion_Docentes_26T03_083031.xls
[08:45:12] ✅ ✓ Procesado (1500 registros)
[08:45:13] ℹ️ Limpiando formatos de IDs (.0)...
[08:45:15] ✅ CONSOLIDACIÓN COMPLETADA
[08:45:15] ℹ️ Archivo: Consolidado_Final_OcupacionDocente.xlsx
[08:45:15] ℹ️ Total de filas: 4500
```

---

## 37. Error común: falta instalar `pandas`, `openpyxl` u `odfpy`

Si aparece un error como:

```bash
ModuleNotFoundError: No module named 'pandas'
```

o:

```bash
ModuleNotFoundError: No module named 'openpyxl'
```

significa que faltan librerías para consolidar.

Solución:

```powershell
python -m pip install pandas openpyxl odfpy
```

O instalar todo nuevamente desde `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

---

## 38. Error común: no se encontraron carpetas de descarga

Si aparece:

```bash
No se encontraron carpetas de descarga
Ejecuta primero 1_Descargar.py
```

significa que todavía no hay reportes descargados.

Solución:

```powershell
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

---

## 39. Error común: no hay archivos para consolidar

Si aparece:

```bash
No hay archivos para consolidar en la carpeta
```

puede significar que:

- La descarga no generó archivos.
- Se está revisando una carpeta incorrecta.
- Los archivos fueron movidos o eliminados.
- Solo hay logs o archivos temporales.

Solución recomendada:

1. Abre la carpeta `descargas_iceberg`.
2. Entra a la carpeta más reciente.
3. Verifica que existan archivos `.xls`, `.csv`, `.txt`, `.ods` o `.xlsx`.
4. Ejecuta nuevamente:

```powershell
python 2_Consolidar.py
```

---

## 40. Nota sobre los archivos `.xls` de ICEBERG

Algunos archivos descargados desde ICEBERG pueden tener extensión `.xls`, pero internamente no siempre son un Excel real.

A veces son archivos de texto plano separados por tabulaciones.

Por eso `2_Consolidar.py` intenta leerlos como texto usando codificación `latin-1` y diferentes separadores.

Esto es normal en reportes de sistemas antiguos o reportes tipo legacy.

---

## 31. Cómo compartir este proyecto con otra persona

No se debe compartir toda la carpeta completa sin revisar, porque puede contener credenciales, descargas o archivos temporales.

### Archivos que sí se pueden compartir

```bash
1_Descargar.py
2_Consolidar.py
3_Filtrar.py
3_2_FiltrarTodasEscuelas.py
config.py
requirements.txt
README.md
.env.example
.gitignore
```

### Archivos que no se deben compartir

```bash
.env
.venv/
descargas_iceberg/
__pycache__/
*.log
*.png
*.xls
*.xlsx
```

El archivo más delicado es:

```bash
.env
```

Porque contiene usuario y contraseña.

---

## 32. Compartir el proyecto como ZIP en Windows usando clic derecho

Esta es la forma más sencilla para un usuario final.

### Paso 1: crear una carpeta limpia

1. Ve a la ubicación donde tienes el proyecto.
2. Haz clic derecho en un espacio en blanco.
3. Selecciona:

```bash
Nuevo > Carpeta
```

4. Coloca este nombre:

```bash
entrega_descarga_iceberg
```

### Paso 2: copiar solo los archivos permitidos

Copia estos archivos desde la carpeta original:

```bash
1_Descargar.py
2_Consolidar.py
3_Filtrar.py
3_2_FiltrarTodasEscuelas.py
config.py
requirements.txt
README.md
.env.example
.gitignore
```

Pégalos dentro de:

```bash
entrega_descarga_iceberg
```

### Paso 3: crear el ZIP

1. Haz clic derecho sobre la carpeta `entrega_descarga_iceberg`.
2. Selecciona:

```bash
Enviar a > Carpeta comprimida (en zip)
```

3. Windows generará un archivo `.zip`.

Ese archivo ZIP sí se puede compartir.

---

## 33. Compartir el proyecto como ZIP en Windows usando PowerShell

Ubícate una carpeta antes del proyecto. Ejemplo:

```powershell
cd C:\Users\ASUS\Documents\Github
```

Crear carpeta limpia:

```powershell
mkdir entrega_descarga_iceberg
```

Copiar archivos necesarios:

```powershell
Copy-Item .\descarga_iceberg\1_Descargar.py .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\2_Consolidar.py .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\3_Filtrar.py .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\3_2_FiltrarTodasEscuelas.py .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\config.py .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\requirements.txt .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\README.md .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\.env.example .\entrega_descarga_iceberg\
Copy-Item .\descarga_iceberg\.gitignore .\entrega_descarga_iceberg\
```

Crear ZIP:

```powershell
Compress-Archive -Path .\entrega_descarga_iceberg\* -DestinationPath .\descarga_iceberg_compartir.zip -Force
```

---

## 34. Compartir el proyecto como ZIP en Linux o macOS

Desde la carpeta del proyecto:

```bash
zip -r descarga_iceberg_compartir.zip . \
  -x ".env" \
  -x ".venv/*" \
  -x "descargas_iceberg/*" \
  -x "__pycache__/*" \
  -x "*.log" \
  -x "*.png" \
  -x "*.xls" \
  -x "*.xlsx"
```

---

## 35. Compartir el proyecto por GitHub o GitLab

Si se va a compartir por GitHub o GitLab, primero asegúrate de tener el archivo `.gitignore`.

Luego ejecuta:

```bash
git init
git add .
git status
```

Antes de continuar, revisa que no aparezca el archivo:

```bash
.env
```

Si `.env` aparece, no hagas commit. Revisa primero el `.gitignore`.

Si todo está bien:

```bash
git commit -m "Primera versión bot descarga Iceberg"
git branch -M main
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

---

## 36. Qué debe hacer la persona que recibe el proyecto

La persona que recibe el ZIP o clona el repositorio debe:

1. Descomprimir el ZIP o clonar el repositorio.
2. Abrir la carpeta en VSCode.
3. Leer el `README.md` en vista previa.
4. Crear su archivo `.env`.
5. Crear el entorno virtual.
6. Activar el entorno virtual.
7. Instalar dependencias.
8. Instalar Chromium de Playwright.
9. Ejecutar el bot.

### Comandos rápidos para Windows

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

---

## 37. Errores comunes y solución rápida

| Error o mensaje | Qué significa | Solución |
|---|---|---|
| `Activate.ps1 porque la ejecución de scripts está deshabilitada` | PowerShell bloquea scripts | Ejecutar `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `No module named playwright` | Playwright no está instalado en el entorno virtual | Ejecutar `python -m pip install playwright python-dotenv` |
| `No module named pandas` | Faltan librerías para consolidar | Ejecutar `python -m pip install pandas openpyxl odfpy` |
| `Cache entry deserialization failed` | Problema menor de caché de pip | Continuar o ejecutar `pip cache purge` |
| `No se encontraron las credenciales` | Falta el archivo `.env` o está mal escrito | Crear/revisar `.env` |
| No aparece el enlace Excel | ICEBERG está lento o no generó el reporte | Subir tiempos de espera o usar `MOSTRAR_NAVEGADOR = True` |
| Login falla | Usuario, contraseña o acceso incorrecto | Validar ingreso manual a ICEBERG |

---

## 38. Recomendaciones de seguridad

- No compartir el archivo `.env`.
- No subir `.env` a GitHub.
- No enviar `.env` por correo o WhatsApp.
- No compartir carpetas de descargas si contienen información sensible.
- Usar `.env.example` para indicar cómo debe configurarse el acceso.
- Revisar el ZIP antes de enviarlo.

---

## 39. Ejecución rápida después de instalado

Cuando el proyecto ya está instalado, en próximas ejecuciones solo debes hacer:

### Windows

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

### Linux o macOS

```bash
cd ruta/del/proyecto/descarga_iceberg
source .venv/bin/activate
python3 1_Descargar.py
python3 2_Consolidar.py
python3 3_Filtrar.py
```

---

## 40. Notas importantes

- El bot depende de la estructura actual de ICEBERG.
- Si ICEBERG cambia botones, nombres, URLs o estructura visual, puede ser necesario ajustar el código.
- El selector del periodo se realiza sobre el primer elemento tipo `combobox` encontrado en la página.
- El enlace de descarga se busca por el texto `Excel`.
- El botón de generación se busca por el texto `Ok`.
- Cada periodo tiene reintentos automáticos.
- Los archivos descargados se nombran con el formato:

```bash
NombreReporte_Periodo_HHMMSS.xls
```

Ejemplo:

```bash
Ocupacion_Docentes_26V03_184512.xls
```

---


---


---

## Filtrado final con `3_Filtrar.py`

Después de descargar y consolidar los reportes, se puede ejecutar el tercer archivo del proyecto:

```powershell
python 3_Filtrar.py
```

Este archivo toma el consolidado generado por `2_Consolidar.py` y aplica filtros para obtener una base final más específica.

---

## ¿Qué hace `3_Filtrar.py`?

El archivo `3_Filtrar.py` realiza este proceso:

1. Busca la carpeta de descargas configurada en `config.py`.
2. Si no encuentra esa carpeta, busca la carpeta más reciente dentro de `descargas_iceberg`.
3. Busca un archivo consolidado que empiece por `Consolidado_Final`.
4. Lee el archivo consolidado `.xlsx`.
5. Aplica los filtros configurados en la parte superior del archivo.
6. Muestra estadísticas del filtrado.
7. Limpia columnas de identificación para quitar valores terminados en `.0`.
8. Genera un archivo filtrado en Excel.
9. Genera también una copia en CSV.

---

## Flujo completo recomendado

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
```

| Paso | Archivo | Función |
|---|---|---|
| 1 | `1_Descargar.py` | Descarga reportes desde ICEBERG. |
| 2 | `2_Consolidar.py` | Une los archivos descargados en un consolidado. |
| 3 | `3_Filtrar.py` | Filtra el consolidado según reglas configuradas. |

---

## Configuración principal del filtro

Los filtros principales están al inicio de `3_Filtrar.py`:

```python
VALOR_FECHA_FILTRO = "30/03/2026"
VALORES_FECHAS_MULTIPLES = None
DEPENDENCIA_OBJETIVO = "INGENIERIA DE SISTEMAS"
```

---

## Cómo cambiar la fecha del filtro

Abre el archivo:

```bash
3_Filtrar.py
```

Busca esta línea:

```python
VALOR_FECHA_FILTRO = "30/03/2026"
```

Cambia la fecha por la que necesites.

Ejemplo:

```python
VALOR_FECHA_FILTRO = "06/04/2026"
```

El formato esperado es:

```bash
DD/MM/YYYY
```

---

## Cómo filtrar por varias fechas

Si necesitas filtrar por varias fechas, busca esta línea:

```python
VALORES_FECHAS_MULTIPLES = None
```

Y cámbiala por una lista:

```python
VALORES_FECHAS_MULTIPLES = ["30/03/2026", "06/04/2026", "13/04/2026"]
```

Para volver a una sola fecha:

```python
VALORES_FECHAS_MULTIPLES = None
```

---

## Cómo cambiar la dependencia filtrada

El filtro de dependencia está en esta línea:

```python
DEPENDENCIA_OBJETIVO = "INGENIERIA DE SISTEMAS"
```

Ejemplo:

```python
DEPENDENCIA_OBJETIVO = "INGENIERIA INDUSTRIAL"
```

El texto debe coincidir con el valor que viene en el consolidado.

---

## Materias excluidas

El archivo excluye algunas materias específicas:

```python
MATERIAS_EXCLUIDAS = [
    "TRABAJO DE INVESTIGACION EN INGENIERIA",
    "PLAN DE NEGOCIO APLICADO PARA ESCUELA DE INGENIERIA",
    "COMPRENSION Y PRODUCCION DE TEXTOS"
]
```

Para excluir otra materia, agrégala dentro de la lista:

```python
MATERIAS_EXCLUIDAS = [
    "TRABAJO DE INVESTIGACION EN INGENIERIA",
    "PLAN DE NEGOCIO APLICADO PARA ESCUELA DE INGENIERIA",
    "COMPRENSION Y PRODUCCION DE TEXTOS",
    "NOMBRE DE OTRA MATERIA"
]
```

---

## Excluir materias por palabra clave

Actualmente está configurado así:

```python
PATRON_EXCLUIR = "PRACTICA"
```

Esto excluye materias que contengan la palabra `PRACTICA`.

Ejemplos:

```bash
PRACTICA PROFESIONAL
PRACTICA EMPRESARIAL
PRACTICA APLICADA
```

Si no quieres excluir por esta palabra:

```python
PATRON_EXCLUIR = ""
```

---

## Condiciones que aplica el filtro

| Condición | Descripción |
|---|---|
| Dependencia | Solo conserva registros de la dependencia configurada. |
| Materia no contiene `PRACTICA` | Excluye materias con la palabra definida en `PATRON_EXCLUIR`. |
| Materias excluidas | Excluye materias específicas definidas en `MATERIAS_EXCLUIDAS`. |
| Capacidad diferente de 0 | Excluye grupos sin capacidad. |
| Inscritos diferente de 0 | Excluye grupos sin inscritos. |
| Fecha de inicio | Conserva solo registros con la fecha configurada. |

---

## Columnas usadas por el filtro

| Filtro | Columna esperada | Posición usada en Python |
|---|---|---|
| Materia | Columna G | `df.iloc[:, 6]` |
| Capacidad | Columna M | `df.iloc[:, 12]` |
| Inscritos | Columna N | `df.iloc[:, 13]` |
| Fecha inicio grupo | Columna U | `df.iloc[:, 20]` |
| Dependencia | Columna AO | `df.iloc[:, 40]` |

> Importante: si el reporte de ICEBERG cambia el orden de columnas, puede ser necesario ajustar estas posiciones en `3_Filtrar.py`.

---

## Archivos que genera el filtrado

Al ejecutar:

```powershell
python 3_Filtrar.py
```

se generan archivos con nombres similares a:

```bash
Filtrado_Ingenieria_20260620_084512.xlsx
Filtrado_Ingenieria_20260620_084512.csv
```

Estos archivos quedan dentro de la misma carpeta donde está el consolidado.

---

## Error común: no se encontró archivo consolidado

Si aparece:

```bash
No se encontró archivo consolidado en la carpeta
Ejecuta primero 2_Consolidar.py
```

Solución:

```powershell
python 2_Consolidar.py
python 3_Filtrar.py
```

---

## Error común: el filtro no arrojó resultados

Si aparece:

```bash
El filtro no arrojó resultados (0 filas)
```

puede significar que:

- La fecha configurada no existe en el consolidado.
- La dependencia no coincide exactamente.
- Las materias fueron excluidas por las reglas.
- Capacidad o inscritos están en 0.
- Cambió el orden de columnas del reporte.

Solución recomendada:

1. Abre `Consolidado_Final_OcupacionDocente.xlsx`.
2. Revisa la columna de fecha de inicio.
3. Copia exactamente una fecha existente.
4. Pégala en `VALOR_FECHA_FILTRO`.
5. Ejecuta de nuevo `python 3_Filtrar.py`.

---

## Nota importante sobre el filtro

El archivo `3_Filtrar.py` está preparado principalmente para el consolidado de ocupación docente.

Si se usa con otro reporte de ICEBERG, puede que las columnas no coincidan.

En ese caso, se deben revisar y ajustar las posiciones usadas en los filtros.

---



---

## Filtro alternativo para todas las escuelas con `3_2_FiltrarTodasEscuelas.py`

Además del filtro específico de Ingeniería, el proyecto puede incluir un filtro alternativo:

```bash
3_2_FiltrarTodasEscuelas.py
```

Este archivo sirve para filtrar el consolidado sin limitarlo a una sola dependencia o escuela.

Es útil cuando se necesita obtener información general de varias escuelas, conservando condiciones como fecha, capacidad, inscritos y exclusión de materias tipo práctica.

---

## Diferencia entre `3_Filtrar.py` y `3_2_FiltrarTodasEscuelas.py`

| Archivo | Uso principal |
|---|---|
| `3_Filtrar.py` | Filtra una dependencia específica, por ejemplo `INGENIERIA DE SISTEMAS`. |
| `3_2_FiltrarTodasEscuelas.py` | Filtra todas las escuelas, sin aplicar una dependencia específica. |

En otras palabras:

- Usa `3_Filtrar.py` cuando necesitas una sola dependencia.
- Usa `3_2_FiltrarTodasEscuelas.py` cuando necesitas revisar todas las escuelas.

---

## Flujo recomendado usando filtro de todas las escuelas

Primero se descargan los reportes:

![1_Descargar](assets/img/1_Descargar.png)

```powershell
python 1_Descargar.py
```

Luego se consolidan:

![2_Consolidar](assets/img/2_Consolidar.png)

```powershell
python 2_Consolidar.py
```

Filtrar la escuala de Ingeniería de Sistemas:

```powershell
python 3_Filtrar.py
```

Finalmente se ejecuta el filtro para todas las escuelas:

```powershell
python 3_2_FiltrarTodasEscuelas.py
```

También puedes ejecutarlo en bloque:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
python 1_Descargar.py
python 2_Consolidar.py
python 3_Filtrar.py
python 3_2_FiltrarTodasEscuelas.py
```

---

## Configuración principal de `3_2_FiltrarTodasEscuelas.py`

Al inicio del archivo se encuentra la configuración principal:

```python
VALOR_FECHA_FILTRO = "02/02/2026"
VALORES_FECHAS_MULTIPLES = None
PATRON_EXCLUIR = "PRACTICA"
```

---

## Cómo cambiar la fecha del filtro de todas las escuelas

Abre el archivo:

```bash
3_2_FiltrarTodasEscuelas.py
```

Busca esta línea:

```python
VALOR_FECHA_FILTRO = "02/02/2026"
```

Cámbiala por la fecha que necesites.

Ejemplo:

```python
VALOR_FECHA_FILTRO = "09/02/2026"
```

El formato debe ser:

```bash
DD/MM/YYYY
```

---

## Cómo filtrar varias fechas en todas las escuelas

Busca esta línea:

```python
VALORES_FECHAS_MULTIPLES = None
```

Para filtrar varias fechas, cambia `None` por una lista:

```python
VALORES_FECHAS_MULTIPLES = ["02/02/2026", "09/02/2026", "16/02/2026"]
```

Si quieres volver a filtrar una sola fecha, deja:

```python
VALORES_FECHAS_MULTIPLES = None
```

---

## Qué condiciones aplica `3_2_FiltrarTodasEscuelas.py`

Este filtro aplica las siguientes condiciones:

| Condición | Descripción |
|---|---|
| Materia no contiene `PRACTICA` | Excluye materias que contengan la palabra configurada en `PATRON_EXCLUIR`. |
| Capacidad diferente de 0 | Excluye grupos sin capacidad. |
| Inscritos diferente de 0 | Excluye grupos sin inscritos. |
| Fecha de inicio | Conserva solo registros con la fecha o fechas configuradas. |

A diferencia de `3_Filtrar.py`, este archivo no aplica filtro por dependencia.

---

## Ajuste importante recomendado en `3_2_FiltrarTodasEscuelas.py`

En la versión revisada aparece esta línea:

```python
condicion_materias = False
```

Y luego esa condición se usa dentro de:

```python
condicion_final = (
    condicion_practica &
    condicion_materias &
    condicion_capacidad &
    condicion_inscritos &
    condicion_fecha
)
```

Esto puede hacer que el resultado siempre sea de **0 filas**, porque `False` dentro de un `AND` hace que toda la condición final sea falsa.

## Archivos que genera `3_2_FiltrarTodasEscuelas.py`

Al ejecutar:

```powershell
python 3_2_FiltrarTodasEscuelas.py
```

se generan archivos con nombres similares a:

```bash
Filtrado_TodasLasEscuelas_20260620_091500.xlsx
Filtrado_TodasLasEscuelas_20260620_091500.csv
```

Estos archivos quedan en la misma carpeta donde está el consolidado.

Ejemplo:

```bash
descargas_iceberg/
└── iceberg_2026_06_20_08_30/
    ├── Consolidado_Final_OcupacionDocente.xlsx
    ├── Filtrado_Ingenieria_20260620_084512.xlsx
    └── Filtrado_TodasLasEscuelas_20260620_091500.xlsx
```

---

## Error común: el filtro de todas las escuelas devuelve 0 filas

Si `3_2_FiltrarTodasEscuelas.py` devuelve 0 filas, revisar:

1. Que la fecha configurada exista en el consolidado.
2. Que capacidad e inscritos no estén en 0.
3. Que el patrón `PRACTICA` no esté excluyendo más registros de lo esperado.
4. Que la línea `condicion_materias` esté en `True`.

Debe quedar así:

```python
condicion_materias = True
```

---

## Columnas usadas por `3_2_FiltrarTodasEscuelas.py`

| Filtro | Columna esperada | Posición usada en Python |
|---|---|---|
| Materia | Columna G | `df.iloc[:, 6]` |
| Capacidad | Columna M | `df.iloc[:, 12]` |
| Inscritos | Columna N | `df.iloc[:, 13]` |
| Fecha inicio grupo | Columna U | `df.iloc[:, 20]` |

> Importante: si ICEBERG cambia el orden de columnas, puede ser necesario ajustar estas posiciones en el código.

---

## 42. Cómo actualizar el proyecto en GitHub

Actualizar GitHub significa subir los cambios realizados en el computador al repositorio en línea.

Por ejemplo, si modificaste:

- `README.md`
- `config.py`
- `1_Descargar.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`

Puedes subir esos cambios a GitHub usando Git.

> Importante: antes de subir cambios, siempre revisa que no se vaya a subir el archivo `.env`, porque contiene usuario y contraseña.

---

### 42.1 Abrir la carpeta del proyecto

Primero debes estar ubicado en la carpeta del proyecto.

Ejemplo en Windows:

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
```

Si estás usando VSCode:

1. Abre Visual Studio Code.
2. Ve a:

```bash
File > Open Folder
```

3. Selecciona la carpeta:

```bash
descarga_iceberg
```

4. Abre una terminal desde:

```bash
Terminal > New Terminal
```

---

### 42.2 Revisar qué archivos cambiaron

Ejecuta:

```powershell
git status
```

Este comando muestra los archivos modificados, nuevos o eliminados.

Ejemplo de salida:

```bash
modified:   README.md
modified:   config.py
```

Antes de continuar, revisa que no aparezca:

```bash
.env
```

Si `.env` aparece, no subas los cambios todavía.

---

### 42.3 Agregar los archivos al commit

Para agregar todos los cambios:

```powershell
git add .
```

También puedes agregar archivos específicos:

```powershell
git add README.md
git add config.py
git add 1_Descargar.py
```

Para este proyecto, normalmente se pueden subir estos archivos:

```bash
1_Descargar.py
2_Consolidar.py
3_Filtrar.py
3_2_FiltrarTodasEscuelas.py
config.py
requirements.txt
README.md
.env.example
.gitignore
```

---

### 42.4 Crear un commit

Un commit es como guardar una versión del proyecto con una descripción.

Ejecuta:

```powershell
git commit -m "Actualización del proyecto"
```

Ejemplos de mensajes de commit:

```powershell
git commit -m "Se actualiza README para usuario final"
```

```powershell
git commit -m "Se ajustan periodos de descarga"
```

```powershell
git commit -m "Se agregan instrucciones de instalación"
```

```powershell
git commit -m "Se actualiza configuración de reportes"
```

---

### 42.5 Traer cambios recientes desde GitHub

Antes de subir tus cambios, es recomendable traer primero los cambios que puedan existir en GitHub.

Ejecuta:

```powershell
git pull origin main
```

Si tu rama se llama `master`, usa:

```powershell
git pull origin master
```

---

### 42.6 Subir los cambios a GitHub

Después de hacer el commit y traer los cambios recientes, ejecuta:

```powershell
git push origin main
```

Si tu rama se llama `master`, usa:

```powershell
git push origin master
```

---

### 42.7 Flujo completo recomendado

Este es el flujo normal para actualizar GitHub:

```powershell
git status
git add .
git commit -m "Descripción del cambio"
git pull origin main
git push origin main
```

Ejemplo real:

```powershell
git status
git add .
git commit -m "Se actualiza documentación del bot Iceberg"
git pull origin main
git push origin main
```

---

## 43. Si es la primera vez que se sube el proyecto a GitHub

Si el proyecto todavía no está conectado con GitHub, se debe hacer una configuración inicial.

### 43.1 Crear el repositorio en GitHub

1. Entra a GitHub.
2. Crea un nuevo repositorio.
3. Coloca un nombre, por ejemplo:

```bash
descarga_iceberg
```

4. Copia la URL del repositorio.

Ejemplo:

```bash
https://github.com/usuario/descarga_iceberg.git
```

---

### 43.2 Inicializar Git en la carpeta del proyecto

Desde la carpeta del proyecto, ejecuta:

```powershell
git init
```

---

### 43.3 Agregar archivos

```powershell
git add .
```

Antes de continuar, revisa:

```powershell
git status
```

Verifica que no aparezca:

```bash
.env
```

---

### 43.4 Crear el primer commit

```powershell
git commit -m "Primera versión del bot descarga Iceberg"
```

---

### 43.5 Definir la rama principal

```powershell
git branch -M main
```

---

### 43.6 Conectar con GitHub

Reemplaza `URL_DEL_REPOSITORIO` por la URL real del repositorio.

```powershell
git remote add origin URL_DEL_REPOSITORIO
```

Ejemplo:

```powershell
git remote add origin https://github.com/usuario/descarga_iceberg.git
```

---

### 43.7 Subir el proyecto por primera vez

```powershell
git push -u origin main
```

---

## 44. Cómo actualizar GitHub desde Visual Studio Code

También puedes actualizar GitHub desde la interfaz visual de VSCode.

### Pasos

1. Abre el proyecto en VSCode.
2. En el menú lateral izquierdo, haz clic en el ícono de **Source Control**.
3. Revisa la lista de archivos modificados.
4. Verifica que no aparezca el archivo:

```bash
.env
```

5. Escribe un mensaje de commit, por ejemplo:

```bash
Se actualiza README
```

6. Haz clic en **Commit**.
7. Luego haz clic en **Sync Changes** o **Push**.

> Aunque VSCode permite hacerlo visualmente, se recomienda revisar primero con `git status` en la terminal para confirmar que no se suban archivos sensibles.

---

## 45. Qué hacer si aparece `.env` en Git

El archivo `.env` no debe subirse a GitHub.

Si al ejecutar:

```powershell
git status
```

aparece:

```bash
.env
```

primero revisa que `.gitignore` tenga esta línea:

```gitignore
.env
```

Si `.env` ya fue agregado por error, ejecuta:

```powershell
git rm --cached .env
```

Luego revisa nuevamente:

```powershell
git status
```

Si ya no aparece `.env`, puedes continuar con el commit.

---

## 46. Archivos recomendados para subir a GitHub

Estos archivos sí pueden subirse:

```bash
1_Descargar.py
2_Consolidar.py
3_Filtrar.py
3_2_FiltrarTodasEscuelas.py
config.py
requirements.txt
README.md
.env.example
.gitignore
```

---

## 47. Archivos que no deben subirse a GitHub

Estos archivos o carpetas no deben subirse:

```bash
.env
.venv/
descargas_iceberg/
__pycache__/
*.log
*.png
*.xls
*.xlsx
```

Motivos:

| Archivo o carpeta | Motivo |
|---|---|
| `.env` | Contiene usuario y contraseña. |
| `.venv/` | Es el entorno virtual local. Puede pesar mucho y se reconstruye con `requirements.txt`. |
| `descargas_iceberg/` | Contiene archivos descargados desde ICEBERG. |
| `__pycache__/` | Archivos temporales de Python. |
| `*.log` | Archivos de registro de ejecución. |
| `*.png` | Capturas de error. |
| `*.xls` y `*.xlsx` | Reportes descargados. |

---

## 48. Comandos rápidos de Git

### Ver estado del proyecto

```powershell
git status
```

### Agregar cambios

```powershell
git add .
```

### Crear commit

```powershell
git commit -m "Mensaje del cambio"
```

### Traer cambios de GitHub

```powershell
git pull origin main
```

### Subir cambios a GitHub

```powershell
git push origin main
```

### Ver repositorio remoto configurado

```powershell
git remote -v
```

### Ver la rama actual

```powershell
git branch
```

---

## 49. Recomendación final antes de subir a GitHub

Antes de ejecutar `git push`, revisa siempre:

```powershell
git status
```

Y confirma que no se esté subiendo:

```bash
.env
```

El archivo `.env.example` sí se puede subir, porque solo contiene una plantilla sin credenciales reales.

## 50. Autor / responsable

Equipo Lite Escuela de Ingenieria de Sistemas.