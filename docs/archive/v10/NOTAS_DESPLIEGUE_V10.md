# Notas de despliegue - ICEBERG v10

## Decisión actual

La app ya fue validada en:

- Local Windows.
- GitHub Codespaces.
- Docker local.

## Interpretación

Docker se probó para validar portabilidad, no porque sea obligatorio tener un servidor físico.

Docker permite que la app corra en un entorno controlado y puede desplegarse en:

- Computador local.
- Máquina virtual.
- VPS.
- Servidor institucional.
- Servicio cloud compatible con contenedores.

## Recomendación de uso

| Uso | Opción recomendada |
|---|---|
| Trabajo personal | Local Windows |
| Compartir pruebas | Codespaces |
| Versión más estable | Docker |
| Publicación simple por URL | Evaluar Streamlit Cloud |

## Siguiente paso sugerido

Antes de publicar de forma más amplia:

1. Probar con un segundo usuario.
2. Confirmar que el ZIP descargado contiene los resultados esperados.
3. Confirmar que las credenciales no se almacenan.
4. Decidir si el despliegue final será Codespaces, Docker o Streamlit Cloud.
